"""
CareerOS A4 PDF Serving & Document Preview Test Suite
=====================================================
Verifies the Release 2.2 document endpoints (SPEC-0044 / SPEC-0045):
1. In-browser inline PDF rendering (/api/documents/download-pdf).
2. Rendered HTML resume view for canvas preview (/api/documents/view-html).
3. 404 handling on missing files.
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_pdf_serving_endpoint():
    """Verifies that download-pdf endpoint serves PDF files inline with application/pdf header."""
    # Check if any tailored PDF exists
    resumes_dir = Path("resumes/tailored")
    pdfs = list(resumes_dir.glob("*.pdf")) if resumes_dir.exists() else []

    if pdfs:
        test_pdf = pdfs[0]
        res = client.get(f"/api/documents/download-pdf?path={test_pdf.as_posix()}")
        assert res.status_code == 200
        assert "application/pdf" in res.headers["content-type"]
        assert "inline" in res.headers.get("content-disposition", "")
        assert len(res.content) > 1000

def test_pdf_serving_404():
    """Verifies 404 response on nonexistent PDF."""
    res = client.get("/api/documents/download-pdf?path=nonexistent_file_xyz.pdf")
    assert res.status_code == 404

def test_html_view_endpoint():
    """Verifies that view-html endpoint serves HTML resumes with text/html header."""
    resumes_dir = Path("resumes/tailored")
    htmls = list(resumes_dir.glob("*.html")) if resumes_dir.exists() else []

    if htmls:
        test_html = htmls[0]
        res = client.get(f"/api/documents/view-html?path={test_html.as_posix()}")
        assert res.status_code == 200
        assert "text/html" in res.headers["content-type"]
        assert len(res.content) > 500
