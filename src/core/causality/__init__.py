"""
OmniCore Causality Service (Group B)

Manages the five causality types (Aristotelian + Emergent):
- EFFICIENT: causesDirectly (hammer -> nail_driving)
- FINAL: servesPurpose (nest -> offspring_protection)
- MATERIAL: constitutedBy (statue -> bronze)
- FORMAL: structuredAs (organism -> genome)
- EMERGENT: emergesFrom (consciousness -> neural_network_activity)
"""

from .store import CausalityStore
from .service import CausalityService

__all__ = ["CausalityStore", "CausalityService"]
