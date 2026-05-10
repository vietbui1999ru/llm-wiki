---
title: "AI and ML Engineering"
type: concept
tags: [ml-engineering, training-pipeline, model-serving, feature-store, experiment-tracking, fine-tuning, ai-agents]
sources: ["Machine-Learning-InterviewssrcMLSDml-system-design.md at main.md"]
created: 2026-05-06
updated: 2026-05-06
---

# AI and ML Engineering

Reference for designing production ML systems — covering the full pipeline from problem formulation through model serving, monitoring, and updates. Agent-specific patterns (multi-agent coordination, RAG, context engineering, skills) are extensively documented in `wiki/concepts/` and are linked here rather than duplicated.

---

## ML System Design: 9-Step Process

When designing an ML system (for production or for an interview), follow this structured flow. Steps are not strictly sequential — iterate as constraints sharpen.

| Step | Focus |
|---|---|
| 1. Problem formulation | Translate business goal to ML objective |
| 2. Metrics | Define offline and online success metrics before training |
| 3. Architecture (MVP) | High-level components — ML and non-ML |
| 4. Data collection | Sources, labeling strategy, storage |
| 5. Feature engineering | Representation, preprocessing, feature store |
| 6. Model development | Selection, training, offline evaluation |
| 7. Prediction service | Batch vs. real-time, edge, nearest neighbor |
| 8. Online testing | A/B experiments, shadow deployment, canary |
| 9. Scaling and monitoring | Drift detection, continual training, failure tolerance |

---

## Step 1: Problem Formulation

Before touching data or models:

- **What is the business goal?** Translate it to an ML objective (e.g., "increase engagement" → "maximize P(click | user, item)")
- **What is the ML category?** Binary classification, ranking, regression, generation, retrieval?
- **What are the inputs and outputs?** Define I/O precisely — this shapes the entire pipeline
- **Is ML actually needed?** A decision tree or heuristic may suffice; ML has real data and compute costs

---

## Step 2: Metrics — Define Before Training

Defining metrics after training is the most common ML engineering mistake. Metrics drive model selection, training objective, and deployment decisions.

### Offline metrics (evaluation without users)

| Task | Metrics |
|---|---|
| Classification | Precision, Recall, F1, ROC AUC, PR AUC, log-loss |
| Ranking | nDCG, MRR, MAP, Precision@k, Recall@k |
| Regression | MSE, MAE, RMSE |
| Generation (NLP) | BLEU, ROUGE, BLEURT |
| Retrieval | Recall@k, MRR |

Imbalanced classes: accuracy is misleading. Use PR AUC or F1. Consider class weights or resampling.

### Online metrics (with real users)

| Type | Examples |
|---|---|
| Engagement | CTR, like rate, comment rate, watch time |
| Conversion | Purchase rate, signup rate |
| Business | Revenue lift, retention |
| Counter metrics | Hide rate, report rate, unsubscribe rate (track alongside, not instead of) |

**Counter metrics matter**: a model that maximizes CTR by showing clickbait will show up in counter metrics before it shows up in CTR degradation.

---

## Step 3: Architecture — Separate ML and Non-ML Components

A production ML system is not just a model. Identify both layers:

**Non-ML components**: user-facing app, API gateway, databases, knowledge graphs, logging infrastructure

**ML components**: candidate generator, ranker, filter, re-ranker, feature server, model server, training pipeline

Multi-stage ML architectures are common for high-traffic systems:
1. **Candidate generation**: retrieve N candidates quickly (e.g., embedding-based ANN retrieval) — recall-oriented
2. **Ranker**: score all N candidates with a heavier model — precision-oriented
3. **Filter / business rules**: apply hard constraints (safety, eligibility, deduplication)

Separating these stages allows each to be scaled, updated, and A/B tested independently.

---

## Step 4: Data Collection and Preparation

### Label acquisition strategies

| Strategy | When to use | Tradeoff |
|---|---|---|
| **Natural labels** (clicks, purchases) | Engagement and recommendation systems | Implicit signal; not clicking ≠ negative |
| **Human annotation** | High-stakes tasks (medical, legal, safety) | Expensive, slow, privacy risks |
| **Programmatic labeling** | Large-scale, moderate precision acceptable | Noisy; useful for pre-training |
| **Weak supervision** | Heuristics, keyword rules, regex | Fast, noisy; combine with hand-labeled data |
| **Transfer learning + zero-shot** | Limited labeled data available | Quality depends on pre-trained model alignment |
| **Active learning** | Budget-constrained annotation | Annotate the examples the model is most uncertain about |

### Data splits — do these correctly

- **Split by time** for time-correlated data (e.g., user behavior). Splitting randomly leaks future information into training.
- **Scale/normalize after split**, using only training split statistics. Fitting scalers on the full dataset leaks test distribution into training.
- **Data leakage** is the most common source of overly optimistic offline metrics that fail to generalize.

### Class imbalance

| Approach | When |
|---|---|
| Resampling (oversample minority, undersample majority) | Moderate imbalance |
| Class weights in loss function | When you want to preserve original data distribution |
| Threshold tuning | After training; adjust the decision threshold to hit target precision/recall |
| Synthetic data (SMOTE) | Tabular data with moderate imbalance |

---

## Step 5: Feature Engineering

### Feature types and representation

| Data type | Representation |
|---|---|
| Categorical (low cardinality) | One-hot encoding |
| Categorical (high cardinality) | Embedding learned end-to-end, or pre-computed |
| Numerical | Scaling/normalization (StandardScaler, MinMax) — do this after split |
| Text | Tokenization → token IDs → embedding (BERT, learned) |
| Image | Resize + normalize → CNN features or ViT patches |
| User history | Sequence of embeddings; aggregate or use transformer over sequence |

### Feature stores

A feature store serves pre-computed features at both training time (offline) and serving time (online), ensuring **training-serving consistency** — the same feature values used during training are available at inference time.

**Without a feature store**: training uses batch-computed features; serving computes features differently → subtle distribution mismatch → degraded model performance in production.

**Components**: offline store (batch features, S3/data warehouse), online store (low-latency serving, Redis/DynamoDB), feature transformation layer, and a registry of feature definitions.

---

## Step 6: Model Development

### Model selection heuristic

Start simple. A heuristic → logistic regression → gradient boosted trees (GBDT) → neural network progression is correct. Each step adds complexity that must be justified by measured improvement.

| Model class | When to prefer |
|---|---|
| Logistic regression / linear | Interpretability required; fast to train, debug, and serve |
| GBDT (XGBoost, LightGBM) | Structured/tabular data; often beats NNs on tabular |
| Neural network | Unstructured data (image, text, audio); complex feature interactions |
| Transformer | Sequential, contextual tasks; large pre-trained models available |

### Training discipline

- **Loss function choice**: must match your metric. If you care about ranking, use a ranking loss — not cross-entropy
- **Offline vs online training**: offline (batch) is simpler; online (continual learning) keeps models fresh but is harder to validate
- **Hyperparameter tuning**: grid search for small spaces, random search for medium, Bayesian optimization for expensive models
- **Model calibration**: raw model scores are not probabilities unless calibrated (Platt scaling, isotonic regression)

---

## Step 7: Prediction Service — Batch vs Real-Time

| Mode | Latency | Throughput | When to use |
|---|---|---|---|
| **Batch** | Hours/minutes | High | Pre-compute for all users nightly; recommendations that don't need real-time freshness |
| **Real-time** | Milliseconds | Lower | Search ranking, ads, anything that depends on the current request context |
| **Hybrid** | — | — | Netflix pattern: batch for title carousels, real-time for row ordering within a carousel |

### On-device / edge inference

When network latency or privacy is a constraint, run inference on-device.

**Model compression techniques** to fit models on device:
- **Quantization**: reduce weight precision (float32 → int8) — typically 2–4× size reduction with small accuracy loss
- **Pruning**: remove low-magnitude weights — unstructured pruning is hard to accelerate; structured pruning is easier
- **Knowledge distillation**: train a small student model to mimic a larger teacher
- **Factorization**: decompose weight matrices into lower-rank approximations

---

## Step 8: Online Testing and Deployment

**A/B testing**: split traffic between control (existing model) and treatment (new model). Run until statistical significance on primary metric is achieved. Track counter metrics in parallel.

**Shadow deployment**: new model receives real traffic and generates predictions, but predictions are not served to users. Used to validate performance and catch failures before full deployment.

**Canary release**: deploy new model to a small fraction of traffic (1–5%). Ramp up as confidence grows. Rollback is fast if metrics degrade.

**Bandits**: multi-armed bandit algorithms (epsilon-greedy, UCB, Thompson sampling) for online A/B testing that allocate more traffic to the better variant as evidence accumulates. Useful when you need faster convergence than traditional A/B.

---

## Step 9: Scaling, Monitoring, and Continual Training

### Monitoring signals

| Signal | What it detects |
|---|---|
| **Data distribution shift** | Input features have changed (covariate shift) |
| **Label distribution shift** | Output distribution has changed (concept drift) |
| **Online metric degradation** | Model predictions are hurting the user experience |
| **System metrics** | Latency, throughput, error rate of the serving infrastructure |

**Covariate shift**: distribution of input X changes but P(Y|X) stays the same. Correct by retraining with recent data.

**Concept drift**: the relationship between X and Y changes (e.g., user behavior evolves). More serious; may require new features, not just retraining.

### Continual training

- **Train from scratch**: expensive; use when distribution has shifted dramatically
- **Fine-tune from base model**: cheaper; works when distribution shift is gradual
- **Auto-update triggers**: time-based (daily, weekly), performance-based (metric drops below threshold), or data-volume-based (N new labeled examples accumulated)

See [[systems/scalability-reliability]] for general infrastructure scaling patterns (load balancing, caching, sharding) that apply to ML serving infrastructure.

---

## AI Agent Engineering — Pointer to wiki/concepts/

Agent-specific patterns are documented extensively elsewhere. This section is a navigation guide, not a duplicate.

| Topic | Wiki location |
|---|---|
| Context engineering (JIT retrieval, compaction, note-taking) | [[concepts/context-engineering]] |
| RAG: contextual retrieval, BM25, reranking | [[concepts/contextual-retrieval]] |
| Agent harness (filesystem, bash, context mgmt, loops) | [[concepts/agent-harness]] |
| Multi-agent coordination (supervisor, worker, state) | [[concepts/agent-harness]], [[concepts/ralph-loop]] |
| Context failure modes (poisoning, distraction, confusion) | [[concepts/context-degradation]] |
| Skills, subagents, teams | [[concepts/agent-skills]], [[concepts/agent-subagents]], [[concepts/agent-teams]] |
| Verification pipeline | [[concepts/verification-pipeline]] |

---

## Cross-references

- [[concepts/context-engineering]] — curating high-signal context for LLM-based agents
- [[concepts/contextual-retrieval]] — RAG with contextual chunk prepending; 49–67% retrieval failure reduction
- [[concepts/agent-harness]] — model + harness = agent; the production deployment unit for AI agents
- [[systems/scalability-reliability]] — caching, load balancing, observability for ML serving infrastructure
- [[systems/data-modeling]] — feature stores, data access patterns, polyglot persistence for ML data
