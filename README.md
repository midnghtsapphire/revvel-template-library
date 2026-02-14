# Revvel Template Library

**The most comprehensive free template library for legal, academic, business, government, and open source documents.**

[![Templates](https://img.shields.io/badge/templates-527+-blue)](https://github.com/MIDNGHTSAPPHIRE/revvel-template-library)
[![Categories](https://img.shields.io/badge/categories-75+-green)](https://github.com/MIDNGHTSAPPHIRE/revvel-template-library)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

## Overview

Revvel Template Library is a comprehensive collection of over 527 professionally curated document templates spanning legal, academic, business, government, and open source categories. The library provides a searchable catalog, REST API, command-line interface, and integration capabilities for accessing templates programmatically.

## Features

- **527+ Templates** across 6 major categories and 75 subcategories
- **SQLite Database** with full-text search (FTS5) support
- **REST API** built with FastAPI for programmatic access
- **CLI Tool** for command-line template search and retrieval
- **Skill Module** for integration with automation systems
- **Free & Open** - prioritizes free and open source templates

## Categories

### ⚖️ Legal (193 templates)
Contracts, NDAs, leases, trusts, wills, court filings, employment agreements, intellectual property, and more.

### 💼 Business (94 templates)
Business plans, financial documents, invoices, proposals, marketing plans, HR forms, and operational templates.

### 💻 FOSS & Developer (68 templates)
GitHub templates, documentation, DevOps configs, security policies, and project management templates.

### 🎓 Academic & Research (61 templates)
Research papers (APA, MLA, IEEE), thesis templates, grant proposals, white papers, and academic CVs.

### 🏛️ Government & Regulatory (56 templates)
IRS forms, USPTO applications, FOIA requests, government contracts, compliance checklists, and regulatory filings.

### 👤 Personal & Finance (20 templates)
Personal budgets, resumes, cover letters, life event planning, and financial tracking.

## Quick Start

### Installation

```bash
git clone https://github.com/MIDNGHTSAPPHIRE/revvel-template-library.git
cd revvel-template-library
```

### Using the CLI

```bash
# List all templates
./cli/revvel-templates list

# Search for templates
./cli/revvel-templates search "NDA"

# Show template details
./cli/revvel-templates show <template-id>

# List categories
./cli/revvel-templates categories

# Show statistics
./cli/revvel-templates stats
```

### Starting the API Server

```bash
cd app
python3 -m pip install fastapi uvicorn
python3 main.py
```

Then visit http://localhost:8000 for the web interface or http://localhost:8000/docs for API documentation.

### Using the Python API

```python
import sqlite3

# Connect to the database
conn = sqlite3.connect('catalog/templates.db')
c = conn.cursor()

# Search for templates
c.execute("""
    SELECT id, name, category, description 
    FROM templates 
    WHERE name LIKE ? OR tags LIKE ?
    LIMIT 10
""", ('%contract%', '%contract%'))

for row in c.fetchall():
    print(f"{row[1]} ({row[2]})")
    print(f"  {row[3]}\n")

conn.close()
```

## API Endpoints

- `GET /` - Landing page with statistics and category browser
- `GET /api/templates` - List templates (supports filtering by category, subcategory, format, free status)
- `GET /api/templates/{id}` - Get specific template details
- `GET /api/search?q={query}` - Full-text search across all templates
- `GET /api/categories` - List all categories with descriptions
- `GET /api/sources` - List all template sources
- `GET /api/stats` - Library statistics and metrics
- `GET /docs` - Interactive Swagger UI documentation

## Database Schema

### templates
Primary table containing all template metadata:
- `id`, `name`, `category`, `subcategory`
- `source`, `source_url`, `download_url`
- `format`, `description`, `is_free`
- `tags`, `file_path`, `has_file`
- `created_at`, `popularity`, `author`, `seo_keywords`

### categories
Hierarchical category structure with icons and descriptions.

### sources
Template source providers with URLs and free/paid status.

### templates_fts
Full-text search index (FTS5) for fast keyword search.

## Template Sources

Templates are aggregated from:

- **Government Agencies**: IRS, USPTO, SBA, GSA, SEC, FDA, FCC
- **Academic Publishers**: IEEE, ACM, Springer, Elsevier, SSRN
- **Legal Resources**: LawDepot, eForms, Nolo, FindLaw
- **Open Source**: GitHub, CNCF, Linux Foundation, Apache Foundation
- **Business Resources**: SCORE, HubSpot, Microsoft Office, Google Docs
- **Original Templates**: Created by Walter-Evans for this library

## Use Cases

- **Legal Professionals**: Access contract templates, court filings, and legal forms
- **Researchers**: Find academic paper templates, grant proposals, and citation formats
- **Entrepreneurs**: Get business plan templates, financial projections, and pitch decks
- **Developers**: Use README templates, contributing guidelines, and security policies
- **Government Contractors**: Access capability statements, FOIA requests, and compliance forms
- **Automation Systems**: Integrate template search into workflows and applications

## Development

### Rebuilding the Catalog

```bash
python3 scripts/build_catalog.py
```

This regenerates the SQLite database from the comprehensive template definitions.

### Project Structure

```
revvel-template-library/
├── catalog/
│   ├── templates.db          # SQLite database
│   └── templates.json         # JSON export
├── templates/                 # Template files organized by category
│   ├── legal/
│   ├── academic/
│   ├── business/
│   ├── government/
│   └── foss/
├── app/
│   └── main.py               # FastAPI application
├── cli/
│   └── revvel-templates      # CLI tool
├── skill/
│   └── SKILL.md              # Skill module documentation
├── scripts/
│   └── build_catalog.py      # Catalog builder
└── README.md
```

## Contributing

Contributions are welcome! To add new templates:

1. Fork the repository
2. Add template metadata to `scripts/build_catalog.py`
3. Add template files to the appropriate `templates/` subdirectory
4. Rebuild the catalog: `python3 scripts/build_catalog.py`
5. Submit a pull request

## Disclaimer

This library aggregates and organizes templates from various free and open sources. Templates are provided for informational purposes only and do not constitute legal, financial, or professional advice. Always consult with qualified professionals before using legal, financial, or regulatory documents.

## License

The catalog, API, CLI, and tooling are released under the MIT License. Individual templates retain their original licenses from their respective sources.

## Attribution

**Built by:** Walter-Evans  
**Repository:** https://github.com/MIDNGHTSAPPHIRE/revvel-template-library  
**Templates provided by:** Free sources and APIs

---

*Revvel Template Library - Making professional document templates accessible to everyone.*
