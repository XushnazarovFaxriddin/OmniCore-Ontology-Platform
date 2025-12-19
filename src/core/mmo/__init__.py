"""
OmniCore MMO Service (Group D)

Manages the Meta-Meta-Ontology (MMO):
- MMO Classes: Define structure and taxonomy
- MMO Slots: Define properties and relationships
- MMO Metrics: Evaluate ontology quality (completeness, coverage, coherence, utility, inclusivity)
"""

from .store import MMOStore
from .service import MMOService

__all__ = ["MMOStore", "MMOService"]
