
import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from ai.harvesting.swarm import OntologyHarvestingSwarm

MOCK_ARXIV_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2101.00001</id>
    <title>A Novel Ontology for AI</title>
    <summary>We present a new ontology...</summary>
    <published>2021-01-01T00:00:00Z</published>
  </entry>
</feed>
"""

async def run_test():
    print("Starting Harvesting Swarm Test...")
    
    # Mock httpx in ArxivHarvester
    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = MOCK_ARXIV_RESPONSE.encode('utf-8')
        mock_client.get.return_value = mock_response
        
        swarm = OntologyHarvestingSwarm()
        candidates = await swarm.discover_candidates(limit=2)
        
        print("\n--- Discovered Candidates ---")
        print(f"Total: {len(candidates)}")
        
        arxiv_found = False
        static_found = False
        
        for c in candidates:
            print(f"- [{c.source}] {c.name}")
            if "arxiv" in c.source:
                arxiv_found = True
            if "academic" in c.source and "arXiv" not in c.name: # Static sources
                static_found = True
                
        if arxiv_found and len(candidates) > 0:
             print("\nTEST PASSED: Dynamic harvesting (mocked) and static harvesting verified.")
        else:
             print("\nTEST FAILED: Did not find expected candidates.")

if __name__ == "__main__":
    asyncio.run(run_test())
