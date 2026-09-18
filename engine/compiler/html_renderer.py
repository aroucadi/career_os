"""
CareerOS Dynamic HTML Resume Renderer
======================================
Converts structured markdown resumes into high-density, ATS-safe,
pixel-perfect A4 HTML suitable for headless Edge/Chrome PDF compilation.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{candidate_name} — Tailored Resume ({target_job})</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        @page {
            size: A4;
            margin: 8mm 10mm 8mm 10mm;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            font-size: 8.5pt;
            line-height: 1.28;
            color: #1e293b;
            background-color: #ffffff;
            -webkit-print-color-adjust: exact;
        }

        .header {
            text-align: center;
            border-bottom: 1.5pt solid #0f172a;
            padding-bottom: 3px;
            margin-bottom: 6px;
        }

        .candidate-name {
            font-size: 17pt;
            font-weight: 700;
            letter-spacing: -0.3px;
            color: #0f172a;
            text-transform: uppercase;
            margin-bottom: 1px;
        }

        .candidate-title {
            font-size: 9.2pt;
            font-weight: 600;
            color: #2563eb;
            margin-bottom: 2px;
        }

        .contact-info {
            font-size: 8pt;
            color: #475569;
            font-weight: 400;
        }

        .contact-sep {
            margin: 0 4px;
            color: #cbd5e1;
        }

        .section {
            margin-bottom: 6.5px;
            page-break-inside: avoid;
        }

        .section-title {
            font-size: 8.8pt;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: #0f172a;
            border-bottom: 1pt solid #cbd5e1;
            padding-bottom: 1.5px;
            margin-bottom: 3.5px;
        }

        .summary-text {
            font-size: 8.4pt;
            color: #334155;
            text-align: justify;
            line-height: 1.30;
        }

        .competencies-list {
            list-style-type: none;
            padding-left: 0;
        }

        .competency-item {
            font-size: 8.2pt;
            color: #334155;
            margin-bottom: 2px;
            line-height: 1.25;
        }

        .competency-item strong {
            color: #0f172a;
            font-weight: 600;
        }

        .job-entry {
            margin-bottom: 5.5px;
            page-break-inside: avoid;
        }

        .job-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 1px;
        }

        .job-company {
            font-weight: 700;
            font-size: 8.9pt;
            color: #0f172a;
        }

        .job-location {
            font-size: 8.1pt;
            color: #64748b;
            font-weight: 400;
        }

        .job-sub {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 2.5px;
        }

        .job-title {
            font-weight: 600;
            font-size: 8.4pt;
            color: #2563eb;
        }

        .job-dates {
            font-size: 8pt;
            color: #64748b;
            font-style: italic;
        }

        .bullet-list {
            list-style-type: none;
            padding-left: 0;
        }

        .bullet-item {
            position: relative;
            padding-left: 11px;
            margin-bottom: 2px;
            font-size: 8.1pt;
            color: #334155;
            text-align: justify;
            line-height: 1.25;
        }

        .bullet-item::before {
            content: "•";
            position: absolute;
            left: 2px;
            color: #2563eb;
            font-weight: bold;
        }

        .bullet-item strong {
            color: #0f172a;
            font-weight: 600;
        }

        .job-env {
            font-size: 7.8pt;
            color: #64748b;
            margin-top: 2px;
            margin-bottom: 3px;
        }

        .job-env strong {
            color: #475569;
        }

        .cert-item {
            font-size: 8.1pt;
            color: #334155;
            margin-bottom: 1.5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="candidate-name">{candidate_name}</div>
        <div class="candidate-title">{headline}</div>
        <div class="contact-info">
            {contact_line}
        </div>
    </div>

    {sections_html}
</body>
</html>
"""

def render_markdown_resume_to_html(md_text: str, target_job: str = "Tailored Mandate") -> str:
    """Parses a structured Markdown resume and injects it into the standard A4 HTML template."""
    lines = md_text.splitlines()
    
    candidate_name = "Candidate Name"
    headline = "Strategic Professional"
    contact_line = ""
    sections = []
    
    current_section = None
    current_section_lines = []
    
    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()
        if not line:
            idx += 1
            continue
            
        if line.startswith("# ") and idx < 5:
            candidate_name = line.replace("# ", "").strip()
            idx += 1
            if idx < len(lines) and lines[idx].strip() and not lines[idx].strip().startswith("#"):
                headline = lines[idx].strip()
                idx += 1
            if idx < len(lines) and lines[idx].strip() and not lines[idx].strip().startswith("---") and not lines[idx].strip().startswith("#"):
                contact_line = lines[idx].strip().replace(" | ", ' <span class="contact-sep">•</span> ')
                idx += 1
            continue

        if line.startswith("## "):
            if current_section:
                sections.append((current_section, current_section_lines))
            current_section = line.replace("## ", "").strip()
            current_section_lines = []
            idx += 1
            continue
            
        if current_section:
            current_section_lines.append(line)
        idx += 1
        
    if current_section:
        sections.append((current_section, current_section_lines))
        
    sections_html = []
    for sec_title, sec_lines in sections:
        sec_html = _render_section(sec_title, sec_lines)
        if sec_html:
            sections_html.append(sec_html)
            
    all_sections = "\n".join(sections_html)
    
    html = HTML_TEMPLATE
    html = html.replace("{candidate_name}", candidate_name)
    html = html.replace("{headline}", headline)
    html = html.replace("{target_job}", target_job)
    html = html.replace("{contact_line}", contact_line)
    html = html.replace("{sections_html}", all_sections)
    return html

def _render_section(title: str, lines: List[str]) -> str:
    """Renders a specific markdown section to styled HTML."""
    out = [f'<div class="section">', f'<div class="section-title">{title}</div>']
    
    t_low = title.lower()
    if "summary" in t_low or "profil" in t_low:
        summary_text = " ".join([l.strip() for l in lines if not l.startswith("---") and not l.startswith("#")])
        out.append(f'<div class="summary-text">{summary_text}</div>')
        
    elif "competenc" in t_low or "value proposition" in t_low:
        out.append('<ul class="competencies-list">')
        for l in lines:
            if l.startswith("- ") or l.startswith("• "):
                item_text = l[2:].strip()
                # format strong
                item_text = re.sub(r"\*\*(.*?)\*\*", r"<strong></strong>", item_text)
                out.append(f'<li class="competency-item">• {item_text}</li>')
        out.append('</ul>')
        
    elif "experience" in t_low:
        # Parse job blocks
        job_blocks = _split_job_blocks(lines)
        for b in job_blocks:
            out.append(b)
            
    else:
        # Default list or paragraph
        for l in lines:
            if l.startswith("- ") or l.startswith("• "):
                it = re.sub(r"\*\*(.*?)\*\*", r"<strong></strong>", l[2:].strip())
                out.append(f'<div class="cert-item">• {it}</div>')
            elif not l.startswith("---"):
                it = re.sub(r"\*\*(.*?)\*\*", r"<strong></strong>", l.strip())
                out.append(f'<div class="summary-text">{it}</div>')
                
    out.append('</div>')
    return "\n".join(out)

def _split_job_blocks(lines: List[str]) -> List[str]:
    """Extracts job entries from lines under Work Experience."""
    blocks = []
    current_company = ""
    current_location = ""
    current_title = ""
    current_dates = ""
    bullets = []
    env_str = ""

    def flush_job():
        nonlocal current_company, current_location, current_title, current_dates, bullets, env_str
        if current_company or current_title:
            b_html = ['<div class="job-entry">']
            b_html.append('<div class="job-header">')
            b_html.append(f'<span class="job-company">{current_company}</span>')
            b_html.append(f'<span class="job-location">{current_location}</span>')
            b_html.append('</div>')
            
            b_html.append('<div class="job-sub">')
            b_html.append(f'<span class="job-title">{current_title}</span>')
            b_html.append(f'<span class="job-dates">{current_dates}</span>')
            b_html.append('</div>')
            
            if bullets:
                b_html.append('<ul class="bullet-list">')
                for bu in bullets:
                    bu_fmt = re.sub(r"\*\*(.*?)\*\*", r"<strong></strong>", bu)
                    b_html.append(f'<li class="bullet-item">{bu_fmt}</li>')
                b_html.append('</ul>')
                
            if env_str:
                b_html.append(f'<div class="job-env"><strong>Environment:</strong> {env_str}</div>')
                
            b_html.append('</div>')
            blocks.append("\n".join(b_html))
            
            current_title = ""
            current_dates = ""
            bullets = []
            env_str = ""

    for l in lines:
        l_str = l.strip()
        if not l_str or l_str.startswith("---"):
            continue

        if l_str.startswith("### "):
            flush_job()
            comp_loc = l_str.replace("### ", "").strip()
            parts = comp_loc.split("—")
            if len(parts) >= 2:
                current_company = parts[0].strip()
                current_location = parts[1].strip()
            else:
                current_company = comp_loc
                current_location = ""
            continue

        if "**" in l_str and ("–" in l_str or "-" in l_str) and "|" in l_str:
            flush_job()
            parts = l_str.split("|")
            current_title = parts[0].replace("**", "").strip()
            current_dates = parts[1].replace("**", "").strip() if len(parts) > 1 else ""
            continue

        if l_str.startswith("- ") or l_str.startswith("• "):
            bullets.append(l_str[2:].strip())
            continue

        if "environment:" in l_str.lower():
            env_str = re.sub(r"\*\*Environment:\*\*", "", l_str, flags=re.IGNORECASE).strip()
            continue

    flush_job()
    return blocks
