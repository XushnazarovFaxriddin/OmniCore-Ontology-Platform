"""
OmniCore Platform v10 - Root Type Mapper and Causality Extractor
Rule-based heuristics for deterministic ontology mapping
"""

from typing import Tuple, List, Dict, Any, Optional
import re

from common.models import ParsedEntity, RootType, CausalityType
from common.logging_config import get_logger

logger = get_logger("rdf.mapper")


class RootTypeMapper:
    """
    Rule-based Root Type Mapper for v10.

    v10 Philosophy: "Start deterministic, augment intelligently"
    - Rule-based heuristics provide baseline classification
    - SLM enhancement only when confidence is low

    v10 Root Types:
    - EXTANT: Entities with spatiotemporal location
    - ABSTRACT: Atemporal, mind-independent structures
    - MENTAL: Subjective, first-person accessible states
    - FICTIVE: Context-dependent representations

    Clarifications:
    - "Sherlock Holmes" is FICTIVE (narrative context), not MENTAL
    - "Pain" is MENTAL when experienced, ABSTRACT when defined
    """

    # Known ontology prefixes and their typical root types
    ONTOLOGY_HINTS = {
        # BFO (Basic Formal Ontology) mappings
        "BFO_0000001": RootType.EXTANT,      # entity
        "BFO_0000002": RootType.EXTANT,      # continuant
        "BFO_0000003": RootType.EXTANT,      # occurrent
        "BFO_0000004": RootType.EXTANT,      # independent continuant
        "BFO_0000020": RootType.EXTANT,      # specifically dependent continuant
        "BFO_0000031": RootType.ABSTRACT,    # generically dependent continuant
        "BFO_0000040": RootType.EXTANT,      # material entity

        # DOLCE mappings
        "DOLCE:Abstract": RootType.ABSTRACT,
        "DOLCE:Physical": RootType.EXTANT,
        "DOLCE:Mental": RootType.MENTAL,
    }

    # Keyword patterns for classification
    EXTANT_KEYWORDS = [
        r"\b(physical|material|object|thing|body|entity|substance|organism)\b",
        r"\b(location|place|space|region|area|zone)\b",
        r"\b(event|process|activity|action|occurrence|happening)\b",
        r"\b(person|human|animal|plant|cell|molecule|atom)\b",
        r"\b(device|machine|tool|instrument|equipment)\b",
        r"\b(building|structure|artifact|product)\b",
    ]

    ABSTRACT_KEYWORDS = [
        r"\b(number|quantity|amount|measure|degree)\b",
        r"\b(property|quality|attribute|characteristic|feature)\b",
        r"\b(relation|relationship|connection|association)\b",
        r"\b(concept|idea|notion|theory|principle)\b",
        r"\b(class|category|type|kind|species|genus)\b",
        r"\b(mathematical|logical|formal|structural)\b",
        r"\b(law|rule|axiom|theorem|proposition)\b",
        r"\b(unit|dimension|metric|standard)\b",
        r"\b(ontology|schema|vocabulary|taxonomy)\b",
    ]

    MENTAL_KEYWORDS = [
        r"\b(emotion|feeling|mood|affect|sentiment)\b",
        r"\b(thought|belief|desire|intention|memory)\b",
        r"\b(perception|sensation|experience|consciousness)\b",
        r"\b(pain|pleasure|happiness|sadness|fear|anger)\b",
        r"\b(mental|psychological|cognitive|subjective)\b",
        r"\b(dream|imagination|fantasy|hallucination)\b",
        r"\b(attention|awareness|mindfulness)\b",
    ]

    FICTIVE_KEYWORDS = [
        r"\b(fictional|fictitious|imaginary|mythical)\b",
        r"\b(character|story|narrative|tale|novel)\b",
        r"\b(simulation|model|representation|depiction)\b",
        r"\b(hypothetical|counterfactual|possible|potential)\b",
        r"\b(game|virtual|digital|simulated)\b",
        r"\b(legend|myth|folklore|fairy)\b",
    ]

    # Negative patterns (reduce confidence)
    AMBIGUOUS_PATTERNS = [
        r"\b(or|and|both|either|neither)\b",
        r"\b(may|might|could|possibly|perhaps)\b",
        r"\b(sometimes|occasionally|often|usually)\b",
    ]

    def __init__(self):
        # Compile patterns for efficiency
        self._extant_patterns = [re.compile(p, re.I) for p in self.EXTANT_KEYWORDS]
        self._abstract_patterns = [re.compile(p, re.I) for p in self.ABSTRACT_KEYWORDS]
        self._mental_patterns = [re.compile(p, re.I) for p in self.MENTAL_KEYWORDS]
        self._fictive_patterns = [re.compile(p, re.I) for p in self.FICTIVE_KEYWORDS]
        self._ambiguous_patterns = [re.compile(p, re.I) for p in self.AMBIGUOUS_PATTERNS]

    def infer_root_type(self, entity: ParsedEntity) -> Tuple[RootType, float]:
        """
        Infer root type using rule-based heuristics.

        Returns:
            Tuple of (RootType, confidence)
        """
        # Check known ontology hints first
        for hint, root_type in self.ONTOLOGY_HINTS.items():
            if hint in entity.iri:
                return root_type, 0.95

        # Build text corpus for analysis
        text_corpus = self._build_text_corpus(entity)

        # Score each root type
        scores = {
            RootType.EXTANT: self._score_patterns(text_corpus, self._extant_patterns),
            RootType.ABSTRACT: self._score_patterns(text_corpus, self._abstract_patterns),
            RootType.MENTAL: self._score_patterns(text_corpus, self._mental_patterns),
            RootType.FICTIVE: self._score_patterns(text_corpus, self._fictive_patterns),
        }

        # Apply entity type hints
        if entity.entity_type == "Class":
            scores[RootType.ABSTRACT] += 0.1
        elif entity.entity_type == "Individual":
            scores[RootType.EXTANT] += 0.1

        # Apply parent class hints
        for parent in entity.parent_iris:
            parent_lower = parent.lower()
            if "abstract" in parent_lower or "concept" in parent_lower:
                scores[RootType.ABSTRACT] += 0.15
            elif "physical" in parent_lower or "material" in parent_lower:
                scores[RootType.EXTANT] += 0.15
            elif "mental" in parent_lower or "psychological" in parent_lower:
                scores[RootType.MENTAL] += 0.15

        # Get best score
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]

        # Calculate confidence
        total_score = sum(scores.values())
        if total_score > 0:
            confidence = best_score / total_score
        else:
            confidence = 0.25  # No signals, default confidence

        # Reduce confidence if ambiguous
        ambiguity_count = self._count_ambiguous(text_corpus)
        if ambiguity_count > 0:
            confidence *= max(0.5, 1 - (ambiguity_count * 0.1))

        # Default to ABSTRACT if no strong signal
        if best_score < 0.1:
            best_type = RootType.ABSTRACT
            confidence = 0.3

        return best_type, min(1.0, confidence)

    def _build_text_corpus(self, entity: ParsedEntity) -> str:
        """Build text corpus from entity for pattern matching"""
        parts = [entity.name]
        parts.extend(entity.labels)
        parts.extend(entity.comments)

        # Include some metadata values
        for key, values in entity.metadata.items():
            if isinstance(values, list):
                parts.extend(str(v) for v in values[:3])
            else:
                parts.append(str(values))

        return " ".join(parts)

    def _score_patterns(self, text: str, patterns: List[re.Pattern]) -> float:
        """Score text against pattern list"""
        score = 0.0
        for pattern in patterns:
            matches = pattern.findall(text)
            score += len(matches) * 0.1
        return min(1.0, score)

    def _count_ambiguous(self, text: str) -> int:
        """Count ambiguous patterns in text"""
        count = 0
        for pattern in self._ambiguous_patterns:
            count += len(pattern.findall(text))
        return count


class CausalityExtractor:
    """
    Rule-based Causality Extractor for v10.

    v10 Causality Types:
    - EFFICIENT: causesDirectly (hammer → nail_driving)
    - FINAL: servesPurpose (nest → offspring_protection)
    - MATERIAL: constitutedBy (statue → bronze)
    - FORMAL: structuredAs (organism → genome)
    - EMERGENT: emergesFrom (consciousness → neural_activity)
    """

    # Predicate patterns for causality detection
    CAUSALITY_PREDICATES = {
        # Efficient causality
        r"causes?|caused_by|results?_in|leads?_to|produces?|generates?|triggers?": CausalityType.EFFICIENT,
        r"affects?|influences?|impacts?|determines?": CausalityType.EFFICIENT,

        # Final causality
        r"purpose|goal|function|serves?|aims?_for|intended_for": CausalityType.FINAL,
        r"used_for|designed_for|meant_for|for_the_purpose_of": CausalityType.FINAL,

        # Material causality
        r"made_of|composed_of|constituted_by|consists?_of|contains?": CausalityType.MATERIAL,
        r"material|substance|component|ingredient|element": CausalityType.MATERIAL,

        # Formal causality
        r"structured_as|organized_as|shaped_by|formed_by|patterned_after": CausalityType.FORMAL,
        r"has_structure|has_form|has_pattern|defined_by": CausalityType.FORMAL,

        # Emergent causality
        r"emerges?_from|arises?_from|develops?_from|springs?_from": CausalityType.EMERGENT,
        r"supervenes?_on|depends?_on|based_on|grounded_in": CausalityType.EMERGENT,
    }

    # Property mappings from common ontologies
    PROPERTY_MAPPINGS = {
        "causedBy": CausalityType.EFFICIENT,
        "causes": CausalityType.EFFICIENT,
        "hasCause": CausalityType.EFFICIENT,
        "resultsIn": CausalityType.EFFICIENT,

        "hasPurpose": CausalityType.FINAL,
        "hasFunction": CausalityType.FINAL,
        "servesAs": CausalityType.FINAL,

        "hasMaterial": CausalityType.MATERIAL,
        "madeOf": CausalityType.MATERIAL,
        "hasComponent": CausalityType.MATERIAL,
        "partOf": CausalityType.MATERIAL,

        "hasStructure": CausalityType.FORMAL,
        "structuredBy": CausalityType.FORMAL,
        "conformsTo": CausalityType.FORMAL,

        "emergesFrom": CausalityType.EMERGENT,
        "derivedFrom": CausalityType.EMERGENT,
        "supervenesOn": CausalityType.EMERGENT,
    }

    def __init__(self):
        # Compile patterns
        self._patterns = {
            re.compile(pattern, re.I): ctype
            for pattern, ctype in self.CAUSALITY_PREDICATES.items()
        }

    def extract_from_relationships(
        self,
        relationships: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract causality types from relationships.

        Returns list of causality links with inferred types.
        """
        causality_links = []

        for rel in relationships:
            predicate = rel.get("predicate", "")
            predicate_name = self._get_local_name(predicate)

            # Check direct property mappings
            if predicate_name in self.PROPERTY_MAPPINGS:
                causality_type = self.PROPERTY_MAPPINGS[predicate_name]
                causality_links.append({
                    "source": rel["source"],
                    "target": rel["target"],
                    "causality_type": causality_type.value,
                    "confidence": 0.9,
                    "predicate": predicate,
                    "inference_method": "property_mapping"
                })
                continue

            # Check pattern matching
            for pattern, ctype in self._patterns.items():
                if pattern.search(predicate_name):
                    causality_links.append({
                        "source": rel["source"],
                        "target": rel["target"],
                        "causality_type": ctype.value,
                        "confidence": 0.75,
                        "predicate": predicate,
                        "inference_method": "pattern_matching"
                    })
                    break

        return causality_links

    def extract_from_text(
        self,
        text: str,
        entity_pairs: List[Tuple[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Extract implicit causality from text descriptions.

        Returns list of potential causality links.
        """
        causality_links = []
        text_lower = text.lower()

        for source, target in entity_pairs:
            # Check if both entities mentioned in text
            source_lower = source.lower()
            target_lower = target.lower()

            if source_lower not in text_lower or target_lower not in text_lower:
                continue

            # Look for causality patterns between entities
            for pattern, ctype in self._patterns.items():
                # Build regex to find pattern between entities
                between_pattern = rf"{re.escape(source_lower)}\s+.*?\s+{pattern.pattern}.*?\s+{re.escape(target_lower)}"
                if re.search(between_pattern, text_lower):
                    causality_links.append({
                        "source": source,
                        "target": target,
                        "causality_type": ctype.value,
                        "confidence": 0.6,
                        "evidence": f"Pattern found in text",
                        "inference_method": "text_extraction"
                    })
                    break

        return causality_links

    def _get_local_name(self, iri: str) -> str:
        """Extract local name from IRI"""
        if "#" in iri:
            return iri.split("#")[-1]
        elif "/" in iri:
            return iri.split("/")[-1]
        return iri


class EpistemicAnnotator:
    """
    Rule-based Epistemic Annotator for v10.

    v10 Epistemic Basis:
    - AXIOMATIC: Self-evident truths, logical necessities
    - EMPIRICAL: Based on observation, experiments, evidence
    - CONSENSUS: Agreed upon by community/experts
    - SPECULATIVE: Hypothetical, theoretical, uncertain
    """

    AXIOMATIC_PATTERNS = [
        r"\b(axiom|definition|by definition|necessarily|always true)\b",
        r"\b(logical|tautology|self-evident|a priori)\b",
        r"\b(mathematical|proven|theorem|lemma)\b",
    ]

    EMPIRICAL_PATTERNS = [
        r"\b(observed|measured|detected|found|discovered)\b",
        r"\b(experiment|study|research|investigation|trial)\b",
        r"\b(evidence|data|statistics|results|findings)\b",
        r"\b(PMID|DOI|published|journal|paper)\b",
    ]

    CONSENSUS_PATTERNS = [
        r"\b(consensus|agreed|accepted|standard|convention)\b",
        r"\b(community|experts|scientists|researchers)\b",
        r"\b(established|recognized|acknowledged|endorsed)\b",
    ]

    SPECULATIVE_PATTERNS = [
        r"\b(hypothesis|theory|proposed|suggested|might)\b",
        r"\b(uncertain|unclear|unknown|speculative)\b",
        r"\b(potential|possible|maybe|perhaps|could)\b",
    ]

    def __init__(self):
        from common.models import EpistemicBasis
        self.EpistemicBasis = EpistemicBasis

        self._patterns = {
            EpistemicBasis.AXIOMATIC: [re.compile(p, re.I) for p in self.AXIOMATIC_PATTERNS],
            EpistemicBasis.EMPIRICAL: [re.compile(p, re.I) for p in self.EMPIRICAL_PATTERNS],
            EpistemicBasis.CONSENSUS: [re.compile(p, re.I) for p in self.CONSENSUS_PATTERNS],
            EpistemicBasis.SPECULATIVE: [re.compile(p, re.I) for p in self.SPECULATIVE_PATTERNS],
        }

    def annotate(
        self,
        text: str,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate epistemic annotation for text.

        Returns dict with basis, certainty, and reasoning.
        """
        # Score each basis
        scores = {}
        for basis, patterns in self._patterns.items():
            score = 0
            for pattern in patterns:
                matches = pattern.findall(text)
                score += len(matches)
            scores[basis] = score

        # Check source for hints
        if source:
            source_lower = source.lower()
            if "pmid" in source_lower or "doi" in source_lower:
                scores[self.EpistemicBasis.EMPIRICAL] += 3
            elif "wiki" in source_lower:
                scores[self.EpistemicBasis.CONSENSUS] += 2

        # Get best basis
        best_basis = max(scores, key=scores.get)
        best_score = scores[best_basis]

        # Default to speculative if no strong signal
        if best_score < 1:
            best_basis = self.EpistemicBasis.SPECULATIVE

        # Calculate certainty based on basis and scores
        certainty_base = {
            self.EpistemicBasis.AXIOMATIC: 0.95,
            self.EpistemicBasis.EMPIRICAL: 0.80,
            self.EpistemicBasis.CONSENSUS: 0.70,
            self.EpistemicBasis.SPECULATIVE: 0.40,
        }

        certainty = certainty_base[best_basis]

        # Adjust certainty based on strength of signals
        if best_score > 5:
            certainty = min(1.0, certainty + 0.1)
        elif best_score < 2:
            certainty = max(0.2, certainty - 0.1)

        return {
            "basis": best_basis.value,
            "certainty": certainty,
            "scores": {k.value: v for k, v in scores.items()},
            "reasoning": f"Best match: {best_basis.value} with score {best_score}"
        }
