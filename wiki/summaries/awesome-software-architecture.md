---
title: "Awesome Software Architecture (mehdihadeli)"
type: summary
tags: [software-architecture, reference, curated-list, ddd, microservices, design-patterns, cqrs]
sources:
  - "raw/Awesome Software Architecture.md"
  - "raw/mehdihadeliawesome-software-architecture 📚 A curated list of awesome articles, videos, and other resources to learn and practice software architecture, patterns, and principles..md"
created: 2026-05-10
updated: 2026-05-10
---

# Awesome Software Architecture (mehdihadeli)

A community-maintained curated list hosted at [awesome-architecture.com](https://awesome-architecture.com) and the companion GitHub repo. Both source files are navigation indexes — link dumps with brief topic descriptions, not prose explanations. Useful as a topic taxonomy and reading list, not as a knowledge source.

## Assessment

Both raw files are the same repository viewed from two entry points:
- `Awesome Software Architecture.md` — stub intro with support/contribution boilerplate
- `mehdihadeliawesome-software-architecture...md` — full table-of-contents index with one-line topic descriptions

Most entries are marked `TODO...` (no description). The substantively described categories are DDD, Microservices, Architectural Design Principles, and modular monolith.

Content already covered by this wiki: [[systems/architectural-patterns]], [[patterns/principles]], [[patterns/design-patterns-behavioral]], [[patterns/design-patterns-creational]], [[patterns/design-patterns-structural]], [[systems/distributed-systems]], [[systems/scalability-reliability]], [[patterns/database]].

## Topic taxonomy

The list covers these major areas (useful as a gap-check):

**Architecture styles** — Clean Architecture, Onion, Hexagonal (Ports & Adapters), Vertical Slice, Event-Driven, SOA, Microservices, Modular Monolith, Actor Model (Akka.NET, Microsoft Orleans, ProtoActor)

**DDD** — Value Objects, Aggregates, Bounded Context, Domain Events, Integration Events, Domain/Application Services, Anemic vs Rich Domain Model, Tactical and Strategic Design Patterns, Domain Primitives

**Distributed systems patterns** — CQRS, Saga, Outbox/Inbox, Circuit Breaker, Bulkhead, BFF, Anti-Corruption Layer, Gateway Aggregation, Sidecar, Ambassador, Strangler Fig, Exactly-Once Delivery

**Messaging tools** — Kafka, RabbitMQ, NATS, ZeroMQ, Change Data Capture (CDC), MassTransit, NServiceBus, Wolverine, Dapr, CAP library

**Microservices operations** — API Gateway (Kong, Ambassador, Ocelot), Service Mesh (Istio, Linkerd), Service Discovery (Consul, Eureka), Observability (ELK/EFK/Loki, distributed tracing, correlation IDs), Resiliency (idempotency, high availability)

**Design principles** — SOLID, GRASP, DRY, KISS, YAGNI, CQS, Cohesion/Coupling, Fail Fast, Composition over Inheritance, Persistence Ignorance, Interface Segregation, IoC

**Anti-patterns** — Big Ball of Mud, God Object, Leaky Abstractions, Static Cling, Anemic Domain Model

**Cloud patterns** — 12-Factor App, cloud-native, PaaS/IaaS (Heroku, Netlify, OpenShift, Nomad, Terraform, Pulumi)

**DevOps tooling** — Docker, Kubernetes (Helm, ArgoCD, Flux, Kustomize, k3s, Kind), Nginx/Traefik ingress, Envoy, HAProxy

**Data** — NoSQL (MongoDB, CosmosDB), Relational (Postgres), Replication, Sharding, Caching

**Modeling** — Event Storming, Event Modeling, Domain Storytelling, ER Diagrams, Architecture Diagrams

## Notable gaps relative to this wiki

The list does not cover: AI/agent orchestration, LLM-specific patterns, testing pyramid in depth, frontend architecture. These are out of scope for the list's domain.

The list separately covers **Actor Model** as a first-class architecture style — not currently in [[systems/architectural-patterns]].

Actor Model is now documented at [[concepts/actor-model]] — 3 primitives, mailbox semantics, supervision trees, virtual actor model (Orleans), implementations table.
