
import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from common.models import Conflict, ConflictType, SLMResponse, AIAgentRole
from ai.slm.debate import ConflictDebate
from ai.slm import debate

# Mock SLM Client
class MockSLMClient:
    async def generate(self, request):
        prompt = request.prompt
        
        # Detect role based on prompt content
        if "You are a PLATONIST" in prompt:
            return SLMResponse(
                response='{"argument": "The number 2 exists independently of physical objects.", "confidence": 0.9}',
                model_used="mock-model",
                confidence=0.9,
                tokens_used=10,
                latency_ms=10
            )
        elif "You are a NOMINALIST" in prompt:
             return SLMResponse(
                response='{"argument": "Numbers are just names we give to collections.", "confidence": 0.85}',
                model_used="mock-model",
                confidence=0.85,
                tokens_used=10,
                latency_ms=10
            )
        elif "You are a PRAGMATIST" in prompt:
             return SLMResponse(
                response='{"argument": "It is useful to treat numbers as real for math.", "confidence": 0.88}',
                model_used="mock-model",
                confidence=0.88,
                tokens_used=10,
                latency_ms=10
            )
        elif "You are the MODERATOR" in prompt:
             return SLMResponse(
                response='{"consensus_reached": true, "consensus_percentage": 0.8, "final_resolution": "Treat as ABSTRACT for utility.", "supporting_agents": ["Platonist", "Pragmatist"]}',
                model_used="mock-model",
                confidence=0.95,
                tokens_used=10,
                latency_ms=10
            )
        else:
            return SLMResponse(
                response="Generic response",
                model_used="mock-model",
                confidence=0.5,
                tokens_used=10,
                latency_ms=10
            )
            
    async def health_check(self, timeout_seconds=1.0):
        return {"mock": True}

# Patch get_slm_client
debate.get_slm_client = lambda: MockSLMClient()

async def run_test():
    print("Starting Debate Protocol Test...")
    
    conflict = Conflict(
        id="test-conflict-1",
        conflict_type=ConflictType.ROOT_DISAGREEMENT,
        entity_a="The Number 2",
        entity_b="Abstract Object",
        description="Is the number 2 an extant object or an abstract object?",
        severity=0.5,
        resolved=False
    )
    
    debater = ConflictDebate()
    result = await debater.run_debate(conflict, max_rounds=1)
    
    print("\n--- Debate Result ---")
    print(f"Consensus Reached: {result.consensus_reached}")
    print(f"Final Resolution: {result.final_resolution}")
    print(f"Supporting Agents: {result.supporting_agents}")
    print(f"Rounds: {len(result.rounds)}")
    
    for r in result.rounds:
        print(f"  [{r.agent_role.value}]: {r.argument}")
        
    if result.consensus_reached and len(result.rounds) == 3:
        print("\nTEST PASSED: Debate logic flow verified.")
    else:
        print("\nTEST FAILED: Unexpected result structure.")

if __name__ == "__main__":
    asyncio.run(run_test())
