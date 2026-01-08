"""
OmniCore Platform v10 - Ontology Harvesting Swarm
v10 Enhanced: AI Quality Filter for autonomous ontology discovery
"""

import asyncio
import abc
import xml.etree.ElementTree as ET
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


class SourceHarvester(abc.ABC):
    """Abstract base class for ontology harvesting strategies."""
    
    @abc.abstractmethod
    async def harvest(self, limit: int = 5) -> List[OntologyCandidate]:
        """Harvest candidates from source."""
        pass


class StaticHarvester(SourceHarvester):
    """Harvests from predefined static sources."""

    SOURCES = {
        'academic': [
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

    async def harvest(self, limit: int = 5) -> List[OntologyCandidate]:
        candidates = []
        for cat, sources in self.SOURCES.items():
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
        return candidates

    def _create_candidate(self, source: Dict[str, Any], category: str) -> Optional[OntologyCandidate]:
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


class ArxivHarvester(SourceHarvester):
    """Harvests ontology-related papers/data from arXiv API."""
    
    BASE_URL = "http://export.arxiv.org/api/query"
    
    async def harvest(self, limit: int = 5) -> List[OntologyCandidate]:
        candidates = []
        import httpx
        
        params = {
            "search_query": "all:ontology AND all:web",
            "start": 0,
            "max_results": limit,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                
                # Parse Atom feed
                root = ET.fromstring(response.content)
                # Atom namespace
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                
                for entry in root.findall('atom:entry', ns):
                    title = entry.find('atom:title', ns).text.strip()
                    id_url = entry.find('atom:id', ns).text.strip()
                    summary = entry.find('atom:summary', ns).text.strip()
                    published = entry.find('atom:published', ns).text.strip()
                    
                    # Create candidate
                    candidates.append(OntologyCandidate(
                        name=f"arXiv: {title[:50]}...",
                        source="academic/arxiv",
                        url=id_url,
                        domain="academic",
                        format="pdf",  # Usually PDF but listing as potential source
                        estimated_size=0,
                        discovered_at=datetime.utcnow(),
                        metadata={
                            "summary": summary[:200],
                            "published": published,
                            "full_title": title
                        }
                    ))
                    
        except Exception as e:
            logger.warning(f"arXiv harvesting failed: {e}")
            
        return candidates


class OntologyHarvestingSwarm:
    """
    v10 Ontology Harvesting Swarm
    Orchestrates multiple harvesters.
    """

    def __init__(self):
        self.settings = get_settings()
        self._slm_service = None
        self.harvesters: List[SourceHarvester] = [
            StaticHarvester(),
            ArxivHarvester()
        ]

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
        Discover ontology candidates from all strategies.
        """
        tasks = [h.harvest(limit) for h in self.harvesters]
        results = await asyncio.gather(*tasks)
        
        all_candidates = []
        for res in results:
            all_candidates.extend(res)
            
        # Filter if category provided (simple string match)
        if category:
            all_candidates = [c for c in all_candidates if category in c.source]
            
        logger.info(f"Discovered {len(all_candidates)} candidates from {len(self.harvesters)} strategies")
        return all_candidates

    async def harvest_batch(
        self,
        max_new: int = 20,
        quality_threshold: float = 0.7
    ) -> List[OntologyCandidate]:
        """
        v10 Enhanced: Harvest batch of ontologies with AI quality filter.
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
        """Get list of available ontology sources (from static harvester)"""
        # Helper to return static list for compatibility
        return StaticHarvester.SOURCES

