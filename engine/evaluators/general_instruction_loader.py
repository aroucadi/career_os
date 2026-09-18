"""Alias for rubric_loader to support legacy imports."""
import sys
from pathlib import Path

parent = Path(__file__).resolve().parent.parent
if str(parent) not in sys.path:
    sys.path.insert(0, str(parent))

from rubric_loader import get_injected_rubrics_prompt, load_file_content

__all__ = ["get_injected_rubrics_prompt", "load_file_content"]
