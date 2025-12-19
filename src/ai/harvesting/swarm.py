"""
OmniCore Platform v10 - Ontology Harvesting Swarm
v10 Enhanced: AI Quality Filter for autonomous ontology discovery
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from common.config import get_settings
from common.logging_config import get_logger

logger = get_logger("ai.harvesting")


@dataclass
class OntologyCandidate:
    """Discovered ontology candidate"""
    name: str
    source: str
    url: str
    domain: str
    format: str
    estimated_size: int
    discovered_at: datetime
    quality_score: Optional[float] = None
    metadata: Dict[str, Any] = None


class OntologyHarvestingSwarm:
    """
    v10 Ontology Harvesting Swarm

    Sources (from v10 spec):
    - Academic: arXiv, PubMed, ACL Anthology
    - Web: DBpedia, Wikidata, Schema.org
    - Standards: BFO 2.0, DOLCE UltraLite, SUMO
    - Domain: SNOMED CT, GO, HP, LKIF, LegalRuleML, OntoCAPE, SSN/SOSA
    """

    SOURCES = {
        'academic': [
            {'name': 'arXiv', 'base_url': 'https://arxiv.org'},
            {'name': 'PubMed', 'base_url': 'https://pubmed.ncbi.nlm.nih.gov'},
            {'name': 'ACL Anthology', 'base_url': 'https://aclanthology.org'},
        ],
        'web': [
            {'name': 'DBpedia', 'base_url': 'https://dbpedia.org/ontology/', 'url': 'https://dbpedia.org/ontology/'},
            {'name': 'Wikidata', 'base_url': 'https://www.wikidata.org', 'url': 'https://www.wikidata.org/wiki/Special:EntityData/Q1.ttl'},
            {'name': 'Schema.org', 'base_url': 'https://schema.org', 'url': 'https://schema.org/version/latest/schemaorg-current-https.ttl'},
        ],
        'standards': [
            {'name': 'BFO 2.0', 'url': 'http://purl.obolibrary.org/obo/bfo.owl', 'format': 'xml'},
            {'name': 'DOLCE UltraLite', 'url': 'http://www.ontologydesignpatterns.org/ont/dul/DUL.owl', 'format': 'xml'},
            {'name': 'SUMO', 'url': 'https://raw.githubusercontent.com/ontologyportal/sumo/master/Merge.kif', 'format': 'kif'},
        ],
        'domain': {
            'biomed': [
                {'name': 'Gene Ontology', 'url': 'http://purl.obolibrary.org/obo/go.owl', 'format': 'xml'},
                {'name': 'Human Phenotype', 'url': 'http://purl.obolibrary.org/obo/hp.owl', 'format': 'xml'},
                {'name': 'Disease Ontology', 'url': 'http://purl.obolibrary.org/obo/doid.owl', 'format': 'xml'},
            ],
            'law': [
                {'name': 'LKIF Core', 'url': 'http://www.estrellaproject.org/lkif-core/lkif-core.owl', 'format': 'xml'},
            ],
            'engineering': [
                {'name': 'SSN/SOSA', 'url': 'http://www.w3.org/ns/ssn/', 'format': 'turtle'},
            ]
        }
    }

    def __init__(self):
        self.settings = get_settings()
        self._slm_service = None

    def _get_slm_service(self):
        """Lazy import SLM service"""
        if self._slm_service is None:
            from ai.slm.service import SLMService
            self._slm_service = SLMService()
        return self._slm_service

    async def discover_candidates(
        self,
        category: str = None,
        limit: int = 5
    ) -> List[OntologyCandidate]:
        """
        Discover ontology candidates from configured sources.

        Args:
            category: Optional category filter (academic, web, standards, domain)
            limit: Max candidates per source

        Returns:
            List of discovered candidates
        """
        candidates = []

        sources_to_check = {}
        if category:
            if category in self.SOURCES:
                sources_to_check[category] = self.SOURCES[category]
        else:
            sources_to_check = self.SOURCES

        for cat, sources in sources_to_check.items():
            if isinstance(sources, dict):
                # Domain sources have sub-categories
                for subcat, subsources in sources.items():
                    for source in subsources[:limit]:
                        candidate = self._create_candidate(source, f"{cat}/{subcat}")
                        if candidate:
                            candidates.append(candidate)
            else:
                for source in sources[:limit]:
                    candidate = self._create_candidate(source, cat)
                    if candidate:
                        candidates.append(candidate)

        logger.info(f"Discovered {len(candidates)} ontology candidates")
        return candidates

    def _create_candidate(
        self,
        source: Dict[str, Any],
        category: str
    ) -> Optional[OntologyCandidate]:
        """Create candidate from source config"""
        if 'url' not in source:
            return None

        return OntologyCandidate(
            name=source.get('name', 'Unknown'),
            source=category,
            url=source['url'],
            domain=category.split('/')[-1] if '/' in category else category,
            format=source.get('format', 'xml'),
            estimated_size=source.get('size', 0),
            discovered_at=datetime.utcnow(),
            metadata=source
        )

    async def harvest_batch(
        self,
        max_new: int = 20,
        quality_threshold: float = 0.7
    ) -> List[OntologyCandidate]:
        """
        v10 Enhanced: Harvest batch of ontologies with AI quality filter.

        Args:
            max_new: Maximum new ontologies to harvest
            quality_threshold: Minimum quality score (0.7 per v10 spec)

        Returns:
            List of approved candidates
        """
        # Discover candidates
        all_candidates = await self.discover_candidates(limit=5)

        # Score candidates with AI
        scored_candidates = await asyncio.gather(*[
            self._score_candidate(candidate) for candidate in all_candidates
        ])

        # Filter by quality threshold
        approved = [
            c for c, score in zip(all_candidates, scored_candidates)
            if score >= quality_threshold
        ]

        # Limit results
        approved = approved[:max_new]

        logger.info(f"Approved {len(approved)}/{len(all_candidates)} candidates (threshold: {quality_threshold})")
        return approved

    async def _score_candidate(self, candidate: OntologyCandidate) -> float:
        """Score candidate using AI quality assessment"""
        try:
            slm_service = self._get_slm_service()

            # Get sample data if possible
            sample_classes = []
            sample_properties = []

            # Use AI to assess quality
            assessment = await slm_service.assess_ontology_quality(
                name=candidate.name,
                source=candidate.url,
                domain=candidate.domain,
                triple_count=candidate.estimated_size,
                sample_classes=sample_classes,
                sample_properties=sample_properties
            )

            score = assessment.get('overall_score', 0.5)
            candidate.quality_score = score

            return score

        except Exception as e:
            logger.warning(f"Failed to score {candidate.name}: {e}")
            return 0.5  # Default score

    async def fetch_and_import(
        self,
        candidate: OntologyCandidate,
        use_slm: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch and import an ontology candidate.

        Returns import result.
        """
        from rdf.parser import OntologyImporter
        from common.models import OntologyImportRequest

        importer = OntologyImporter()

        request = OntologyImportRequest(
            source_url=candidate.url,
            format=candidate.format,
            use_slm=use_slm,
            conflict_resolution="auto"
        )

        result = await importer.import_ontology(request)

        return {
            "candidate": candidate.name,
            "success": result.success,
            "entities_created": result.entities_created,
            "triples_imported": result.triples_imported,
            "slm_enhancements": result.slm_enhancements,
            "errors": result.errors
        }

    def get_available_sources(self) -> Dict[str, Any]:
        """Get list of available ontology sources"""
        return self.SOURCES
