[![Docling](https://github.com/docling-project/docling/raw/main/docs/assets/docling_processing.png)](https://github.com/docling-project/docling)

## Docling

[![DS4SD%2Fdocling | Trendshift](https://camo.githubusercontent.com/a35a9182b261bd58b124bfa2760bb23d6f29146c8a9aa00fbefa0e45885d4829/68747470733a2f2f7472656e6473686966742e696f2f6170692f62616467652f7265706f7369746f726965732f3132313332)](https://trendshift.io/repositories/12132)

Docling simplifies document processing, parsing diverse formats — including advanced PDF understanding — and providing seamless integrations with the gen AI ecosystem.

## Features

- 🗂️ Parsing of [multiple document formats](https://docling-project.github.io/docling/usage/supported_formats/) incl. PDF, DOCX, PPTX, XLSX, HTML, WAV, MP3, WebVTT, images (PNG, TIFF, JPEG,...), LaTeX, plain text, and more
- 📑 Advanced PDF understanding incl. page layout, reading order, table structure, code, formulas, image classification, and more
- 🧬 Unified, expressive [DoclingDocument](https://docling-project.github.io/docling/concepts/docling_document/) representation format
- ↪️ Various [export formats](https://docling-project.github.io/docling/usage/supported_formats/) and options, including Markdown, HTML, WebVTT, [DocTags](https://arxiv.org/abs/2503.11576) and lossless JSON
- 📜 Support of several application-specifc XML schemas incl. [USPTO](https://www.uspto.gov/patents) patents, [JATS](https://jats.nlm.nih.gov/) articles, and [XBRL](https://www.xbrl.org/) financial reports.
- 🔒 Local execution capabilities for sensitive data and air-gapped environments
- 🤖 Plug-and-play [integrations](https://docling-project.github.io/docling/integrations/) incl. LangChain, LlamaIndex, Crew AI & Haystack for agentic AI
- 🔍 Extensive OCR support for scanned PDFs and images
- 👓 Support of several Visual Language Models ([GraniteDocling](https://huggingface.co/ibm-granite/granite-docling-258M))
- 🎙️ Audio support with Automatic Speech Recognition (ASR) models
- 🔌 Connect to any agent using the [MCP server](https://docling-project.github.io/docling/usage/mcp/)
- 💻 Simple and convenient CLI

### What's new

- 📤 Structured [information extraction](https://docling-project.github.io/docling/examples/extraction/) \[🧪 beta\]
- 📑 New layout model (**Heron**) by default, for faster PDF parsing
- 🔌 [MCP server](https://docling-project.github.io/docling/usage/mcp/) for agentic applications
- 💼 Parsing of XBRL (eXtensible Business Reporting Language) documents for financial reports
- 💬 Parsing of WebVTT (Web Video Text Tracks) files and export to WebVTT format
- 💬 Parsing of LaTeX files
- 📝 Parsing of plain-text files (`.txt`, `.text`) and Markdown supersets (`.qmd`, `.Rmd`)
- 📝 Chart understanding (Barchart, Piechart, LinePlot): converting them into tables, code or adding detailed descriptions

### Coming soon

- 📝 Metadata extraction, including title, authors, references & language
- 📝 Complex chemistry understanding (Molecular structures)

## Installation

To use Docling, simply install `docling` from your package manager, e.g. pip:

```
pip install docling
```

> **Note:** Python 3.9 support was dropped in docling version 2.70.0. Please use Python 3.10 or higher.

Works on macOS, Linux and Windows environments. Both x86\_64 and arm64 architectures.

More [detailed installation instructions](https://docling-project.github.io/docling/installation/) are available in the docs.

## Getting started

To convert individual documents with python, use `convert()`, for example:

```
from docling.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869"  # document per local path or URL
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())  # output: "## Docling Technical Report[...]"
```

More [advanced usage options](https://docling-project.github.io/docling/usage/advanced_options/) are available in the docs.

## CLI

Docling has a built-in CLI to run conversions.

```
docling https://arxiv.org/pdf/2206.01062
```

You can also use 🥚 [GraniteDocling](https://huggingface.co/ibm-granite/granite-docling-258M) and other VLMs via Docling CLI:

```
docling --pipeline vlm --vlm-model granite_docling https://arxiv.org/pdf/2206.01062
```

This will use MLX acceleration on supported Apple Silicon hardware.

Read more [here](https://docling-project.github.io/docling/usage/)

## Documentation

Check out Docling's [documentation](https://docling-project.github.io/docling/), for details on installation, usage, concepts, recipes, extensions, and more.

## Examples

Go hands-on with our [examples](https://docling-project.github.io/docling/examples/), demonstrating how to address different application use cases with Docling.

## Integrations

To further accelerate your AI application development, check out Docling's native [integrations](https://docling-project.github.io/docling/integrations/) with popular frameworks and tools.

## Get help and support

Please feel free to connect with us using the [discussion section](https://github.com/docling-project/docling/discussions).

## Technical report

For more details on Docling's inner workings, check out the [Docling Technical Report](https://arxiv.org/abs/2408.09869).

## Contributing

Please read [Contributing to Docling](https://github.com/docling-project/docling/blob/main/CONTRIBUTING.md) for details.

## References

If you use Docling in your projects, please consider citing the following:

```
@techreport{Docling,
   = {Deep Search Team},
  month = {8},
  title = {Docling Technical Report},
  url = {https://arxiv.org/abs/2408.09869},
  eprint = {2408.09869},
  doi = {10.48550/arXiv.2408.09869},
  version = {1.0.0},
  year = {2024}
}
```

## License

The Docling codebase is under MIT license. For individual model usage, please refer to the model licenses found in the original packages.

## LF AI & Data

Docling is hosted as a project in the [LF AI & Data Foundation](https://lfaidata.foundation/projects/).

### IBM ❤️ Open Source AI

The project was started by the AI for knowledge team at IBM Research Zurich.