"""
OmniCore Roots Service (Group A)

Manages the four fundamental ontological root types:
- EXTANT: Entities with spatiotemporal location
- ABSTRACT: Atemporal, mind-independent structures
- MENTAL: Subjective, first-person accessible states
- FICTIVE: Context-dependent representations
"""

from .store import RootsStore
from .service import RootsService

__all__ = ["RootsStore", "RootsService"]
