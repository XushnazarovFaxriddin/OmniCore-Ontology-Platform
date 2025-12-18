"""
OmniCore Ontology Platform v10
AI-Orchestrated Ontological Computing System
"""

import sys
from pathlib import Path

# Ensure local "src" directory is importable when running as `python -m src.*`
_SRC_DIR = Path(__file__).resolve().parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

__version__ = "10.0.0"
__author__ = "OmniCore Team"
