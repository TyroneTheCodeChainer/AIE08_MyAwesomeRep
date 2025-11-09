"""Agentic RAG with Together AI Open Source Endpoints

This module implements a Retrieval-Augmented Generation (RAG) pipeline using Together AI's
open source endpoints instead of OpenAI. It follows the architecture from Sessions 14/15
but replaces the LLM and embedding models with Together AI alternatives.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Annotated, List

import tiktoken
from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain_community.vectorstores import Qdrant
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_together import ChatTogether, TogetherEmbeddings
from langgraph.graph import START, StateGraph
from typing_extensions import TypedDict


def _tiktoken_len(text: str) -> int:
    """Return token length using tiktoken for chunk length measurement."""
    tokens = tiktoken.encoding_for_model("gpt-4o").encode(text)
    return len(tokens)


class _RAGState(TypedDict):
    """State schema for the RAG graph: retrieve then generate."""
    question: str
    context: List[Document]
    response: str


def _build_rag_graph(
    data_dir: str,
    model_endpoint: str = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    embedding_model: str = "togethercomputer/m2-bert-80M-8k-retrieval"
) -> "CompiledGraph":
    """Construct and compile a RAG graph using Together AI endpoints.

    Args:
        data_dir: Directory containing PDF files to index
        model_endpoint: Together AI model endpoint for chat completions
        embedding_model: Together AI model for embeddings

    Steps:
        1) Load PDFs from data_dir recursively
        2) Split documents into token-aware chunks
        3) Create embeddings using Together AI and store in Qdrant
        4) Define chat prompt and Together AI generation model
        5) Wire a two-node graph: retrieve -> generate
    """
    # Load PDFs from data directory
    try:
        directory_loader = DirectoryLoader(
            data_dir, glob="**/*.pdf", loader_cls=PyMuPDFLoader
        )
        documents = directory_loader.load()
        print(f"Loaded {len(documents)} documents from {data_dir}")
    except Exception as e:
        print(f"Error loading documents: {e}")
        documents = []

    # Split documents into chunks
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except Exception:
        from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=750, chunk_overlap=100, length_function=_tiktoken_len
    )
    chunks = text_splitter.split_documents(documents) if documents else []
    print(f"Created {len(chunks)} chunks")

    # Create embeddings using Together AI
    embedding_function = TogetherEmbeddings(model=embedding_model)

    # Build Qdrant vector store (in-memory)
    qdrant_vectorstore = Qdrant.from_documents(
        documents=chunks,
        embedding=embedding_function,
        location=":memory:",
        collection_name="rag_documents"
    )
    retriever = qdrant_vectorstore.as_retriever(search_kwargs={"k": 5})
    print(f"Vector store created with {len(chunks)} chunks")

    # Set up prompt template
    human_template = (
        "\n#CONTEXT:\n{context}\n\nQUERY:\n{query}\n\n"
        "Use the provided context to answer the provided user query. "
        "Only use the provided context to answer the query. "
        "If you do not know the answer, or it's not contained in the "
        "provided context, respond with \"I don't know\""
    )
    chat_prompt = ChatPromptTemplate.from_messages([("human", human_template)])

    # Set up Together AI chat model
    generator_llm = ChatTogether(
        model=model_endpoint,
        temperature=0.7,
        max_tokens=512
    )

    # Define RAG graph nodes
    def retrieve(state: _RAGState) -> _RAGState:
        """Retrieve relevant documents based on the question."""
        retrieved_docs = retriever.invoke(state["question"]) if retriever else []
        print(f"Retrieved {len(retrieved_docs)} documents")
        return {"context": retrieved_docs}  # type: ignore

    def generate(state: _RAGState) -> _RAGState:
        """Generate response using retrieved context."""
        generator_chain = chat_prompt | generator_llm | StrOutputParser()
        response_text = generator_chain.invoke(
            {"query": state["question"], "context": state.get("context", [])}
        )
        return {"response": response_text}  # type: ignore

    # Build and compile the graph
    graph_builder = StateGraph(_RAGState)
    graph_builder = graph_builder.add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")

    compiled_graph = graph_builder.compile()
    print("RAG graph compiled successfully")

    return compiled_graph


@lru_cache(maxsize=1)
def _get_rag_graph():
    """Return a cached compiled RAG graph built from RAG_DATA_DIR."""
    data_dir = os.environ.get("RAG_DATA_DIR", "data")
    model_endpoint = os.environ.get("TOGETHER_MODEL_ENDPOINT", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
    return _build_rag_graph(data_dir, model_endpoint)


@tool
def retrieve_information(
    query: Annotated[str, "Query to ask the retrieve information tool"]
):
    """Use Retrieval Augmented Generation to retrieve information about how people are using AI in their daily work."""
    graph = _get_rag_graph()
    result = graph.invoke({"question": query})
    # Return the response string if available
    if isinstance(result, dict) and "response" in result:
        return result["response"]
    return result


def main():
    """Main function to test the RAG system."""
    import getpass

    # Set up API key if not already set
    if "TOGETHER_API_KEY" not in os.environ:
        os.environ["TOGETHER_API_KEY"] = getpass.getpass("Enter your Together API key: ")

    # Optional: Set custom model endpoint
    if "TOGETHER_MODEL_ENDPOINT" not in os.environ:
        print("\nUsing default model: meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo")
        print("To use a different model, set TOGETHER_MODEL_ENDPOINT environment variable")

    # Build the RAG graph
    print("\n=== Building RAG Graph ===")
    graph = _get_rag_graph()

    # Test queries
    test_queries = [
        "How are people using AI in their daily work?",
        "What are the main applications of AI mentioned in the document?",
        "What challenges do people face when using AI?"
    ]

    print("\n=== Testing RAG System ===")
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"Q: {query}")

        result = graph.invoke({"question": query})
        response = result.get("response", "No response generated")

        print(f"A: {response}")
        print("-" * 80)


if __name__ == "__main__":
    main()
