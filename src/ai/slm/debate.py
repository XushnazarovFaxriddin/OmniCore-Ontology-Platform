"""
OmniCore Platform v10 - AI Debate Protocol
Implements the multi-agent debate for conflict resolution.
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from common.logging_config import get_logger
from common.models import (
    AIAgentRole, DebateRound, DebateResult, Conflict, ConflictType, 
    SLMRequest
)
from .client import get_slm_client
from .prompts import PromptTemplates

logger = get_logger("ai.debate")

@dataclass
class DebateAgent:
    """
    AI Agent participating in the debate.
    Injects specific philosophical persona (Platonist, Nominalist, Pragmatist).
    """
    role: AIAgentRole
    persona_description: str
    
    async def generate_argument(
        self, 
        conflict: Conflict, 
        round_num: int, 
        previous_arguments: str
    ) -> DebateRound:
        """
        Generate an argument based on the agent's persona and current debate state.
        """
        client = get_slm_client()
        
        prompt = PromptTemplates.get_debate_prompt(
            role=self.role.value,
            conflict_type=conflict.conflict_type.value,
            entity_a=conflict.entity_a,
            entity_b=conflict.entity_b,
            description=conflict.description,
            previous_arguments=previous_arguments
        )

        request = SLMRequest(
            prompt=prompt,
            task_type="conflict",
            max_tokens=512,  # Configurable in settings
            temperature=0.3
        )

        response = await client.generate(request)
        
        # Simple parsing logic (in production, use robust JSON parsing/repair)
        # Assuming the SLM prompt instructs to return JSON or structured text
        # For this implementation, we rely on the prompt to give us the argument text directly 
        # or we wrap it.
        
        # NOTE: In v10 spec, the prompt template returns JSON with 'argument', 'confidence'.
        # We need to parse that here.
        import json
        import re
        
        content = response.response
        parsed = {}
        
        try:
            # Try to find JSON block
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            if json_match:
                parsed = json.loads(json_match.group(1))
            else:
                # Try direct parse
                parsed = json.loads(content)
        except Exception:
            # Fallback if no JSON
            parsed = {"argument": content, "confidence": response.confidence}

        return DebateRound(
            round_number=round_num,
            agent_role=self.role,
            argument=parsed.get("argument", content),
            confidence=float(parsed.get("confidence", response.confidence)),
            supporting_evidence=parsed.get("supporting_evidence", [])
        )

class ConflictDebate:
    """
    Orchestrates the 5-round debate protocol between agents.
    """
    
    def __init__(self):
        self.agents = [
            DebateAgent(
                role=AIAgentRole.PLATONIST,
                persona_description="Believes in independent abstract forms. Prefers ABSTRACT root type."
            ),
            DebateAgent(
                role=AIAgentRole.NOMINALIST,
                persona_description="Believes only particulars exist. Prefers EXTANT root type."
            ),
            DebateAgent(
                role=AIAgentRole.PRAGMATIST,
                persona_description="Focuses on utility and context. Flexible classification."
            )
        ]
        
    async def run_debate(
        self, 
        conflict: Conflict, 
        max_rounds: int = 5,
        consensus_threshold: float = 0.75
    ) -> DebateResult:
        """
        Run the debate protocol.
        """
        logger.info(f"Starting debate for conflict {conflict.id} ({conflict.entity_a} vs {conflict.entity_b})")
        
        rounds: List[DebateRound] = []
        all_arguments_history = ""
        
        # Run rounds
        for round_num in range(1, max_rounds + 1):
            logger.debug(f"Debate Round {round_num}")
            
            # Gather arguments from all agents for this round
            # Could be done in parallel
            round_tasks = [
                agent.generate_argument(conflict, round_num, all_arguments_history)
                for agent in self.agents
            ]
            
            round_results = await asyncio.gather(*round_tasks)
            
            for res in round_results:
                rounds.append(res)
                all_arguments_history += f"\n[{res.agent_role.value.upper()} Round {round_num}]: {res.argument}\n"
                
        # Moderator Synthesis
        final_result = await self._synthesize_result(
            conflict, 
            all_arguments_history, 
            consensus_threshold,
            rounds
        )
        
        return final_result

    async def _synthesize_result(
        self,
        conflict: Conflict,
        all_arguments: str,
        threshold: float,
        rounds: List[DebateRound]
    ) -> DebateResult:
        """
        Use the SLM as a moderator to synthesize the debate and determine consensus.
        """
        client = get_slm_client()
        
        moderator_prompt = PromptTemplates.get_debate_prompt(
            role="moderator",
            conflict_type=conflict.conflict_type.value,
            entity_a=conflict.entity_a,
            entity_b=conflict.entity_b,
            description=conflict.description,
            all_arguments=all_arguments,
            threshold=threshold
        )
        
        request = SLMRequest(
            prompt=moderator_prompt,
            task_type="conflict",
            max_tokens=1024,
            temperature=0.2
        )
        
        response = await client.generate(request)
        
        # Parse result
        import json
        import re
        content = response.response
        parsed = {}
        
        try:
             # Try to find JSON block
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            if json_match:
                parsed = json.loads(json_match.group(1))
            else:
                parsed = json.loads(content)
        except Exception as e:
            logger.error(f"Failed to parse moderator response: {e}")
            parsed = {
                "consensus_reached": False,
                "final_resolution": "Failed to synthesize debate.",
                "supporting_agents": [],
                "consensus_percentage": 0.0
            }

        # Validate supporting agents
        supporting_roles = []
        for role_str in parsed.get("supporting_agents", []):
            try:
                supporting_roles.append(AIAgentRole(role_str.lower()))
            except ValueError:
                pass
                
        return DebateResult(
            conflict_id=conflict.id,
            rounds=rounds,
            consensus_reached=parsed.get("consensus_reached", False),
            consensus_threshold=threshold,
            final_resolution=parsed.get("final_resolution", "No resolution reached"),
            supporting_agents=supporting_roles,
            contextual_axiom=parsed.get("contextual_axiom")
        )
