---
name: revvel-template-library
description: Access and search the comprehensive Revvel Template Library with 500+ legal, academic, business, government, and FOSS templates. Use this skill to find and retrieve document templates for any purpose.
---

# Revvel Template Library Skill

## Overview

The Revvel Template Library provides access to over 527 professionally curated templates across 6 major categories and 75 subcategories. This skill enables you to search, browse, and retrieve templates for legal documents, academic papers, business plans, government forms, and open source projects.

## When to Use This Skill

Use this skill when the user needs:
- Legal document templates (contracts, NDAs, leases, trusts, court filings, etc.)
- Academic templates (research papers, thesis, grant proposals, white papers)
- Business documents (business plans, invoices, proposals, marketing plans)
- Government forms and applications (IRS, USPTO, FOIA requests, etc.)
- Open source project templates (README, contributing guidelines, security policies)
- Any professional document template

## Database Location

The template catalog is stored in a SQLite database at:
```
/home/ubuntu/revvel-template-library/catalog/templates.db
```

## Database Schema

### templates table
- `id` - Unique template identifier
- `name` - Template name
- `category` - Main category (Legal, Business, Academic & Research, etc.)
- `subcategory` - Specific subcategory
- `source` - Original source of the template
- `source_url` - URL to the source
- `download_url` - Direct download link (if available)
- `format` - File format (MD, DOCX, PDF, LaTeX, etc.)
- `description` - Detailed description
- `is_free` - Whether the template is free (1) or paid (0)
- `tags` - Comma-separated keywords
- `file_path` - Local file path (if downloaded)
- `has_file` - Whether local file exists
- `created_at` - Creation timestamp
- `popularity` - Usage/popularity score
- `author` - Template author
- `seo_keywords` - SEO-optimized keywords

### categories table
- `id` - Category identifier
- `name` - Category name
- `parent_id` - Parent category (for hierarchy)
- `description` - Category description
- `icon` - Emoji icon

### sources table
- `id` - Source identifier
- `name` - Source name
- `url` - Source website
- `description` - Source description
- `is_free` - Whether source is free

## Usage Examples

### Search for Templates

```python
import sqlite3

conn = sqlite3.connect('/home/ubuntu/revvel-template-library/catalog/templates.db')
c = conn.cursor()

# Search by keyword
c.execute("""
    SELECT id, name, category, description 
    FROM templates 
    WHERE name LIKE ? OR description LIKE ? OR tags LIKE ?
    LIMIT 10
""", ('%NDA%', '%NDA%', '%NDA%'))

for row in c.fetchall():
    print(f"{row[0]}: {row[1]} ({row[2]})")
    print(f"  {row[3]}\n")

conn.close()
```

### List Templates by Category

```python
import sqlite3

conn = sqlite3.connect('/home/ubuntu/revvel-template-library/catalog/templates.db')
c = conn.cursor()

# Get all legal templates
c.execute("""
    SELECT id, name, subcategory, format 
    FROM templates 
    WHERE category = 'Legal' AND is_free = 1
    ORDER BY name
    LIMIT 20
""")

for row in c.fetchall():
    print(f"{row[0]}: {row[1]} ({row[2]}) - {row[3]}")

conn.close()
```

### Get Template Details

```python
import sqlite3

conn = sqlite3.connect('/home/ubuntu/revvel-template-library/catalog/templates.db')
c = conn.cursor()

template_id = "abc123"
c.execute("SELECT * FROM templates WHERE id = ?", (template_id,))
template = c.fetchone()

if template:
    print(f"Name: {template[1]}")
    print(f"Category: {template[2]}")
    print(f"Description: {template[8]}")
    print(f"Source: {template[4]}")
    print(f"Format: {template[7]}")

conn.close()
```

### Full-Text Search (FTS5)

```python
import sqlite3

conn = sqlite3.connect('/home/ubuntu/revvel-template-library/catalog/templates.db')
c = conn.cursor()

# Full-text search using FTS5 index
c.execute("""
    SELECT t.id, t.name, t.category, t.description
    FROM templates t
    JOIN templates_fts fts ON t.name = fts.name
    WHERE templates_fts MATCH ?
    LIMIT 10
""", ("contract employment",))

for row in c.fetchall():
    print(f"{row[1]} ({row[2]})")
    print(f"  {row[3]}\n")

conn.close()
```

## CLI Tool

A command-line interface is available at:
```
/home/ubuntu/revvel-template-library/cli/revvel-templates
```

Usage:
```bash
# List templates
revvel-templates list --category Legal --free

# Search templates
revvel-templates search "business plan"

# Show template details
revvel-templates show <template-id>

# List categories
revvel-templates categories

# Show statistics
revvel-templates stats
```

## API Server

A FastAPI web application is available at:
```
/home/ubuntu/revvel-template-library/app/main.py
```

Start the server:
```bash
cd /home/ubuntu/revvel-template-library/app
python3 main.py
```

API endpoints:
- `GET /` - Landing page
- `GET /api/templates` - List templates (with filters)
- `GET /api/templates/{id}` - Get template details
- `GET /api/search?q={query}` - Full-text search
- `GET /api/categories` - List categories
- `GET /api/sources` - List sources
- `GET /api/stats` - Library statistics
- `GET /docs` - Interactive API documentation

## Template Categories

### Legal (193 templates)
- Contracts & Agreements
- Real Estate
- Wills & Estate Planning
- Family Law
- Business Formation
- Court Filings
- Intellectual Property
- Employment Law
- Trusts
- Compliance

### Business (94 templates)
- Business Plans
- Financial Documents
- Marketing
- Human Resources
- Operations
- Sales & Proposals
- Invoicing & Billing

### FOSS & Developer (68 templates)
- GitHub Templates
- Documentation
- DevOps & Infrastructure
- Security
- Project Management

### Academic & Research (61 templates)
- Research Papers
- Thesis & Dissertation
- Grant Proposals
- White Papers
- Academic Posters
- Academic CV
- LaTeX Templates

### Government & Regulatory (56 templates)
- Tax & IRS
- Business Registration
- Patents & Trademarks
- FOIA & Public Records
- Government Contracts
- Government Grants
- Regulatory Compliance

### Personal & Finance (20 templates)
- Personal Finance
- Life Events
- Career
- Correspondence

## Best Practices

1. **Always search first** - Use full-text search or keyword filtering to find relevant templates
2. **Check is_free flag** - Prioritize free templates unless user specifically needs paid resources
3. **Provide context** - When presenting templates, include category, format, and description
4. **Suggest alternatives** - If exact match not found, suggest similar templates from the same category
5. **Legal disclaimer** - Always remind users to consult qualified professionals for legal, financial, or regulatory documents

## Integration with Workflows

When a user requests a document template:

1. **Identify the need** - Determine what type of document they need
2. **Search the library** - Query the database using relevant keywords
3. **Present options** - Show 3-5 most relevant templates with descriptions
4. **Provide details** - When user selects a template, show full details including source and format
5. **Guide usage** - Explain how to use/customize the template
6. **Add disclaimer** - Include appropriate professional consultation disclaimer

## Maintenance

The catalog can be rebuilt or updated using:
```bash
python3 /home/ubuntu/revvel-template-library/scripts/build_catalog.py
```

This regenerates the database from the comprehensive template definitions and merges any new research data.

## Attribution

All templates are sourced from free and open sources. The library aggregates and organizes templates from:
- Government agencies (IRS, USPTO, SBA, etc.)
- Open source repositories (GitHub, etc.)
- Academic institutions
- Free legal form providers
- Original templates created by Walter-Evans

**Built by:** Walter-Evans  
**Repository:** https://github.com/MIDNGHTSAPPHIRE/revvel-template-library  
**License:** Templates retain their original licenses; catalog and tooling are open source
