"""
Session 15 Activity #1: Simple Agent that uses A2A Protocol

This client agent demonstrates how to create an agent that communicates with
another agent through the A2A (Agent-to-Agent) protocol. The agent can make
API calls to the server agent and handle responses.
"""

import asyncio
import logging
from typing import Any
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleA2AClientAgent:
    """
    A simple agent that communicates with other agents using the A2A protocol.

    This agent can:
    - Discover and connect to A2A-compliant agents
    - Send queries and receive responses
    - Handle multi-turn conversations
    - Process streaming responses
    """

    def __init__(self, base_url: str = 'http://localhost:10000', timeout: float = 60.0):
        """
        Initialize the Simple A2A Client Agent.

        Args:
            base_url: The base URL of the A2A server agent
            timeout: Timeout for HTTP requests in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.httpx_client: httpx.AsyncClient | None = None
        self.client: A2AClient | None = None
        self.agent_card: AgentCard | None = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()

    async def connect(self) -> None:
        """
        Connect to the A2A server agent and fetch its agent card.

        The agent card contains metadata about the agent's capabilities,
        supported features, and API endpoints.
        """
        logger.info(f"🔌 Connecting to A2A agent at {self.base_url}")

        # Create HTTP client with extended timeout
        self.httpx_client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout)
        )

        # Initialize card resolver
        resolver = A2ACardResolver(
            httpx_client=self.httpx_client,
            base_url=self.base_url,
        )

        try:
            # Fetch the agent card
            logger.info("📋 Fetching agent card...")
            self.agent_card = await resolver.get_agent_card()

            logger.info("✅ Successfully fetched agent card:")
            logger.info(f"   Agent Name: {self.agent_card.name if hasattr(self.agent_card, 'name') else 'Unknown'}")
            logger.info(f"   Version: {self.agent_card.version if hasattr(self.agent_card, 'version') else 'Unknown'}")

            # Initialize A2A client
            self.client = A2AClient(
                httpx_client=self.httpx_client,
                agent_card=self.agent_card
            )

            logger.info("🤝 A2A Client initialized successfully!")

        except Exception as e:
            logger.error(f"❌ Failed to connect to agent: {e}")
            await self.disconnect()
            raise

    async def disconnect(self) -> None:
        """Disconnect from the A2A server agent and clean up resources"""
        if self.httpx_client:
            await self.httpx_client.aclose()
            logger.info("🔌 Disconnected from A2A agent")

    async def send_query(self, query: str, task_id: str | None = None, context_id: str | None = None) -> dict[str, Any]:
        """
        Send a query to the A2A agent and receive a response.

        Args:
            query: The question or prompt to send to the agent
            task_id: Optional task ID for multi-turn conversations
            context_id: Optional context ID for multi-turn conversations

        Returns:
            The agent's response as a dictionary
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Call connect() first.")

        logger.info(f"💬 Sending query: {query[:100]}...")

        # Construct the message payload
        message_data: dict[str, Any] = {
            'role': 'user',
            'parts': [
                {'kind': 'text', 'text': query}
            ],
            'message_id': uuid4().hex,
        }

        # Add task_id and context_id for multi-turn conversations
        if task_id:
            message_data['task_id'] = task_id
        if context_id:
            message_data['context_id'] = context_id

        # Create the request
        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(message=message_data)
        )

        # Send and receive response
        response = await self.client.send_message(request)

        logger.info(f"✅ Received response from agent")

        return response.model_dump(mode='json', exclude_none=True)

    async def multi_turn_conversation(self, queries: list[str]) -> list[dict[str, Any]]:
        """
        Have a multi-turn conversation with the agent.

        Args:
            queries: List of queries to send in sequence

        Returns:
            List of responses from the agent
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Call connect() first.")

        logger.info(f"🔄 Starting multi-turn conversation with {len(queries)} queries")

        responses = []
        task_id = None
        context_id = None

        for i, query in enumerate(queries, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Turn {i}/{len(queries)}")
            logger.info(f"{'='*60}")

            # Send query
            response = await self.send_query(query, task_id, context_id)
            responses.append(response)

            # Extract task_id and context_id for subsequent turns
            if i == 1 and 'root' in response and 'result' in response['root']:
                result = response['root']['result']
                task_id = result.get('id')
                context_id = result.get('context_id')
                logger.info(f"📍 Established conversation context (task_id: {task_id})")

        logger.info(f"\n✅ Multi-turn conversation complete!")
        return responses


async def demo_simple_agent():
    """
    Demonstration of the Simple A2A Client Agent

    This demo shows:
    1. Single-turn queries
    2. Multi-turn conversations
    3. Different types of queries (web search, academic, document-based)
    """
    print("\n" + "="*80)
    print("SESSION 15 ACTIVITY #1: SIMPLE A2A CLIENT AGENT DEMO")
    print("="*80)

    async with SimpleA2AClientAgent() as agent:
        # Test 1: Simple single-turn query
        print("\n📝 TEST 1: Single-Turn Query (Web Search)")
        print("-"*80)

        response1 = await agent.send_query(
            "What are the latest developments in artificial intelligence that you know about in 2025?"
        )

        print(f"\nResponse: {response1}")

        # Test 2: Academic query
        print("\n\n📝 TEST 2: Single-Turn Query (Academic Search)")
        print("-"*80)

        response2 = await agent.send_query(
            "Find recent papers about transformer architectures in machine learning"
        )

        print(f"\nResponse: {response2}")

        # Test 3: Multi-turn conversation
        print("\n\n📝 TEST 3: Multi-Turn Conversation")
        print("-"*80)

        conversation_queries = [
            "What are the key features of the GPT-4 architecture?",
            "How does it compare to earlier models like GPT-3?",
            "What are the practical applications of this technology?"
        ]

        conversation_responses = await agent.multi_turn_conversation(conversation_queries)

        print(f"\n✅ Multi-turn conversation completed with {len(conversation_responses)} exchanges")

        # Test 4: Document-based query (if RAG is configured)
        print("\n\n📝 TEST 4: Document-Based Query (RAG)")
        print("-"*80)

        response4 = await agent.send_query(
            "Based on the documents you have, what are the key policies or guidelines?"
        )

        print(f"\nResponse: {response4}")

    print("\n" + "="*80)
    print("🎉 DEMO COMPLETE!")
    print("="*80)

    print("\n💡 Key Takeaways:")
    print("   1. A2A protocol enables seamless agent-to-agent communication")
    print("   2. Agent cards provide discovery and capability information")
    print("   3. Multi-turn conversations maintain context automatically")
    print("   4. The protocol is flexible and supports various query types")
    print("   5. Agents can leverage different tools (web search, academic, RAG)")


async def targeted_demo():
    """
    A more targeted demo focusing on specific A2A features
    """
    print("\n" + "="*80)
    print("TARGETED A2A FEATURES DEMO")
    print("="*80)

    async with SimpleA2AClientAgent() as agent:
        # Feature 1: Agent Card Inspection
        print("\n🔍 FEATURE 1: Agent Card Inspection")
        print("-"*80)

        if agent.agent_card:
            card_dict = agent.agent_card.model_dump(exclude_none=True)
            print(f"Agent Card Details:")
            for key, value in card_dict.items():
                print(f"  {key}: {value}")

        # Feature 2: Async Communication
        print("\n\n⚡ FEATURE 2: Parallel Queries")
        print("-"*80)

        queries = [
            "What is machine learning?",
            "What is deep learning?",
            "What is natural language processing?"
        ]

        print("Sending multiple queries concurrently...")
        tasks = [agent.send_query(q) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                print(f"  Query {i}: ❌ Error - {result}")
            else:
                print(f"  Query {i}: ✅ Success")

        # Feature 3: Error Handling
        print("\n\n🛡️  FEATURE 3: Error Handling")
        print("-"*80)

        try:
            # Send a potentially problematic query
            response = await agent.send_query(
                "This is a very complex query with multiple parts that requires extensive tool usage"
            )
            print("  ✅ Query handled successfully")
        except Exception as e:
            print(f"  ⚠️  Caught exception: {e}")


if __name__ == "__main__":
    print("\n🤖 Simple A2A Client Agent")
    print("="*80)
    print("\nThis agent demonstrates the A2A protocol by communicating with")
    print("a running A2A server agent. Make sure the server is running at")
    print("http://localhost:10000 before starting this client.")
    print("\nTo start the server:")
    print("  uv run python -m app")
    print("\n" + "="*80)

    # Run the demo
    try:
        # Uncomment the demo you want to run:
        asyncio.run(demo_simple_agent())
        # asyncio.run(targeted_demo())
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()
