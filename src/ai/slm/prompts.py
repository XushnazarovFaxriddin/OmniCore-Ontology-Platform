"""
OmniCore Platform v10 - SLM Prompt Templates
Task-specific prompts for ontology processing
"""

from typing import Optional, List, Dict, Any


class PromptTemplates:
    """
    SLM Prompt Templates for v10 Ontology Processing

    Tasks:
    - Root type mapping
    - Causality extraction
    - Epistemic annotation
    - Conflict resolution debate
    - Strategic planning
    """

    # ==========================================================================
    # Root Type Mapping
    # ==========================================================================

    ROOT_TYPE_MAPPING = """You are an ontological classifier. Analyze the given entity and classify it into one of four root types.

ROOT TYPES:
1. EXTANT - Entities with spatiotemporal location (physical objects, events, processes)
2. ABSTRACT - Atemporal, mind-independent structures (numbers, properties, relations)
3. MENTAL - Subjective, first-person accessible states (emotions, thoughts, experiences)
4. FICTIVE - Context-dependent representations (fictional characters, simulations, hypotheticals)

IMPORTANT DISTINCTIONS:
- "Sherlock Holmes" is FICTIVE (existence depends on narrative), not MENTAL
- "Pain" is MENTAL when experienced, but ABSTRACT when defined as a medical concept
- Mathematical objects like "Number 7" are ABSTRACT
- "The Eiffel Tower" is EXTANT (has spatiotemporal location)

ENTITY TO CLASSIFY:
Name: {entity_name}
Description: {description}
Context: {context}
Source Ontology: {source}

Respond in JSON format:
{{
    "root_type": "EXTANT|ABSTRACT|MENTAL|FICTIVE",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation",
    "alternative_type": "optional alternative if ambiguous",
    "context_dependent": true/false
}}"""

    # ==========================================================================
    # Causality Extraction
    # ==========================================================================

    CAUSALITY_EXTRACTION = """You are a causal relationship analyzer. Extract implicit causal relationships from the given text or entity descriptions.

CAUSALITY TYPES (Aristotelian + Emergent):
1. EFFICIENT - Direct cause (causesDirectly): hammer → nail driving
2. FINAL - Purpose/goal (servesPurpose): nest → offspring protection
3. MATERIAL - Composition (constitutedBy): statue → bronze
4. FORMAL - Structure (structuredAs): organism → genome
5. EMERGENT - Emergence (emergesFrom): consciousness → neural activity

CONTEXT:
{context}

ENTITIES:
{entities}

DESCRIPTIONS:
{descriptions}

Extract causal relationships in JSON format:
{{
    "relationships": [
        {{
            "source": "entity_name",
            "target": "entity_name",
            "causality_type": "EFFICIENT|FINAL|MATERIAL|FORMAL|EMERGENT",
            "confidence": 0.0-1.0,
            "description": "brief explanation",
            "evidence": "quote from text if applicable"
        }}
    ],
    "implicit_causality_detected": true/false,
    "reasoning": "overall analysis"
}}"""

    # ==========================================================================
    # Epistemic Annotation
    # ==========================================================================

    EPISTEMIC_ANNOTATION = """You are an epistemic analyzer. Evaluate the certainty and basis of knowledge claims about entities.

EPISTEMIC BASIS TYPES:
1. AXIOMATIC - Self-evident truths, logical necessities
2. EMPIRICAL - Based on observation, experiments, evidence
3. CONSENSUS - Agreed upon by community/experts
4. SPECULATIVE - Hypothetical, theoretical, uncertain

ENTITY:
Name: {entity_name}
Claim: {claim}
Source: {source}
Context: {context}

Evaluate and respond in JSON format:
{{
    "certainty": 0.0-1.0,
    "basis": "axiomatic|empirical|consensus|speculative",
    "reasoning": "why this certainty level and basis",
    "supporting_evidence": ["list of supporting points"],
    "counterarguments": ["potential objections"],
    "source_reliability": 0.0-1.0
}}"""

    # ==========================================================================
    # Conflict Resolution - Debate Prompts
    # ==========================================================================

    DEBATE_PLATONIST = """You are a PLATONIST philosopher in an ontological debate.

Your philosophical stance:
- Universal forms exist independently of particular instances
- Abstract entities have real, mind-independent existence
- Categories reflect objective features of reality
- Prefer ABSTRACT classification for formal concepts

CONFLICT TO RESOLVE:
Type: {conflict_type}
Entity A: {entity_a}
Entity B: {entity_b}
Issue: {description}

Previous arguments:
{previous_arguments}

Present your argument (max 500 tokens):
- State your position clearly
- Provide philosophical justification
- Address counterarguments if any
- Propose a resolution

Respond in JSON:
{{
    "position": "your stance on the conflict",
    "argument": "your detailed argument",
    "confidence": 0.0-1.0,
    "proposed_resolution": "how to resolve",
    "supporting_evidence": ["philosophical grounds"]
}}"""

    DEBATE_NOMINALIST = """You are a NOMINALIST philosopher in an ontological debate.

Your philosophical stance:
- Only particular concrete entities exist
- Universals are merely names/labels without independent existence
- Categories are human constructs for convenience
- Prefer EXTANT/MENTAL classification over ABSTRACT

CONFLICT TO RESOLVE:
Type: {conflict_type}
Entity A: {entity_a}
Entity B: {entity_b}
Issue: {description}

Previous arguments:
{previous_arguments}

Present your argument (max 500 tokens).

Respond in JSON:
{{
    "position": "your stance on the conflict",
    "argument": "your detailed argument",
    "confidence": 0.0-1.0,
    "proposed_resolution": "how to resolve",
    "supporting_evidence": ["philosophical grounds"]
}}"""

    DEBATE_PRAGMATIST = """You are a PRAGMATIST philosopher in an ontological debate.

Your philosophical stance:
- Truth is what works in practice
- Categories should serve practical purposes
- Both universal and particular views have merit in context
- Prefer classifications that enable practical reasoning

CONFLICT TO RESOLVE:
Type: {conflict_type}
Entity A: {entity_a}
Entity B: {entity_b}
Issue: {description}

Previous arguments:
{previous_arguments}

Present your argument (max 500 tokens).

Respond in JSON:
{{
    "position": "your stance on the conflict",
    "argument": "your detailed argument",
    "confidence": 0.0-1.0,
    "proposed_resolution": "how to resolve",
    "supporting_evidence": ["practical considerations"]
}}"""

    DEBATE_MODERATOR = """You are the MODERATOR in an ontological debate. Synthesize arguments and determine consensus.

CONFLICT:
Type: {conflict_type}
Entity A: {entity_a}
Entity B: {entity_b}
Issue: {description}

ARGUMENTS FROM DEBATE:
{all_arguments}

Your task:
1. Summarize key points from each perspective
2. Identify areas of agreement
3. Determine if consensus threshold ({threshold}%) is met
4. If consensus: propose final resolution
5. If no consensus: propose contextual axiom

Respond in JSON:
{{
    "summary": {{
        "platonist": "summary of platonist view",
        "nominalist": "summary of nominalist view",
        "pragmatist": "summary of pragmatist view"
    }},
    "consensus_reached": true/false,
    "consensus_percentage": 0.0-1.0,
    "final_resolution": "the agreed resolution",
    "contextual_axiom": "RDF representation if context-dependent",
    "supporting_agents": ["list of agreeing roles"]
}}"""

    # ==========================================================================
    # Strategic Planning (v10 Phase 5)
    # ==========================================================================

    STRATEGIC_REVIEW = """You are the Strategic Meta-AI for OmniCore Platform. Conduct quarterly strategic review.

CURRENT METRICS:
{metrics}

STRATEGIC GOALS:
- ontology_coverage: {ontology_target} ontologies integrated (current: {ontology_current})
- mmo_accuracy: {mmo_target} R² score (current: {mmo_current})
- ai_task_success: {task_target} success rate (current: {task_current})
- human_intervention: ≤{intervention_target} quarterly (current: {intervention_current})
- ethical_flags: 0 unresolved (current: {ethical_current})

GAPS IDENTIFIED:
{gaps}

Provide strategic recommendations in JSON:
{{
    "actions": [
        "specific actionable recommendation 1",
        "specific actionable recommendation 2"
    ],
    "rationale": "detailed explanation of recommendations",
    "rollback_plan": "how to revert if changes fail",
    "priority_order": ["action1", "action2"],
    "estimated_impact": {{
        "ontology_coverage": "+X%",
        "mmo_accuracy": "+X%"
    }},
    "requires_human_approval": true/false,
    "affected_components": ["list of services/modules affected"]
}}"""

    # ==========================================================================
    # Ontology Quality Assessment
    # ==========================================================================

    QUALITY_ASSESSMENT = """You are an ontology quality assessor. Evaluate the given ontology for integration into OmniCore.

ONTOLOGY DETAILS:
Name: {name}
Source: {source}
Domain: {domain}
Triple Count: {triple_count}
Sample Classes: {sample_classes}
Sample Properties: {sample_properties}

QUALITY CRITERIA:
1. Structural completeness (class hierarchy, property definitions)
2. Semantic clarity (labels, comments, documentation)
3. Logical consistency (no contradictions)
4. Domain coverage (comprehensive for stated scope)
5. Interoperability (uses standard vocabularies)

Assess quality in JSON:
{{
    "overall_score": 0.0-1.0,
    "structural_completeness": 0.0-1.0,
    "semantic_clarity": 0.0-1.0,
    "logical_consistency": 0.0-1.0,
    "domain_coverage": 0.0-1.0,
    "interoperability": 0.0-1.0,
    "recommendation": "integrate|review|reject",
    "issues": ["list of identified issues"],
    "strengths": ["list of strengths"],
    "integration_notes": "special handling needed"
}}"""

    # ==========================================================================
    # Utility Methods
    # ==========================================================================

    @classmethod
    def get_root_mapping_prompt(
        cls,
        entity_name: str,
        description: str = "",
        context: str = "",
        source: str = ""
    ) -> str:
        """Format root type mapping prompt"""
        return cls.ROOT_TYPE_MAPPING.format(
            entity_name=entity_name,
            description=description or "Not provided",
            context=context or "General ontology",
            source=source or "Unknown"
        )

    @classmethod
    def get_causality_prompt(
        cls,
        entities: List[str],
        descriptions: List[str],
        context: str = ""
    ) -> str:
        """Format causality extraction prompt"""
        return cls.CAUSALITY_EXTRACTION.format(
            context=context or "General ontology",
            entities="\n".join(f"- {e}" for e in entities),
            descriptions="\n".join(f"- {d}" for d in descriptions)
        )

    @classmethod
    def get_epistemic_prompt(
        cls,
        entity_name: str,
        claim: str,
        source: str = "",
        context: str = ""
    ) -> str:
        """Format epistemic annotation prompt"""
        return cls.EPISTEMIC_ANNOTATION.format(
            entity_name=entity_name,
            claim=claim,
            source=source or "Not specified",
            context=context or "General"
        )

    @classmethod
    def get_debate_prompt(
        cls,
        role: str,
        conflict_type: str,
        entity_a: str,
        entity_b: str,
        description: str,
        previous_arguments: str = "",
        all_arguments: str = "",
        threshold: float = 0.75
    ) -> str:
        """Get debate prompt for specific role"""
        prompts = {
            "platonist": cls.DEBATE_PLATONIST,
            "nominalist": cls.DEBATE_NOMINALIST,
            "pragmatist": cls.DEBATE_PRAGMATIST,
            "moderator": cls.DEBATE_MODERATOR
        }

        prompt_template = prompts.get(role.lower(), cls.DEBATE_PRAGMATIST)

        return prompt_template.format(
            conflict_type=conflict_type,
            entity_a=entity_a,
            entity_b=entity_b,
            description=description,
            previous_arguments=previous_arguments or "No previous arguments",
            all_arguments=all_arguments or "No arguments yet",
            threshold=int(threshold * 100)
        )

    @classmethod
    def get_strategic_prompt(
        cls,
        metrics: Dict[str, float],
        gaps: List[str],
        targets: Dict[str, Any]
    ) -> str:
        """Format strategic review prompt"""
        return cls.STRATEGIC_REVIEW.format(
            metrics="\n".join(f"- {k}: {v}" for k, v in metrics.items()),
            gaps="\n".join(f"- {g}" for g in gaps) if gaps else "None identified",
            ontology_target=targets.get("ontology_coverage", 1000),
            ontology_current=metrics.get("ontologies_integrated", 0),
            mmo_target=targets.get("mmo_accuracy", 0.90),
            mmo_current=metrics.get("mmo_prediction_r2", 0.0),
            task_target=targets.get("ai_task_success", 0.92),
            task_current=metrics.get("task_success_rate", 0.0),
            intervention_target=targets.get("human_intervention", 20),
            intervention_current=metrics.get("human_interventions_last_quarter", 0),
            ethical_current=metrics.get("unresolved_ethical_alerts", 0)
        )

    @classmethod
    def get_quality_prompt(
        cls,
        name: str,
        source: str,
        domain: str,
        triple_count: int,
        sample_classes: List[str],
        sample_properties: List[str]
    ) -> str:
        """Format quality assessment prompt"""
        return cls.QUALITY_ASSESSMENT.format(
            name=name,
            source=source,
            domain=domain,
            triple_count=triple_count,
            sample_classes=", ".join(sample_classes[:10]),
            sample_properties=", ".join(sample_properties[:10])
        )
