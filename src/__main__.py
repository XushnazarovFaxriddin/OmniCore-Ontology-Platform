"""
OmniCore Platform v10 - Main Entry Point
Run with: python -m src or python -m omnicore
"""

import sys
import os

# Add src directory to path for proper imports
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from orchestrator.cli import main

if __name__ == "__main__":
    main()
