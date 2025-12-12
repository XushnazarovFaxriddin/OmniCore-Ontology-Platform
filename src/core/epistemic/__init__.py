"""
OmniCore Epistemic Service (Group C)

Manages epistemic annotations with different basis types:
- AXIOMATIC: Self-evident truths
- EMPIRICAL: Evidence-based knowledge
- CONSENSUS: Community-agreed knowledge
- SPECULATIVE: Hypothetical or theoretical
"""

from .store import EpistemicStore
from .service import EpistemicService

__all__ = ["EpistemicStore", "EpistemicService"]
