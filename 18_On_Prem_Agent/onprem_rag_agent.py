"""On-Premises RAG Agent with Ollama and Qdrant

This module implements a fully on-premises Retrieval-Augmented Generation (RAG) agent using:
- Ollama for LLM inference (deepseek-r1:8b)
- Ollama for embeddings (mxbai-embed-large)
- Qdrant for vector storage (running via Docker)
- LangGraph for agent orchestration

No cloud APIs are used - everything runs locally on your machine.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Annotated, List, Literal

from langchain_community.document_loaders import DirectoryLoader, JSONLoader
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict


class AgentState(MessagesState):
    """State for the on-prem RAG agent."""
    pass


def load_and_index_documents(
    data_dir: str = "./data/data",
    qdrant_url: str = "127.0.0.1:6334",
    collection_name: str = "DnD_Documents"
) -> QdrantVectorStore:
    """Load JSON documents and create Qdrant vector store.

    Args:
        data_dir: Directory containing JSON files
        qdrant_url: Qdrant server URL
        collection_name: Name for the Qdrant collection

    Returns:
        QdrantVectorStore instance
    """
    print(f"Loading documents from {data_dir}...")

    # Load JSON documents
    json_loader = DirectoryLoader(
        path=data_dir,
        glob="**/*.json",
        loader_cls=JSONLoader,
        loader_kwargs={"jq_schema": "..", "text_content": False}
    )
    documents = json_loader.load()
    print(f"Loaded {len(documents)} documents")

    # Create embeddings using local Ollama model
    print("Creating embeddings with Ollama (mxbai-embed-large)...")
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    # Create Qdrant vector store
    print(f"Creating Qdrant vector store at {qdrant_url}...")
    print("NOTE: This may take several minutes for large datasets...")

    vectorstore = QdrantVectorStore.from_documents(
        documents,
        embeddings,
        url=qdrant_url,
        prefer_grpc=True,
        collection_name=collection_name,
    )

    print(f"Vector store created with collection '{collection_name}'")
    return vectorstore


def get_or_create_vectorstore(
    qdrant_url: str = "127.0.0.1:6334",
    collection_name: str = "DnD_Documents",
    recreate: bool = False
) -> QdrantVectorStore:
    """Get existing vectorstore or create a new one.

    Args:
        qdrant_url: Qdrant server URL
        collection_name: Name for the Qdrant collection
        recreate: If True, recreate the collection even if it exists

    Returns:
        QdrantVectorStore instance
    """
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    if recreate:
        print("Recreating vector store...")
        return load_and_index_documents(qdrant_url=qdrant_url, collection_name=collection_name)

    try:
        # Try to connect to existing collection
        print(f"Attempting to connect to existing collection '{collection_name}'...")
        vectorstore = QdrantVectorStore.from_existing_collection(
            embedding=embeddings,
            collection_name=collection_name,
            url=qdrant_url,
            prefer_grpc=True,
        )
        print(f"Connected to existing collection '{collection_name}'")
        return vectorstore
    except Exception as e:
        print(f"Collection not found or error connecting: {e}")
        print("Creating new vector store...")
        return load_and_index_documents(qdrant_url=qdrant_url, collection_name=collection_name)


@lru_cache(maxsize=1)
def _get_vectorstore():
    """Return a cached vectorstore instance."""
    qdrant_url = os.environ.get("QDRANT_URL", "127.0.0.1:6334")
    collection_name = os.environ.get("QDRANT_COLLECTION", "DnD_Documents")
    return get_or_create_vectorstore(qdrant_url=qdrant_url, collection_name=collection_name)


@tool
def retrieve_dnd_information(
    query: Annotated[str, "Search query for D&D feats and abilities"]
) -> str:
    """Search the D&D knowledge base for information about feats, abilities, and rules.

    This tool uses a local RAG system to find relevant information from the D&D dataset.
    """
    vectorstore = _get_vectorstore()

    # Retrieve relevant documents
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    docs = retriever.invoke(query)

    if not docs:
        return "No relevant information found in the D&D knowledge base."

    # Format the results
    context = "\n\n".join([f"Document {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs)])

    # Use local LLM to generate response
    llm = ChatOllama(model="deepseek-r1:8b", temperature=0.7)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful D&D assistant. Use the provided context to answer questions about D&D feats, abilities, and rules. Only use information from the context."),
        ("human", "Context:\n{context}\n\nQuestion: {query}\n\nProvide a clear and concise answer based only on the context above.")
    ])

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"context": context, "query": query})

    return response


def create_onprem_agent(
    model: str = "deepseek-r1:8b",
    temperature: float = 0.7
) -> "CompiledGraph":
    """Create an on-premises RAG agent using LangGraph.

    The agent has access to a RAG tool for retrieving D&D information.

    Args:
        model: Ollama model to use
        temperature: Temperature for generation

    Returns:
        Compiled LangGraph agent
    """
    # Initialize the LLM
    llm = ChatOllama(model=model, temperature=temperature)

    # Bind tools to the LLM
    tools = [retrieve_dnd_information]
    llm_with_tools = llm.bind_tools(tools)

    # Define agent node
    def agent_node(state: AgentState) -> AgentState:
        """Agent node that decides whether to use tools or respond."""
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    # Define routing function
    def should_continue(state: AgentState) -> Literal["tools", "end"]:
        """Determine if we should continue to tools or end."""
        last_message = state["messages"][-1]

        # If there are tool calls, continue to tools
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        # Otherwise, end
        return "end"

    # Build the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))

    # Add edges
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
        }
    )
    workflow.add_edge("tools", "agent")

    # Compile
    app = workflow.compile()
    print("On-premises RAG agent compiled successfully")

    return app


def chat_with_agent(agent: "CompiledGraph", message: str) -> str:
    """Send a message to the agent and get a response.

    Args:
        agent: Compiled agent graph
        message: User message

    Returns:
        Agent's response
    """
    result = agent.invoke({"messages": [HumanMessage(content=message)]})
    return result["messages"][-1].content


def main():
    """Main function to test the on-prem agent."""
    print("\n" + "="*80)
    print("ON-PREMISES RAG AGENT")
    print("="*80)
    print("\nThis agent runs completely on your local machine:")
    print("- LLM: Ollama (deepseek-r1:8b)")
    print("- Embeddings: Ollama (mxbai-embed-large)")
    print("- Vector Store: Qdrant (Docker)")
    print("- No cloud APIs required!")
    print("\n" + "="*80)

    # Check if Qdrant is running
    print("\nChecking Qdrant connection...")
    qdrant_url = os.environ.get("QDRANT_URL", "127.0.0.1:6334")

    try:
        # Try to get or create vectorstore
        print(f"Connecting to Qdrant at {qdrant_url}...")
        vectorstore = _get_vectorstore()
        print("✓ Qdrant connection successful")
    except Exception as e:
        print(f"\n✗ Error connecting to Qdrant: {e}")
        print("\nMake sure Qdrant is running via Docker:")
        print("  docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant")
        return

    # Create the agent
    print("\nCreating on-premises agent...")
    agent = create_onprem_agent()

    # Test queries
    test_queries = [
        "What are some feats that improve a character's strength?",
        "Tell me about feats related to magic or spellcasting",
        "What feats are good for a rogue character?"
    ]

    print("\n" + "="*80)
    print("TESTING AGENT")
    print("="*80)

    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"User: {query}")

        try:
            response = chat_with_agent(agent, query)
            print(f"\nAgent: {response}")
        except Exception as e:
            print(f"\nError: {e}")

        print("\n" + "-"*80)

    print("\n" + "="*80)
    print("ON-PREM AGENT TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
