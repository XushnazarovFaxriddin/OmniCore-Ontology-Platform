"""
OmniCore Platform v10 - RDF/OWL Parser
Lossless deterministic parsing with optional SLM enhancement
"""

import asyncio
import hashlib
import time
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path
import json

from common.config import get_settings
from common.logging_config import get_logger
from common.models import (
    ParsedEntity, RootType, OntologyImportRequest, OntologyImportResult,
    Provenance, Conflict, ConflictType, generate_operation_id, generate_version_string
)

logger = get_logger("rdf.parser")


class RDFParser:
    """
    v10 Deterministic RDF/OWL Parser using rdflib.

    Philosophy: "Start deterministic, augment intelligently"
    - All structured data (OWL/RDF) parsed losslessly
    - SLM never replaces — only enhances when natural-language context fills gaps
    """

    # Standard namespaces
    NAMESPACES = {
        "owl": "http://www.w3.org/2002/07/owl#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "dc": "http://purl.org/dc/elements/1.1/",
        "dcterms": "http://purl.org/dc/terms/",
        "foaf": "http://xmlns.com/foaf/0.1/",
        "obo": "http://purl.obolibrary.org/obo/",
        "bfo": "http://purl.obolibrary.org/obo/BFO_"
    }

    # Format mappings for rdflib
    FORMAT_MAP = {
        "xml": "xml",
        "turtle": "turtle",
        "ttl": "turtle",
        "n3": "n3",
        "nt": "nt",
        "ntriples": "nt",
        "json-ld": "json-ld",
        "jsonld": "json-ld"
    }

    def __init__(self):
        self.settings = get_settings()
        self._graph = None

    def _get_graph(self):
        """Lazy import rdflib and create graph"""
        try:
            from rdflib import Graph, Namespace, URIRef, Literal, BNode
            from rdflib.namespace import RDF, RDFS, OWL, XSD, SKOS, DC, DCTERMS

            self._rdf_imports = {
                "Graph": Graph,
                "Namespace": Namespace,
                "URIRef": URIRef,
                "Literal": Literal,
                "BNode": BNode,
                "RDF": RDF,
                "RDFS": RDFS,
                "OWL": OWL,
                "XSD": XSD,
                "SKOS": SKOS,
                "DC": DC,
                "DCTERMS": DCTERMS
            }
            return Graph()
        except ImportError:
            logger.error("rdflib not installed. Install with: pip install rdflib")
            raise ImportError("rdflib required for RDF parsing")

    def parse_content(
        self,
        content: str,
        format: str = "turtle",
        base_iri: str = None
    ) -> Tuple[Any, int]:
        """
        Parse RDF content string.

        Returns:
            Tuple of (graph, triple_count)
        """
        graph = self._get_graph()
        fmt = self.FORMAT_MAP.get(format.lower(), "turtle")

        try:
            graph.parse(data=content, format=fmt, publicID=base_iri)
            triple_count = len(graph)
            logger.info(f"Parsed {triple_count} triples in {fmt} format")
            return graph, triple_count
        except Exception as e:
            logger.error(f"Failed to parse RDF content: {e}")
            raise

    def parse_file(
        self,
        file_path: str,
        format: str = None
    ) -> Tuple[Any, int]:
        """
        Parse RDF file.

        Format is auto-detected from extension if not specified.
        """
        graph = self._get_graph()
        path = Path(file_path)

        if format is None:
            ext = path.suffix.lower().lstrip(".")
            format = ext if ext in self.FORMAT_MAP else "turtle"

        fmt = self.FORMAT_MAP.get(format.lower(), "turtle")

        try:
            graph.parse(str(path), format=fmt)
            triple_count = len(graph)
            logger.info(f"Parsed {triple_count} triples from {file_path}")
            return graph, triple_count
        except Exception as e:
            logger.error(f"Failed to parse RDF file {file_path}: {e}")
            raise

    async def parse_url(
        self,
        url: str,
        format: str = None
    ) -> Tuple[Any, int]:
        """
        Parse RDF from URL.
        """
        import httpx

        async with httpx.AsyncClient(timeout=self.settings.ontology_import_timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            content = response.text

        # Auto-detect format from content-type or URL
        if format is None:
            content_type = response.headers.get("content-type", "")
            if "turtle" in content_type or url.endswith(".ttl"):
                format = "turtle"
            elif "xml" in content_type or url.endswith(".owl") or url.endswith(".rdf"):
                format = "xml"
            elif "json" in content_type:
                format = "json-ld"
            else:
                format = "turtle"

        return self.parse_content(content, format, base_iri=url)

    def extract_entities(self, graph) -> List[ParsedEntity]:
        """
        Extract entities from parsed RDF graph.

        Extracts:
        - Classes (owl:Class, rdfs:Class)
        - Properties (owl:ObjectProperty, owl:DatatypeProperty, rdf:Property)
        - Individuals (owl:NamedIndividual, typed instances)
        """
        RDF = self._rdf_imports["RDF"]
        RDFS = self._rdf_imports["RDFS"]
        OWL = self._rdf_imports["OWL"]
        SKOS = self._rdf_imports["SKOS"]
        URIRef = self._rdf_imports["URIRef"]

        entities = []
        seen_iris = set()

        # Extract classes
        class_types = [OWL.Class, RDFS.Class]
        for class_type in class_types:
            for s in graph.subjects(RDF.type, class_type):
                if isinstance(s, URIRef) and str(s) not in seen_iris:
                    entity = self._extract_entity_info(graph, s, "Class")
                    entities.append(entity)
                    seen_iris.add(str(s))

        # Extract properties
        prop_types = [OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty, RDF.Property]
        for prop_type in prop_types:
            for s in graph.subjects(RDF.type, prop_type):
                if isinstance(s, URIRef) and str(s) not in seen_iris:
                    entity = self._extract_entity_info(graph, s, "Property")
                    entities.append(entity)
                    seen_iris.add(str(s))

        # Extract individuals
        for s in graph.subjects(RDF.type, OWL.NamedIndividual):
            if isinstance(s, URIRef) and str(s) not in seen_iris:
                entity = self._extract_entity_info(graph, s, "Individual")
                entities.append(entity)
                seen_iris.add(str(s))

        logger.info(f"Extracted {len(entities)} entities from graph")
        return entities

    def _extract_entity_info(self, graph, subject, entity_type: str) -> ParsedEntity:
        """Extract detailed info for a single entity"""
        RDFS = self._rdf_imports["RDFS"]
        SKOS = self._rdf_imports["SKOS"]
        DC = self._rdf_imports["DC"]
        URIRef = self._rdf_imports["URIRef"]

        iri = str(subject)
        name = self._get_local_name(iri)

        # Get labels
        labels = []
        for pred in [RDFS.label, SKOS.prefLabel, SKOS.altLabel, DC.title]:
            for obj in graph.objects(subject, pred):
                labels.append(str(obj))

        # Get comments/descriptions
        comments = []
        for pred in [RDFS.comment, SKOS.definition, DC.description, SKOS.note]:
            for obj in graph.objects(subject, pred):
                comments.append(str(obj))

        # Get parent classes
        parents = []
        for obj in graph.objects(subject, RDFS.subClassOf):
            if isinstance(obj, URIRef):
                parents.append(str(obj))

        # Build metadata
        metadata = {}
        for pred, obj in graph.predicate_objects(subject):
            pred_name = self._get_local_name(str(pred))
            if pred_name not in ["type", "label", "comment", "subClassOf"]:
                if pred_name not in metadata:
                    metadata[pred_name] = []
                metadata[pred_name].append(str(obj))

        return ParsedEntity(
            iri=iri,
            name=labels[0] if labels else name,
            entity_type=entity_type,
            inferred_root_type=None,  # Will be filled by mapper
            labels=labels,
            comments=comments,
            parent_iris=parents,
            metadata=metadata
        )

    def _get_local_name(self, iri: str) -> str:
        """Extract local name from IRI"""
        if "#" in iri:
            return iri.split("#")[-1]
        elif "/" in iri:
            return iri.split("/")[-1]
        return iri

    def extract_relationships(self, graph) -> List[Dict[str, Any]]:
        """
        Extract relationships from graph.

        Looks for:
        - rdfs:subClassOf (hierarchy)
        - owl:equivalentClass
        - Custom object properties
        """
        RDF = self._rdf_imports["RDF"]
        RDFS = self._rdf_imports["RDFS"]
        OWL = self._rdf_imports["OWL"]
        URIRef = self._rdf_imports["URIRef"]

        relationships = []

        # subClassOf relationships
        for s, o in graph.subject_objects(RDFS.subClassOf):
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                relationships.append({
                    "source": str(s),
                    "target": str(o),
                    "predicate": "rdfs:subClassOf",
                    "type": "hierarchy"
                })

        # equivalentClass
        for s, o in graph.subject_objects(OWL.equivalentClass):
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                relationships.append({
                    "source": str(s),
                    "target": str(o),
                    "predicate": "owl:equivalentClass",
                    "type": "equivalence"
                })

        # Object property assertions
        for prop in graph.subjects(RDF.type, OWL.ObjectProperty):
            for s, o in graph.subject_objects(prop):
                if isinstance(s, URIRef) and isinstance(o, URIRef):
                    relationships.append({
                        "source": str(s),
                        "target": str(o),
                        "predicate": str(prop),
                        "type": "object_property"
                    })

        logger.info(f"Extracted {len(relationships)} relationships from graph")
        return relationships


class OntologyImporter:
    """
    v10 Ontology Import Pipeline.

    Pipeline:
    1. Parse RDF/OWL (deterministic)
    2. Extract entities
    3. Map root types (rule-based heuristics)
    4. SLM Enhancement (optional, if use_slm=true)
    5. Conflict detection
    6. Conflict resolution (AI debate)
    7. Commit to MO
    8. Update MMO metrics
    9. Create snapshot
    """

    def __init__(self):
        self.settings = get_settings()
        self.parser = RDFParser()
        self._slm_service = None

    def _get_slm_service(self):
        """Lazy import SLM service"""
        if self._slm_service is None:
            from ai.slm.service import SLMService
            self._slm_service = SLMService()
        return self._slm_service

    async def import_ontology(
        self,
        request: OntologyImportRequest
    ) -> OntologyImportResult:
        """
        Import ontology following v10 pipeline.
        """
        start_time = time.time()
        operation_id = generate_operation_id()
        version = generate_version_string()

        errors = []
        warnings = []
        entities_created = 0
        causality_links_created = 0
        epistemic_annotations_created = 0
        conflicts_detected = 0
        conflicts_resolved = 0
        slm_enhancements = 0

        try:
            # Step 1: Parse RDF/OWL
            if request.content:
                graph, triple_count = self.parser.parse_content(
                    request.content,
                    request.format
                )
            elif request.source_url:
                graph, triple_count = await self.parser.parse_url(
                    request.source_url,
                    request.format
                )
            else:
                raise ValueError("Either content or source_url required")

            # Check triple limit
            if triple_count > self.settings.ontology_max_triples:
                warnings.append(f"Ontology has {triple_count} triples, exceeds limit of {self.settings.ontology_max_triples}")

            # Step 2: Extract entities
            entities = self.parser.extract_entities(graph)
            relationships = self.parser.extract_relationships(graph)

            # Step 3 & 4: Map root types (with optional SLM enhancement)
            from .mapper import RootTypeMapper
            mapper = RootTypeMapper()

            mapped_entities = []
            for entity in entities:
                # Rule-based mapping first
                root_type, confidence = mapper.infer_root_type(entity)
                entity.inferred_root_type = root_type

                # SLM enhancement if enabled and confidence is low
                if request.use_slm and confidence < 0.7:
                    try:
                        slm_service = self._get_slm_service()
                        slm_root, slm_conf, reasoning = await slm_service.infer_root_type(
                            entity_name=entity.name,
                            description=entity.comments[0] if entity.comments else "",
                            context=entity.entity_type,
                            source=request.source_url or "direct_content"
                        )

                        if slm_conf > confidence:
                            entity.inferred_root_type = slm_root
                            entity.metadata["slm_enhancement"] = {
                                "original_type": root_type.value,
                                "enhanced_type": slm_root.value,
                                "confidence": slm_conf,
                                "reasoning": reasoning
                            }
                            slm_enhancements += 1
                    except Exception as e:
                        warnings.append(f"SLM enhancement failed for {entity.name}: {e}")

                mapped_entities.append(entity)

            entities_created = len(mapped_entities)

            # Step 5: Conflict detection
            conflicts = await self._detect_conflicts(mapped_entities, relationships)
            conflicts_detected = len(conflicts)

            # Step 6: Conflict resolution
            if conflicts and request.conflict_resolution == "auto":
                resolved = await self._resolve_conflicts(conflicts)
                conflicts_resolved = resolved

            # Build provenance
            provenance = Provenance(
                source_ontology=request.source_url or "direct_content",
                parsed_by=f"rdflib {self._get_rdflib_version()}",
                enhanced_by=f"{self.settings.slm_model_name}" if slm_enhancements > 0 else None,
                ai_confidence=None,
                committed_at=datetime.utcnow(),
                operation_id=operation_id
            )

            processing_time = (time.time() - start_time) * 1000

            return OntologyImportResult(
                success=True,
                ontology_id=operation_id,
                version=version,
                triples_imported=triple_count,
                entities_created=entities_created,
                causality_links_created=causality_links_created,
                epistemic_annotations_created=epistemic_annotations_created,
                conflicts_detected=conflicts_detected,
                conflicts_resolved=conflicts_resolved,
                slm_enhancements=slm_enhancements,
                processing_time_ms=processing_time,
                provenance=provenance,
                errors=errors,
                warnings=warnings
            )

        except Exception as e:
            logger.error(f"Ontology import failed: {e}")
            return OntologyImportResult(
                success=False,
                ontology_id=operation_id,
                version=version,
                triples_imported=0,
                entities_created=0,
                causality_links_created=0,
                epistemic_annotations_created=0,
                conflicts_detected=0,
                conflicts_resolved=0,
                slm_enhancements=0,
                processing_time_ms=(time.time() - start_time) * 1000,
                provenance=Provenance(operation_id=operation_id),
                errors=[str(e)],
                warnings=warnings
            )

    async def _detect_conflicts(
        self,
        entities: List[ParsedEntity],
        relationships: List[Dict]
    ) -> List[Conflict]:
        """Detect conflicts in imported data"""
        conflicts = []
        conflict_id = 0

        # Check for root type disagreements (same name, different inferred types)
        name_to_entities = {}
        for entity in entities:
            name = entity.name.lower()
            if name in name_to_entities:
                existing = name_to_entities[name]
                if existing.inferred_root_type != entity.inferred_root_type:
                    conflict_id += 1
                    conflicts.append(Conflict(
                        id=f"conflict_{conflict_id}",
                        conflict_type=ConflictType.ROOT_DISAGREEMENT,
                        entity_a=existing.iri,
                        entity_b=entity.iri,
                        description=f"Root type disagreement: {existing.inferred_root_type} vs {entity.inferred_root_type}",
                        severity=0.7,
                        resolution_options=["keep_first", "keep_second", "context_dependent"]
                    ))
            else:
                name_to_entities[name] = entity

        # Check for potential causal cycles (simplified)
        # In full implementation, would use graph algorithms

        return conflicts

    async def _resolve_conflicts(self, conflicts: List[Conflict]) -> int:
        """Resolve conflicts using SLM debate"""
        resolved = 0

        for conflict in conflicts:
            if conflict.conflict_type == ConflictType.ROOT_DISAGREEMENT:
                try:
                    slm_service = self._get_slm_service()
                    result = await slm_service.resolve_conflict_via_debate(
                        conflict,
                        max_rounds=self.settings.conflict_debate_rounds
                    )

                    if result.consensus_reached:
                        conflict.resolved = True
                        conflict.resolution = result.final_resolution
                        resolved += 1
                except Exception as e:
                    logger.warning(f"Conflict resolution failed: {e}")

        return resolved

    def _get_rdflib_version(self) -> str:
        """Get rdflib version"""
        try:
            import rdflib
            return rdflib.__version__
        except Exception:
            return "unknown"
