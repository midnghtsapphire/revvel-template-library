#!/usr/bin/env python3
"""
Revvel Template Library - FastAPI Application
Comprehensive template library system with search, browse, and download capabilities.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from pathlib import Path
from typing import List, Optional
import os

app = FastAPI(
    title="Revvel Template Library",
    description="Comprehensive template library with 500+ legal, academic, business, government, and FOSS templates",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "/home/ubuntu/revvel-template-library/catalog/templates.db"
TEMPLATES_DIR = "/home/ubuntu/revvel-template-library/templates"

def get_db():
    """Get database connection."""
    return sqlite3.connect(DB_PATH)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Landing page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Revvel Template Library</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                   max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            h1 { color: #2c3e50; }
            .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 60px; border-radius: 10px; margin-bottom: 30px; }
            .stats { display: flex; gap: 20px; margin: 30px 0; }
            .stat-card { background: white; padding: 20px; border-radius: 8px; flex: 1; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .stat-number { font-size: 36px; font-weight: bold; color: #667eea; }
            .stat-label { color: #666; margin-top: 5px; }
            .categories { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
            .category-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                            transition: transform 0.2s; cursor: pointer; }
            .category-card:hover { transform: translateY(-5px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
            .category-icon { font-size: 48px; margin-bottom: 10px; }
            .category-name { font-size: 20px; font-weight: bold; color: #2c3e50; }
            .category-count { color: #666; margin-top: 5px; }
            .api-docs { margin-top: 40px; padding: 20px; background: white; border-radius: 8px; }
            .endpoint { background: #f8f9fa; padding: 10px; margin: 10px 0; border-left: 4px solid #667eea; }
            a { color: #667eea; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .footer { margin-top: 60px; padding: 20px; text-align: center; color: #666; border-top: 1px solid #ddd; }
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>🚀 Revvel Template Library</h1>
            <p style="font-size: 20px; margin-top: 10px;">The most comprehensive free template library for legal, academic, business, government, and open source documents.</p>
            <p style="margin-top: 20px;">Built by Walter-Evans | Powered by free sources and APIs</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">527+</div>
                <div class="stat-label">Total Templates</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">75+</div>
                <div class="stat-label">Subcategories</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">56+</div>
                <div class="stat-label">Sources</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">100%</div>
                <div class="stat-label">Free & Open</div>
            </div>
        </div>
        
        <h2>📚 Browse by Category</h2>
        <div class="categories">
            <div class="category-card" onclick="location.href='/api/templates?category=Legal'">
                <div class="category-icon">⚖️</div>
                <div class="category-name">Legal</div>
                <div class="category-count">193 templates</div>
            </div>
            <div class="category-card" onclick="location.href='/api/templates?category=Business'">
                <div class="category-icon">💼</div>
                <div class="category-name">Business</div>
                <div class="category-count">94 templates</div>
            </div>
            <div class="category-card" onclick="location.href='/api/templates?category=FOSS%20%26%20Developer'">
                <div class="category-icon">💻</div>
                <div class="category-name">FOSS & Developer</div>
                <div class="category-count">68 templates</div>
            </div>
            <div class="category-card" onclick="location.href='/api/templates?category=Academic%20%26%20Research'">
                <div class="category-icon">🎓</div>
                <div class="category-name">Academic & Research</div>
                <div class="category-count">61 templates</div>
            </div>
            <div class="category-card" onclick="location.href='/api/templates?category=Government%20%26%20Regulatory'">
                <div class="category-icon">🏛️</div>
                <div class="category-name">Government & Regulatory</div>
                <div class="category-count">56 templates</div>
            </div>
            <div class="category-card" onclick="location.href='/api/templates?category=Personal%20%26%20Finance'">
                <div class="category-icon">👤</div>
                <div class="category-name">Personal & Finance</div>
                <div class="category-count">20 templates</div>
            </div>
        </div>
        
        <div class="api-docs">
            <h2>🔌 API Endpoints</h2>
            <div class="endpoint">
                <strong>GET /api/templates</strong> - List all templates (with optional filters)
                <br><small>Query params: category, subcategory, is_free, format, q (search)</small>
            </div>
            <div class="endpoint">
                <strong>GET /api/templates/{id}</strong> - Get specific template details
            </div>
            <div class="endpoint">
                <strong>GET /api/search?q={query}</strong> - Full-text search across templates
            </div>
            <div class="endpoint">
                <strong>GET /api/categories</strong> - List all categories
            </div>
            <div class="endpoint">
                <strong>GET /api/sources</strong> - List all template sources
            </div>
            <div class="endpoint">
                <strong>GET /docs</strong> - Interactive API documentation (Swagger UI)
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Revvel Template Library</strong> | Built by Walter-Evans</p>
            <p>Templates provided by free sources and APIs | <a href="https://github.com/MIDNGHTSAPPHIRE/revvel-template-library">GitHub Repository</a></p>
            <p style="font-size: 12px; margin-top: 10px;">This library aggregates templates from various free and open sources. Always consult with qualified professionals before using legal, financial, or regulatory documents.</p>
        </div>
    </body>
    </html>
    """

@app.get("/api/templates")
async def list_templates(
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    is_free: Optional[bool] = None,
    format: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = Query(100, le=500),
    offset: int = 0
):
    """List templates with optional filtering."""
    conn = get_db()
    c = conn.cursor()
    
    query = "SELECT * FROM templates WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    if subcategory:
        query += " AND subcategory = ?"
        params.append(subcategory)
    if is_free is not None:
        query += " AND is_free = ?"
        params.append(1 if is_free else 0)
    if format:
        query += " AND format LIKE ?"
        params.append(f"%{format}%")
    if q:
        query += " AND (name LIKE ? OR description LIKE ? OR tags LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
    
    query += f" LIMIT {limit} OFFSET {offset}"
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    columns = ["id", "name", "category", "subcategory", "source", "source_url", 
               "download_url", "format", "description", "is_free", "tags", 
               "file_path", "has_file", "created_at", "popularity", "author", "seo_keywords"]
    
    results = [dict(zip(columns, row)) for row in rows]
    return {"count": len(results), "templates": results}

@app.get("/api/templates/{template_id}")
async def get_template(template_id: str):
    """Get specific template details."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM templates WHERE id = ?", (template_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Template not found")
    
    columns = ["id", "name", "category", "subcategory", "source", "source_url", 
               "download_url", "format", "description", "is_free", "tags", 
               "file_path", "has_file", "created_at", "popularity", "author", "seo_keywords"]
    
    return dict(zip(columns, row))

@app.get("/api/search")
async def search_templates(q: str, limit: int = 50):
    """Full-text search using FTS5."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("""
        SELECT t.* FROM templates t
        JOIN templates_fts fts ON t.name = fts.name
        WHERE templates_fts MATCH ?
        LIMIT ?
    """, (q, limit))
    
    rows = c.fetchall()
    conn.close()
    
    columns = ["id", "name", "category", "subcategory", "source", "source_url", 
               "download_url", "format", "description", "is_free", "tags", 
               "file_path", "has_file", "created_at", "popularity", "author", "seo_keywords"]
    
    results = [dict(zip(columns, row)) for row in rows]
    return {"count": len(results), "results": results}

@app.get("/api/categories")
async def list_categories():
    """List all categories."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM categories")
    rows = c.fetchall()
    conn.close()
    
    columns = ["id", "name", "parent_id", "description", "icon"]
    return [dict(zip(columns, row)) for row in rows]

@app.get("/api/sources")
async def list_sources():
    """List all template sources."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM sources")
    rows = c.fetchall()
    conn.close()
    
    columns = ["id", "name", "url", "description", "is_free"]
    return [dict(zip(columns, row)) for row in rows]

@app.get("/api/stats")
async def get_stats():
    """Get library statistics."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM templates")
    total_templates = c.fetchone()[0]
    
    c.execute("SELECT COUNT(DISTINCT category) FROM templates")
    total_categories = c.fetchone()[0]
    
    c.execute("SELECT COUNT(DISTINCT subcategory) FROM templates")
    total_subcategories = c.fetchone()[0]
    
    c.execute("SELECT COUNT(DISTINCT source) FROM templates")
    total_sources = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM templates WHERE is_free = 1")
    free_templates = c.fetchone()[0]
    
    c.execute("SELECT category, COUNT(*) as count FROM templates GROUP BY category ORDER BY count DESC")
    by_category = [{"category": row[0], "count": row[1]} for row in c.fetchall()]
    
    conn.close()
    
    return {
        "total_templates": total_templates,
        "total_categories": total_categories,
        "total_subcategories": total_subcategories,
        "total_sources": total_sources,
        "free_templates": free_templates,
        "by_category": by_category
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
