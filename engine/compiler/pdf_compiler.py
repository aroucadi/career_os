"""
CareerOS PDF Resume Compiler
============================
Uses headless Microsoft Edge or Google Chrome to compile pixel-perfect,
ATS-compliant HTML resume templates into standard A4 PDF files.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

_ROOT_DIR = Path(__file__).resolve().parent.parent.parent

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

def find_browser_executable() -> Optional[str]:
    """Finds available Edge or Chrome headless executable."""
    for p in EDGE_PATHS:
        if os.path.exists(p):
            return p
    return None

def compile_html_to_pdf(html_file: Path, output_pdf: Path) -> bool:
    """Compiles an HTML resume template to PDF using headless browser."""
    browser_exe = find_browser_executable()
    if not browser_exe:
        print("[ERROR] Headless browser executable (Edge/Chrome) not found on system.")
        return False

    html_file = Path(html_file).resolve()
    output_pdf = Path(output_pdf).resolve()

    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    if output_pdf.exists():
        try:
            output_pdf.unlink()
        except Exception as e:
            print(f"[WARNING] Could not delete existing PDF {output_pdf}: {e}")

    file_url = f"file:///{str(html_file).replace('\\', '/')}"

    cmd = [
        browser_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={str(output_pdf)}",
        file_url,
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        if output_pdf.exists():
            print(f"✅ [SUCCESS] PDF successfully compiled: {output_pdf}")
            return True
        else:
            print(f"❌ [ERROR] PDF generation command ran but file was not created: {output_pdf}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ [ERROR] Browser failed to render PDF: {e.stderr.decode('utf-8', errors='ignore')}")
        return False

def compile_latest_resume(version: str = "v12") -> bool:
    """Compiles the specified resume version to PDF in root and resumes/."""
    template_name = f"resume_{version}_template.html"
    template_path = _ROOT_DIR / "resumes" / "templates" / template_name
    
    if not template_path.exists():
        # Fallback to root or engine template
        template_path = _ROOT_DIR / template_name
        if not template_path.exists():
            print(f"[ERROR] Template {template_name} not found in resumes/templates/ or root.")
            return False

    target_pdf_resumes = _ROOT_DIR / "resumes" / f"Alaa_Eddine_Roucadi_Resume_{version}.pdf"
    target_pdf_root = _ROOT_DIR / f"Alaa_Eddine_Roucadi_Resume_{version}.pdf"

    success = compile_html_to_pdf(template_path, target_pdf_resumes)
    if success:
        # Also copy to root for quick access
        try:
            import shutil
            shutil.copy2(target_pdf_resumes, target_pdf_root)
            print(f"✅ [SUCCESS] Synced to root: {target_pdf_root}")
        except Exception as e:
            print(f"[WARNING] Could not copy to root: {e}")

    return success

def compile_custom_resume(html_path: Path, output_pdf: Path) -> bool:
    """Compiles an arbitrary HTML resume file into a target PDF."""
    html_path = Path(html_path).resolve()
    output_pdf = Path(output_pdf).resolve()
    if not html_path.exists():
        print(f"[ERROR] HTML source file not found: {html_path}")
        return False
    return compile_html_to_pdf(html_path, output_pdf)

if __name__ == "__main__":
    version_arg = sys.argv[1] if len(sys.argv) > 1 else "v12"
    compile_latest_resume(version_arg)
