"""
OmniCore Platform v10 - SLM Service
High-level service for ontology-specific SLM operations
"""

import json
import re
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from common.config import get_settings
from common.logging_config import get_logger
from common.models import (
    SLMRequest, SLMResponse, SLMEnhancement,
    RootType, CausalityType, EpistemicBasis,
    AIAgentRole, DebateRound, DebateResult, Conflict
)
from .client import SLMClient, get_slm_client
from .prompts import PromptTemplates

logger = get_logger("slm.service")


class SLMService:
    """
    High-level SLM Service for OmniCore v10

    Provides specialized methods for:
    - Root type inference
    - Causality extraction
    - Epistemic annotation
    - Conflict resolution via AI debate
    - Strategic planning
    """

    def __init__(self, client: Optional[SLMClient] = None):
        self.client = client or get_slm_client()
        self.settings = get_settings()

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from SLM response, handling markdown code blocks"""
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
        if json_match:
            response = json_match.group(1)

        # Try direct JSON parsing
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON object in response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass

        logger.warning("Failed to parse JSON from SLM response")
        return {}

    # ==========================================================================
    # Root Type Inference
    # ==========================================================================

    async def infer_root_type(
        self,
        entity_name: str,
        description: str = "",
        context: str = "",
        source: str = ""
    ) -> Tuple[RootType, float, str]:
        """
        Infer root type for an entity using SLM.

        Returns:
            Tuple of (root_type, confidence, reasoning)
        """
        prompt = PromptTemplates.get_root_mapping_prompt(
            entity_name=entity_name,
            description=description,
            context=context,
            source=source
        )

        request = SLMRequest(
            prompt=prompt,
            task_type="root_mapping",
            max_tokens=512,
            temperature=0.1
        )

        response = await self.client.generate(request)
        parsed = self._parse_json_response(response.response)

        # Extract and validate root type
        root_type_str = parsed.get("root_type", "ABSTRACT").upper()
        try:
            root_type = RootType(root_type_str)
        except ValueError:
            root_type = RootType.ABSTRACT
            logger.warning(f"Invalid root type '{root_type_str}', defaulting to ABSTRACT")

        confidence = parsed.get("confidence", response.confidence)
        reasoning = parsed.get("reasoning", "Inferred by SLM")

        return root_type, confidence, reasoning

    async def batch_infer_root_types(
        self,
        entities: List[Dict[str, str]]
    ) -> List[Tuple[str, RootType, float, str]]:
        """
        Batch infer root types for multiple entities.

        Args:
            entities: List of dicts with 'name', 'description', 'context', 'source'

        Returns:
            List of (entity_name, root_type, confidence, reasoning)
        """
        results = []
        for entity in entities:
            root_type, confidence, reasoning = await self.infer_root_type(
                entity_name=entity.get("name", ""),
                description=entity.get("description", ""),
                context=entity.get("context", ""),
                source=entity.get("source", "")
            )
            results.append((entity.get("name", ""), root_type, confidence, reasoning))
        return results

    # ==========================================================================
    # Causality Extraction
    # ==========================================================================

    async def extract_causality(
        self,
        entities: List[str],
        descriptions: List[str],
        context: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Extract implicit causal relationships using SLM.

        Returns:
            List of causal relationship dicts
        """
        prompt = PromptTemplates.get_causality_prompt(
            entities=entities,
            descriptions=descriptions,
            context=context
        )

        request = SLMRequest(
            prompt=prompt,
            task_type="causality",
            max_tokens=1024,
            temperature=0.1
        )

        response = await self.client.generate(request)
        parsed = self._parse_json_response(response.response)

        relationships = parsed.get("relationships", [])

        # Validate causality types
        validated = []
        for rel in relationships:
            causality_type = rel.get("causality_type", "EFFICIENT").upper()
            try:
                CausalityType(causality_type)
                validated.append(rel)
            except ValueError:
                logger.warning(f"Invalid causality type '{causality_type}', skipping")

        return validated

    # ==========================================================================
    # Epistemic Annotation
    # ==========================================================================

    async def generate_epistemic_annotation(
        self,
        entity_name: str,
        claim: str,
        source: str = "",
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Generate epistemic annotation for a claim using SLM.

        Returns:
            Dict with certainty, basis, reasoning
        """
        prompt = PromptTemplates.get_epistemic_prompt(
            entity_name=entity_name,
            claim=claim,
            source=source,
            context=context
        )

        request = SLMRequest(
            prompt=prompt,
            task_type="epistemic",
            max_tokens=512,
            temperature=0.1
        )

        response = await self.client.generate(request)
        parsed = self._parse_json_response(response.response)

        # Validate basis
        basis_str = parsed.get("basis", "speculative").lower()
        try:
            EpistemicBasis(basis_str)
        except ValueError:
            basis_str = "speculative"

        return {
            "certainty": min(1.0, max(0.0, parsed.get("certainty", 0.5))),
            "basis": basis_str,
            "reasoning": parsed.get("reasoning", ""),
            "supporting_evidence": parsed.get("supporting_evidence", []),
            "source_reliability": parsed.get("source_reliability", 0.5)
        }

    # ==========================================================================
    # Conflict Resolution via AI Debate
    # ==========================================================================

    async def resolve_conflict_via_debate(
        self,
        conflict: Conflict,
        max_rounds: int = 5
    ) -> DebateResult:
        """
        Resolve ontological conflict via multi-agent AI debate.

        v10 Protocol:
        - 5 rounds, turn-based
        - Roles: Platonist, Nominalist, Pragmatist
        - Moderator synthesizes and checks consensus
        - Consensus threshold: 75% (3/4 agents agree)
        """
        rounds: List[DebateRound] = []
        all_arguments = ""
        consensus_threshold = self.settings.conflict_consensus_threshold

        roles = [AIAgentRole.PLATONIST, AIAgentRole.NOMINALIST, AIAgentRole.PRAGMATIST]

        # Conduct debate rounds
        for round_num in range(1, max_rounds + 1):
            for role in roles:
                prompt = PromptTemplates.get_debate_prompt(
                    role=role.value,
                    conflict_type=conflict.conflict_type.value,
                    entity_a=conflict.entity_a,
                    entity_b=conflict.entity_b,
                    description=conflict.description,
                    previous_arguments=all_arguments
                )

                request = SLMRequest(
                    prompt=prompt,
                    task_type="conflict",
                    max_tokens=self.settings.conflict_max_tokens_per_turn,
                    temperature=0.3
                )

                response = await self.client.generate(request)
                parsed = self._parse_json_response(response.response)

                round_entry = DebateRound(
                    round_number=round_num,
                    agent_role=role,
                    argument=parsed.get("argument", response.response[:500]),
                    confidence=parsed.get("confidence", response.confidence),
                    supporting_evidence=parsed.get("supporting_evidence", [])
                )
                rounds.append(round_entry)

                all_arguments += f"\n[{role.value.upper()} Round {round_num}]: {round_entry.argument}\n"

        # Moderator synthesizes
        moderator_prompt = PromptTemplates.get_debate_prompt(
            role="moderator",
            conflict_type=conflict.conflict_type.value,
            entity_a=conflict.entity_a,
            entity_b=conflict.entity_b,
            description=conflict.description,
            all_arguments=all_arguments,
            threshold=consensus_threshold
        )

        request = SLMRequest(
            prompt=moderator_prompt,
            task_type="conflict",
            max_tokens=1024,
            temperature=0.2
        )

        response = await self.client.generate(request)
        synthesis = self._parse_json_response(response.response)

        # Determine consensus
        consensus_reached = synthesis.get("consensus_reached", False)
        consensus_pct = synthesis.get("consensus_percentage", 0.0)

        if consensus_pct >= consensus_threshold:
            consensus_reached = True

        # Build result
        supporting_roles = []
        for role_str in synthesis.get("supporting_agents", []):
            try:
                supporting_roles.append(AIAgentRole(role_str.lower()))
            except ValueError:
                pass

        return DebateResult(
            conflict_id=conflict.id,
            rounds=rounds,
            consensus_reached=consensus_reached,
            consensus_threshold=consensus_threshold,
            final_resolution=synthesis.get("final_resolution", "No resolution reached"),
            supporting_agents=supporting_roles,
            contextual_axiom=synthesis.get("contextual_axiom")
        )

    # ==========================================================================
    # Strategic Planning
    # ==========================================================================

    async def generate_strategic_plan(
        self,
        metrics: Dict[str, float],
        gaps: List[str]
    ) -> Dict[str, Any]:
        """
        Generate strategic plan for quarterly review.

        v10 Phase 5: Full autonomy with human oversight for critical changes
        """
        targets = {
            "ontology_coverage": 1000,
            "mmo_accuracy": 0.90,
            "ai_task_success": 0.92,
            "human_intervention": 20
        }

        prompt = PromptTemplates.get_strategic_prompt(
            metrics=metrics,
            gaps=gaps,
            targets=targets
        )

        request = SLMRequest(
            prompt=prompt,
            task_type="general",
            max_tokens=1024,
            temperature=0.3
        )

        response = await self.client.generate(request)
        plan = self._parse_json_response(response.response)

        # v10 Safety: Check if plan affects root types or causality
        actions = plan.get("actions", [])
        requires_approval = plan.get("requires_human_approval", False)

        for action in actions:
            action_lower = action.lower()
            if any(term in action_lower for term in ["root", "causality", "mmo weight"]):
                requires_approval = True
                break

        plan["requires_human_approval"] = requires_approval

        return plan

    # ==========================================================================
    # Ontology Quality Assessment
    # ==========================================================================

    async def assess_ontology_quality(
        self,
        name: str,
        source: str,
        domain: str,
        triple_count: int,
        sample_classes: List[str],
        sample_properties: List[str]
    ) -> Dict[str, Any]:
        """
        Assess quality of an ontology for integration.

        Returns quality scores and recommendation
        """
        prompt = PromptTemplates.get_quality_prompt(
            name=name,
            source=source,
            domain=domain,
            triple_count=triple_count,
            sample_classes=sample_classes,
            sample_properties=sample_properties
        )

        request = SLMRequest(
            prompt=prompt,
            task_type="general",
            max_tokens=1024,
            temperature=0.1
        )

        response = await self.client.generate(request)
        assessment = self._parse_json_response(response.response)

        # Ensure valid recommendation
        recommendation = assessment.get("recommendation", "review").lower()
        if recommendation not in ["integrate", "review", "reject"]:
            recommendation = "review"

        assessment["recommendation"] = recommendation

        return assessment

    # ==========================================================================
    # Entity Enhancement
    # ==========================================================================

    async def enhance_entity(
        self,
        entity_id: str,
        entity_name: str,
        entity_description: str,
        enhancement_types: List[str] = None
    ) -> List[SLMEnhancement]:
        """
        Enhance an entity with SLM-derived insights.

        Enhancement types: root_hint, causality, epistemic
        """
        if enhancement_types is None:
            enhancement_types = ["root_hint", "causality", "epistemic"]

        enhancements = []

        for etype in enhancement_types:
            if etype == "root_hint":
                root_type, confidence, reasoning = await self.infer_root_type(
                    entity_name=entity_name,
                    description=entity_description
                )
                enhancements.append(SLMEnhancement(
                    entity_id=entity_id,
                    enhancement_type="root_hint",
                    original_value=None,
                    enhanced_value=root_type.value,
                    confidence=confidence,
                    rationale=reasoning,
                    model_id=self.settings.slm_model_name
                ))

            elif etype == "epistemic":
                annotation = await self.generate_epistemic_annotation(
                    entity_name=entity_name,
                    claim=entity_description
                )
                enhancements.append(SLMEnhancement(
                    entity_id=entity_id,
                    enhancement_type="epistemic",
                    original_value=None,
                    enhanced_value=f"certainty={annotation['certainty']}, basis={annotation['basis']}",
                    confidence=annotation['certainty'],
                    rationale=annotation['reasoning'],
                    model_id=self.settings.slm_model_name
                ))

        return enhancements
