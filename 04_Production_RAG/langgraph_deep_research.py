"""
Session 04: LangGraph Deep Research System
==========================================

This module implements a production-ready Deep Research system using LangGraph,
aligning with the AI MakerSpace curriculum requirements for advanced RAG
applications with multi-agent workflows and cyclic reasoning.

INDUSTRY ALIGNMENT:
- Implements the "Deep Research" use case that every major AI company has released in 2025
- Uses LangGraph for stateful, cyclic workflows
- Demonstrates multi-agent reasoning and autonomous exploration
- Aligns with OpenAI's Six Use Case Primitives (Research category)

TECHNICAL ARCHITECTURE:
- LangGraph for complex workflow orchestration
- Multi-agent system with specialized roles
- Cyclic reasoning for iterative research
- Integration with LangSmith for evaluation
- Support for both OpenAI and OSS models
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, TypedDict, Annotated
from dataclasses import dataclass
from enum import Enum

# LangChain Core
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain_core.documents import Document

# LangChain Components
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.retrievers import BaseRetriever
from langchain_community.llms import Ollama

# LangGraph
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# LangSmith
from langsmith import Client
from langchain_core.tracers import LangChainTracer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResearchState(TypedDict):
    """State object for the Deep Research workflow."""
    messages: Annotated[List[BaseMessage], add_messages]
    query: str
    research_plan: Dict[str, Any]
    search_results: List[Dict[str, Any]]
    analysis_results: List[Dict[str, Any]]
    synthesis: Dict[str, Any]
    final_report: str
    current_phase: str
    iteration_count: int
    max_iterations: int
    research_complete: bool

class ResearchPhase(Enum):
    """Phases of the Deep Research process."""
    PLANNING = "planning"
    SEARCHING = "searching"
    ANALYZING = "analyzing"
    SYNTHESIZING = "synthesizing"
    REPORTING = "reporting"
    ITERATING = "iterating"

class DeepResearchLangGraph:
    """
    Production-ready Deep Research system using LangGraph.
    
    This system implements the industry-standard Deep Research capabilities
    with multi-agent workflows, cyclic reasoning, and comprehensive evaluation.
    """
    
    def __init__(self, 
                 openai_api_key: str = None,
                 langsmith_api_key: str = None,
                 ollama_base_url: str = "http://localhost:11434",
                 project_name: str = "deep-research-langgraph"):
        """Initialize the Deep Research LangGraph system."""
        self.openai_api_key = openai_api_key
        self.langsmith_api_key = langsmith_api_key
        self.ollama_base_url = ollama_base_url
        
        # Initialize LangSmith client
        if langsmith_api_key:
            self.langsmith_client = Client(api_key=langsmith_api_key)
            self.tracer = LangChainTracer(project_name=project_name)
        else:
            self.langsmith_client = None
            self.tracer = None
        
        # Initialize models (only if API key provided)
        if openai_api_key:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=openai_api_key,
                temperature=0.3
            )
        else:
            self.llm = None
        
        # Initialize embeddings (only if API key provided)
        if openai_api_key:
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                api_key=openai_api_key
            )
        else:
            self.embeddings = None
        
        # Initialize vector store (only if embeddings available)
        if self.embeddings:
            self.vectorstore = Chroma(
                embedding_function=self.embeddings,
                persist_directory="./chroma_db"
            )
        else:
            self.vectorstore = None
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Build the LangGraph workflow
        self.graph = self._build_graph()
        
        # Research history
        self.research_history = []
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for Deep Research."""
        
        # Create the state graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes for each phase
        workflow.add_node("planner", self._planning_node)
        workflow.add_node("searcher", self._searching_node)
        workflow.add_node("analyzer", self._analyzing_node)
        workflow.add_node("synthesizer", self._synthesizing_node)
        workflow.add_node("reporter", self._reporting_node)
        workflow.add_node("iterator", self._iterating_node)
        
        # Define the workflow edges
        workflow.set_entry_point("planner")
        
        # Planning -> Searching
        workflow.add_edge("planner", "searcher")
        
        # Searching -> Analyzing
        workflow.add_edge("searcher", "analyzer")
        
        # Analyzing -> Synthesizing
        workflow.add_edge("analyzer", "synthesizer")
        
        # Synthesizing -> Reporting
        workflow.add_edge("synthesizer", "reporter")
        
        # Reporter -> Iterator (for potential iterations)
        workflow.add_conditional_edges(
            "reporter",
            self._should_iterate,
            {
                "iterate": "iterator",
                "complete": END
            }
        )
        
        # Iterator -> Searching (for additional research)
        workflow.add_edge("iterator", "searcher")
        
        # Compile the graph
        return workflow.compile(checkpointer=MemorySaver())
    
    async def _planning_node(self, state: ResearchState) -> ResearchState:
        """Planning phase: Create comprehensive research plan."""
        logger.info("Executing planning phase")
        
        query = state["query"]
        
        planning_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Research Planner. Your role is to create comprehensive research plans for complex queries.

Your task is to:
1. Break down the query into specific research sub-questions
2. Identify key areas to investigate
3. Suggest search strategies and sources
4. Create a structured research approach
5. Estimate the scope and complexity

Provide your response as a JSON object with:
- sub_questions: List of specific questions to research
- key_areas: List of main topics to investigate
- search_strategies: List of search approaches
- sources_to_check: List of recommended source types
- estimated_complexity: Low/Medium/High
- research_depth: Surface/Deep/Comprehensive"""),
            ("human", f"Create a research plan for: {query}")
        ])
        
        planning_chain = planning_prompt | self.llm | StrOutputParser()
        
        try:
            plan_response = await planning_chain.ainvoke({"query": query})
            research_plan = json.loads(plan_response)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            research_plan = {
                "sub_questions": [query],
                "key_areas": ["general information"],
                "search_strategies": ["web search", "academic sources"],
                "sources_to_check": ["websites", "papers", "reports"],
                "estimated_complexity": "Medium",
                "research_depth": "Deep"
            }
        
        # Update state
        state["research_plan"] = research_plan
        state["current_phase"] = ResearchPhase.PLANNING.value
        state["messages"].append(AIMessage(content=f"Research plan created: {json.dumps(research_plan, indent=2)}"))
        
        return state
    
    async def _searching_node(self, state: ResearchState) -> ResearchState:
        """Searching phase: Gather information from various sources."""
        logger.info("Executing searching phase")
        
        query = state["query"]
        research_plan = state.get("research_plan", {})
        
        # Simulate web search (in production, integrate with real search APIs)
        search_results = await self._simulate_web_search(query, research_plan)
        
        # Process and store documents
        documents = []
        for result in search_results:
            doc = Document(
                page_content=result["content"],
                metadata={
                    "title": result["title"],
                    "url": result["url"],
                    "source_type": result["source_type"],
                    "relevance_score": result["relevance_score"]
                }
            )
            documents.append(doc)
        
        # Add to vector store
        if documents:
            self.vectorstore.add_documents(documents)
        
        # Update state
        state["search_results"] = search_results
        state["current_phase"] = ResearchPhase.SEARCHING.value
        state["messages"].append(AIMessage(content=f"Found {len(search_results)} relevant sources"))
        
        return state
    
    async def _analyzing_node(self, state: ResearchState) -> ResearchState:
        """Analyzing phase: Analyze gathered information."""
        logger.info("Executing analyzing phase")
        
        query = state["query"]
        search_results = state.get("search_results", [])
        
        # Retrieve relevant documents
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})
        relevant_docs = retriever.get_relevant_documents(query)
        
        # Create analysis prompt
        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Research Analyst. Your role is to analyze information sources and extract key insights.

Your analysis should:
1. Evaluate the credibility and relevance of each source
2. Identify key facts and insights
3. Note any contradictions or gaps
4. Assess the overall quality of information gathered
5. Extract actionable insights

Provide your analysis as a structured JSON response with:
- source_evaluations: List of evaluations for each source
- key_facts: List of important facts discovered
- insights: List of key insights
- contradictions: List of any contradictory information
- gaps: List of information gaps identified
- overall_quality: Assessment of information quality"""),
            ("human", f"""Analyze the following sources for the query: {query}

Sources:
{json.dumps([{"title": s["title"], "content": s["content"][:500]} for s in search_results], indent=2)}

Relevant Documents:
{json.dumps([{"content": doc.page_content[:500], "metadata": doc.metadata} for doc in relevant_docs], indent=2)}""")
        ])
        
        analysis_chain = analysis_prompt | self.llm | StrOutputParser()
        
        try:
            analysis_response = await analysis_chain.ainvoke({
                "query": query,
                "search_results": search_results,
                "relevant_docs": relevant_docs
            })
            analysis_results = json.loads(analysis_response)
        except json.JSONDecodeError:
            analysis_results = {
                "source_evaluations": [],
                "key_facts": ["Analysis failed to parse"],
                "insights": ["Unable to extract insights"],
                "contradictions": [],
                "gaps": ["Analysis incomplete"],
                "overall_quality": "Unknown"
            }
        
        # Update state
        state["analysis_results"] = analysis_results
        state["current_phase"] = ResearchPhase.ANALYZING.value
        state["messages"].append(AIMessage(content=f"Analysis completed: {len(analysis_results.get('key_facts', []))} key facts identified"))
        
        return state
    
    async def _synthesizing_node(self, state: ResearchState) -> ResearchState:
        """Synthesizing phase: Synthesize findings into insights."""
        logger.info("Executing synthesizing phase")
        
        query = state["query"]
        analysis_results = state.get("analysis_results", {})
        research_plan = state.get("research_plan", {})
        
        synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an Information Synthesizer. Your role is to synthesize research findings into coherent insights.

Your synthesis should:
1. Identify patterns and connections across sources
2. Generate key insights and conclusions
3. Highlight important implications
4. Note areas requiring further research
5. Create a coherent narrative from the findings

Provide a comprehensive synthesis as a structured JSON response with:
- key_insights: List of main insights discovered
- patterns: List of patterns identified across sources
- implications: List of important implications
- recommendations: List of actionable recommendations
- further_research: List of areas needing more research
- confidence_level: High/Medium/Low confidence in findings"""),
            ("human", f"""Synthesize the research findings for: {query}

Research Plan:
{json.dumps(research_plan, indent=2)}

Analysis Results:
{json.dumps(analysis_results, indent=2)}""")
        ])
        
        synthesis_chain = synthesis_prompt | self.llm | StrOutputParser()
        
        try:
            synthesis_response = await synthesis_chain.ainvoke({
                "query": query,
                "research_plan": research_plan,
                "analysis_results": analysis_results
            })
            synthesis = json.loads(synthesis_response)
        except json.JSONDecodeError:
            synthesis = {
                "key_insights": ["Synthesis failed to parse"],
                "patterns": [],
                "implications": [],
                "recommendations": [],
                "further_research": [],
                "confidence_level": "Low"
            }
        
        # Update state
        state["synthesis"] = synthesis
        state["current_phase"] = ResearchPhase.SYNTHESIZING.value
        state["messages"].append(AIMessage(content=f"Synthesis completed: {len(synthesis.get('key_insights', []))} insights generated"))
        
        return state
    
    async def _reporting_node(self, state: ResearchState) -> ResearchState:
        """Reporting phase: Generate comprehensive research report."""
        logger.info("Executing reporting phase")
        
        query = state["query"]
        research_plan = state.get("research_plan", {})
        analysis_results = state.get("analysis_results", {})
        synthesis = state.get("synthesis", {})
        
        reporting_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Report Generator. Your role is to create comprehensive research reports.

Create a professional research report with:
1. Executive Summary
2. Key Findings
3. Detailed Analysis
4. Conclusions and Recommendations
5. Sources and Citations
6. Areas for Further Research

Format the report in clear, professional language suitable for business use.
Use proper markdown formatting for structure and readability."""),
            ("human", f"""Create a comprehensive research report for: {query}

Research Plan:
{json.dumps(research_plan, indent=2)}

Analysis Results:
{json.dumps(analysis_results, indent=2)}

Synthesis:
{json.dumps(synthesis, indent=2)}""")
        ])
        
        reporting_chain = reporting_prompt | self.llm | StrOutputParser()
        
        try:
            final_report = await reporting_chain.ainvoke({
                "query": query,
                "research_plan": research_plan,
                "analysis_results": analysis_results,
                "synthesis": synthesis
            })
        except Exception as e:
            final_report = f"Report generation failed: {str(e)}"
        
        # Update state
        state["final_report"] = final_report
        state["current_phase"] = ResearchPhase.REPORTING.value
        state["messages"].append(AIMessage(content=f"Final report generated: {len(final_report)} characters"))
        
        return state
    
    async def _iterating_node(self, state: ResearchState) -> ResearchState:
        """Iterating phase: Determine if additional research is needed."""
        logger.info("Executing iterating phase")
        
        query = state["query"]
        synthesis = state.get("synthesis", {})
        iteration_count = state.get("iteration_count", 0)
        max_iterations = state.get("max_iterations", 3)
        
        # Check if we need more iterations
        if iteration_count >= max_iterations:
            state["research_complete"] = True
            state["current_phase"] = ResearchPhase.REPORTING.value
            return state
        
        # Determine if additional research is needed
        iteration_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Research Coordinator. Determine if additional research is needed.

Consider:
1. Are there significant gaps in the current findings?
2. Are there contradictory or unclear information?
3. Would additional sources provide valuable insights?
4. Is the current research sufficient for the query?

Respond with JSON:
- needs_more_research: true/false
- reasoning: explanation of decision
- additional_queries: list of specific queries to research further"""),
            ("human", f"""Current research iteration: {iteration_count + 1}

Query: {query}

Current Synthesis:
{json.dumps(synthesis, indent=2)}

Should we conduct additional research?""")
        ])
        
        iteration_chain = iteration_prompt | self.llm | StrOutputParser()
        
        try:
            iteration_response = await iteration_chain.ainvoke({
                "query": query,
                "synthesis": synthesis,
                "iteration_count": iteration_count
            })
            iteration_decision = json.loads(iteration_response)
        except json.JSONDecodeError:
            iteration_decision = {
                "needs_more_research": False,
                "reasoning": "Unable to parse iteration decision",
                "additional_queries": []
            }
        
        # Update state
        state["iteration_count"] = iteration_count + 1
        state["current_phase"] = ResearchPhase.ITERATING.value
        
        if iteration_decision.get("needs_more_research", False):
            # Add additional queries to research plan
            additional_queries = iteration_decision.get("additional_queries", [])
            if additional_queries:
                research_plan = state.get("research_plan", {})
                if "additional_queries" not in research_plan:
                    research_plan["additional_queries"] = []
                research_plan["additional_queries"].extend(additional_queries)
                state["research_plan"] = research_plan
            
            state["messages"].append(AIMessage(content=f"Additional research needed: {iteration_decision.get('reasoning', 'No reasoning provided')}"))
        else:
            state["research_complete"] = True
            state["messages"].append(AIMessage(content="Research iteration complete"))
        
        return state
    
    def _should_iterate(self, state: ResearchState) -> str:
        """Determine if the workflow should iterate or complete."""
        if state.get("research_complete", False):
            return "complete"
        else:
            return "iterate"
    
    async def _simulate_web_search(self, query: str, research_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Simulate web search results (replace with real search API in production)."""
        # This is a simulation - in production, integrate with real search APIs
        # like Google Search API, Bing Search API, or web scraping tools
        
        sub_questions = research_plan.get("sub_questions", [query])
        search_strategies = research_plan.get("search_strategies", ["web search"])
        
        mock_results = []
        
        for i, sub_query in enumerate(sub_questions[:3]):  # Limit to 3 sub-queries
            mock_results.extend([
                {
                    "title": f"Research Article: {sub_query}",
                    "url": f"https://example.com/research/{sub_query.replace(' ', '-')}-{i}",
                    "content": f"This is a comprehensive article about {sub_query} that provides detailed insights and analysis. It covers the main aspects of the topic and provides evidence-based conclusions.",
                    "relevance_score": 0.95 - (i * 0.1),
                    "source_type": "academic"
                },
                {
                    "title": f"Industry Report: {sub_query}",
                    "url": f"https://example.com/industry/{sub_query.replace(' ', '-')}-{i}",
                    "content": f"An industry analysis of {sub_query} with market trends, future predictions, and practical applications. This report provides valuable insights for business decision-making.",
                    "relevance_score": 0.88 - (i * 0.1),
                    "source_type": "industry"
                },
                {
                    "title": f"News Article: {sub_query}",
                    "url": f"https://example.com/news/{sub_query.replace(' ', '-')}-{i}",
                    "content": f"Recent news and developments related to {sub_query}. This article provides up-to-date information and current perspectives on the topic.",
                    "relevance_score": 0.82 - (i * 0.1),
                    "source_type": "news"
                }
            ])
        
        return mock_results
    
    async def conduct_research(self, 
                             query: str, 
                             max_iterations: int = 3,
                             config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Conduct comprehensive deep research using LangGraph.
        
        Args:
            query: The research query
            max_iterations: Maximum number of research iterations
            config: Optional configuration for the graph execution
            
        Returns:
            Dictionary containing the research results
        """
        logger.info(f"Starting Deep Research for query: {query}")
        
        # Initialize state
        initial_state = ResearchState(
            messages=[HumanMessage(content=query)],
            query=query,
            research_plan={},
            search_results=[],
            analysis_results=[],
            synthesis={},
            final_report="",
            current_phase=ResearchPhase.PLANNING.value,
            iteration_count=0,
            max_iterations=max_iterations,
            research_complete=False
        )
        
        # Execute the graph
        try:
            if self.tracer:
                # Use LangSmith tracing
                final_state = await self.graph.ainvoke(
                    initial_state,
                    config=config or {"callbacks": [self.tracer]}
                )
            else:
                final_state = await self.graph.ainvoke(initial_state, config=config)
            
            # Extract results
            result = {
                "query": query,
                "final_report": final_state["final_report"],
                "research_plan": final_state["research_plan"],
                "search_results": final_state["search_results"],
                "analysis_results": final_state["analysis_results"],
                "synthesis": final_state["synthesis"],
                "iteration_count": final_state["iteration_count"],
                "messages": [msg.content for msg in final_state["messages"]],
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
            
            # Store in history
            self.research_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Research failed: {str(e)}")
            return {
                "query": query,
                "final_report": f"Research failed: {str(e)}",
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_research_history(self) -> List[Dict[str, Any]]:
        """Get the research history."""
        return self.research_history
    
    def get_research_by_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Get research results by query."""
        for research in self.research_history:
            if research["query"] == query:
                return research
        return None

# Example usage and testing
async def main():
    """Example usage of the Deep Research LangGraph system."""
    # Initialize the system
    research_system = DeepResearchLangGraph(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
        ollama_base_url="http://localhost:11434"
    )
    
    # Conduct research
    query = "What are the latest trends in AI agent development in 2025?"
    result = await research_system.conduct_research(query, max_iterations=2)
    
    print(f"Research completed: {result['status']}")
    print(f"Report preview: {result['final_report'][:500]}...")
    print(f"Iterations: {result['iteration_count']}")

if __name__ == "__main__":
    asyncio.run(main())
