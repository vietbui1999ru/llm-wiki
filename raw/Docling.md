### Docling converts messy documents into structured data and simplifies downstream document and AI processing by detecting tables, formulas, reading order, OCR, and much more.

##### [From Source to Structure: The LaTeX Backend Story](https://www.docling.ai/blog/20260315_00_the_latex_story/)

[All blog posts](https://www.docling.ai/blog/)

##### [Moving Beyond Sparse Grounding with Complete Screen Parsing Supervision](https://scholar.google.com/citations?view_op=view_citation&hl=en&user=sPuvIfgAAAAJ&cstart=20&pagesize=80&citation_for_view=sPuvIfgAAAAJ:9vf0nzSNQJEC)

[All papers](https://www.docling.ai/papers/)

**Install** Docling as a [Python library](https://pypi.org/project/docling) with your favorite package manager:

```
pip install docling
```

**Run** the CLI directly from your terminal:

```bash
docling https://arxiv.org/pdf/2206.01062
```

**Code** a document conversion as part of a Python application:

```python
from docling.document_converter import DocumentConverter
                        
                            source = "https://arxiv.org/pdf/2408.09869"
                            converter = DocumentConverter()
                            doc = converter.convert(source).document
                            print(doc.export_to_markdown())
```

**Deploy** it as [Docling Serve ![](https://www.docling.ai/img/serve.webp)](https://github.com/docling-project/docling-serve) 

**Enable** an agent via [Docling MCP ![](https://www.docling.ai/img/mcp.webp)](https://github.com/docling-project/docling-mcp) 

**Import** many document formats into a unified and structured [Docling Document](https://docling-project.github.io/docling/concepts/docling_document) , including scanned pages via an OCR engine of your choice.

**Export** a parsed document to formats that simplify processing and ingestion into AI, RAG, and agentic systems.

**Extract** document components and their properties from the Docling Document.

<table><thead><tr><th></th><th>Rich</th><th>Markup</th><th>Tabular</th><th>Image</th><th>Audio</th></tr></thead><tbody><tr><th rowspan="5">Import</th><td>PDF</td><td>Markdown</td><td>XLSX</td><td>PNG</td><td>MP3</td></tr><tr><td>DOCX</td><td>HTML</td><td>CSV</td><td>JPEG</td><td>WAV</td></tr><tr><td>PPTX</td><td>AsciiDoc</td><td></td><td>TIFF</td><td></td></tr><tr><td></td><td>WebVTT</td><td></td><td>BMP</td><td></td></tr><tr><td></td><td></td><td></td><td>WEBP</td><td></td></tr></tbody><tbody><tr><th rowspan="3">Export</th><td>JSON</td><td>Text</td><td></td><td></td><td></td></tr><tr><td>Doctags</td><td>Markdown</td><td></td><td></td><td></td></tr><tr><td></td><td>HTML</td><td></td><td></td><td></td></tr></tbody><tbody><tr><th rowspan="11">Extract</th><th rowspan="2">Page</th><th colspan="4">Component</th></tr><tr><th>Text</th><th>Table</th><th colspan="2">Picture</th></tr><tr><td>Image</td><td><a href="#text-header">Header</a></td><td><a href="#table-structure">Structure</a></td><td colspan="2"><a href="#picture-image">Image</a></td></tr><tr><td>Number</td><td><a href="#text-paragraph">Paragraph</a></td><td><a href="#table-cell">Cell</a></td><td colspan="2"><a href="#picture-class">Class</a></td></tr><tr><td><a href="#furniture">Header</a></td><td><a href="#seq-list">List item</a></td><td></td><td colspan="2"><a href="#picture-description">Description</a></td></tr><tr><td><a href="#furniture">Footer</a></td><td><a href="#seq-code">Code</a></td><td></td><td colspan="2"></td></tr><tr><td></td><td><a href="#formula">Formula</a></td><td colspan="3"><a href="#table-caption">Caption</a></td></tr><tr><td></td><td colspan="4"><a href="#order">Reading order</a></td></tr><tr><td></td><td colspan="4"><a href="#chunks">Chunks</a></td></tr><tr><td colspan="5"><a href="#layout">Bounding boxes</a></td></tr></tbody></table>

Docling partitions a document into bite-sized chunks of contiguous text, ready for ingestion by AI systems.

Docling stores and traverses components according to reading order.

Docling detects one or multiple bounding boxes per component, which can fragment and span different pages.

Docling detects and optionally excludes page headers and footers from exports.

Docling captures table structure, such as rows, columns, and (multi-level) headers. Docling is able to interpret complex table cell content, such as lists. Docling groups captions with their respective pictures and tables.

Docling extracts pictures as image data and stores it in the Docling Document or as external image files. Docling classifies pictures by their contents, assigning labels such as chart and diagram types. Docling enriches pictures with additional captions that describe their contents.

Docling detects mathematical formulas and converts them to LaTeX syntax.

Docling detects blocks of code and classifies their programming languages. Docling detects list items and groups them together.

Docling distinguishes section headers from subsequent paragraphs. Docling concatenates fragmented paragraphs, across one or multiple pages, into one text.