"""
OmniCore Global Ontology Service (Group E)

Aggregates data and health status from all other services:
- Global statistics across all ontology components
- Sample data from each service
- System-wide health monitoring
"""

from .service import GlobalService

__all__ = ["GlobalService"]
