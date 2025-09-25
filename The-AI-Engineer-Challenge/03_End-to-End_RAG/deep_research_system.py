"""
Session 03: Deep Research Multi-Agent System
============================================

This implements the primary cohort use case - Deep Research - as described in the
AI MakerSpace curriculum. This is a multi-agent system that can autonomously
explore, gather, and synthesize information from various sources.

INDUSTRY ALIGNMENT:
- Implements the "Deep Research" use case that every major AI company has released in 2025
- Aligns with OpenAI's Six Use Case Primitives (Research category)
- Focuses on productivity and ROI through time savings
- Demonstrates multi-agent reasoning and autonomous exploration

TECHNICAL STACK:
- LLM: OpenAI GPT-4o-mini + OSS models via Ollama
- Embedding Model: OpenAI text-embedding-3-small
- Orchestration: OpenAI Python SDK + custom multi-agent framework
- Vector Database: Custom Pythonic vector store
- User Interface: Modern web interface
- Deployment: Docker + Vercel ready
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

import openai
from openai import AsyncOpenAI
import requests
from bs4 import BeautifulSoup
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResearchPhase(Enum):
    """Phases of the Deep Research process."""
    PLANNING = "planning"
    SEARCHING = "searching"
    ANALYZING = "analyzing"
    SYNTHESIZING = "synthesizing"
    REPORTING = "reporting"

@dataclass
class ResearchTask:
    """Represents a single research task."""
    id: str
    query: str
    phase: ResearchPhase
    sources: List[Dict[str, Any]]
    findings: List[str]
    status: str = "pending"
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class ResearchAgent:
    """Individual research agent with specific capabilities."""
    name: str
    role: str
    capabilities: List[str]
    model: str = "gpt-4o-mini"
    
class DeepResearchSystem:
    """
    Multi-agent Deep Research system that can autonomously explore,
    gather, and synthesize information from various sources.
    
    This implements the industry-standard Deep Research capabilities
    seen in ChatGPT, Claude, Perplexity, and other major AI platforms.
    """
    
    def __init__(self, openai_api_key: str, ollama_base_url: str = "http://localhost:11434"):
        """Initialize the Deep Research system."""
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.ollama_base_url = ollama_base_url
        
        # Initialize research agents
        self.agents = {
            "planner": ResearchAgent(
                name="Research Planner",
                role="Creates comprehensive research plans and breaks down complex queries",
                capabilities=["query_analysis", "plan_generation", "task_decomposition"]
            ),
            "searcher": ResearchAgent(
                name="Information Searcher",
                role="Searches and gathers information from various sources",
                capabilities=["web_search", "source_evaluation", "content_extraction"]
            ),
            "analyst": ResearchAgent(
                name="Research Analyst",
                role="Analyzes and evaluates gathered information",
                capabilities=["content_analysis", "fact_verification", "source_critique"]
            ),
            "synthesizer": ResearchAgent(
                name="Information Synthesizer",
                role="Synthesizes findings into coherent insights",
                capabilities=["pattern_recognition", "insight_generation", "knowledge_synthesis"]
            ),
            "reporter": ResearchAgent(
                name="Report Generator",
                role="Creates comprehensive research reports",
                capabilities=["report_writing", "citation_management", "formatting"]
            )
        }
        
        # Research state
        self.active_research = {}
        self.research_history = []
        
        # Vector store for knowledge management
        self.knowledge_base = []
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
    async def conduct_research(self, query: str, research_id: str = None) -> Dict[str, Any]:
        """
        Conduct comprehensive deep research on a given query.
        
        This is the main entry point that orchestrates the multi-agent workflow.
        """
        if research_id is None:
            research_id = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Starting Deep Research for query: {query}")
        
        # Initialize research task
        research_task = ResearchTask(
            id=research_id,
            query=query,
            phase=ResearchPhase.PLANNING,
            sources=[],
            findings=[]
        )
        
        self.active_research[research_id] = research_task
        
        try:
            # Phase 1: Planning
            await self._planning_phase(research_task)
            
            # Phase 2: Searching
            await self._searching_phase(research_task)
            
            # Phase 3: Analyzing
            await self._analyzing_phase(research_task)
            
            # Phase 4: Synthesizing
            await self._synthesizing_phase(research_task)
            
            # Phase 5: Reporting
            report = await self._reporting_phase(research_task)
            
            # Complete research
            research_task.status = "completed"
            self.research_history.append(research_task)
            
            return {
                "research_id": research_id,
                "query": query,
                "status": "completed",
                "report": report,
                "sources": research_task.sources,
                "findings": research_task.findings,
                "created_at": research_task.created_at.isoformat(),
                "completed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Research failed: {str(e)}")
            research_task.status = "failed"
            return {
                "research_id": research_id,
                "query": query,
                "status": "failed",
                "error": str(e)
            }
    
    async def _planning_phase(self, task: ResearchTask):
        """Phase 1: Create comprehensive research plan."""
        logger.info(f"Planning phase for: {task.query}")
        
        planning_prompt = f"""
        As a Research Planner, create a comprehensive research plan for the following query:
        
        Query: {task.query}
        
        Your task is to:
        1. Break down the query into specific research sub-questions
        2. Identify key areas to investigate
        3. Suggest search strategies and sources
        4. Create a structured research approach
        
        Provide your response as a JSON object with:
        - sub_questions: List of specific questions to research
        - key_areas: List of main topics to investigate
        - search_strategies: List of search approaches
        - sources_to_check: List of recommended source types
        - timeline: Estimated time for each phase
        """
        
        response = await self.client.chat.completions.create(
            model=self.agents["planner"].model,
            messages=[
                {"role": "system", "content": f"You are {self.agents['planner'].name}. {self.agents['planner'].role}"},
                {"role": "user", "content": planning_prompt}
            ],
            temperature=0.3
        )
        
        plan = json.loads(response.choices[0].message.content)
        task.findings.append(f"Research Plan: {json.dumps(plan, indent=2)}")
        task.phase = ResearchPhase.SEARCHING
        
    async def _searching_phase(self, task: ResearchTask):
        """Phase 2: Search and gather information."""
        logger.info(f"Searching phase for: {task.query}")
        
        # Simulate web search (in production, integrate with real search APIs)
        search_results = await self._simulate_web_search(task.query)
        
        for result in search_results:
            task.sources.append({
                "title": result["title"],
                "url": result["url"],
                "content": result["content"],
                "relevance_score": result["relevance_score"],
                "source_type": result["source_type"]
            })
        
        task.phase = ResearchPhase.ANALYZING
        
    async def _analyzing_phase(self, task: ResearchTask):
        """Phase 3: Analyze gathered information."""
        logger.info(f"Analyzing phase for: {task.query}")
        
        analysis_prompt = f"""
        As a Research Analyst, analyze the following information sources for the query: {task.query}
        
        Sources:
        {json.dumps([{"title": s["title"], "content": s["content"][:500]} for s in task.sources], indent=2)}
        
        Your analysis should:
        1. Evaluate the credibility and relevance of each source
        2. Identify key facts and insights
        3. Note any contradictions or gaps
        4. Assess the overall quality of information gathered
        
        Provide your analysis as a structured JSON response.
        """
        
        response = await self.client.chat.completions.create(
            model=self.agents["analyst"].model,
            messages=[
                {"role": "system", "content": f"You are {self.agents['analyst'].name}. {self.agents['analyst'].role}"},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.2
        )
        
        analysis = json.loads(response.choices[0].message.content)
        task.findings.append(f"Analysis: {json.dumps(analysis, indent=2)}")
        task.phase = ResearchPhase.SYNTHESIZING
        
    async def _synthesizing_phase(self, task: ResearchTask):
        """Phase 4: Synthesize findings into insights."""
        logger.info(f"Synthesizing phase for: {task.query}")
        
        synthesis_prompt = f"""
        As an Information Synthesizer, synthesize the research findings for: {task.query}
        
        Research Findings:
        {json.dumps(task.findings, indent=2)}
        
        Your synthesis should:
        1. Identify patterns and connections across sources
        2. Generate key insights and conclusions
        3. Highlight important implications
        4. Note areas requiring further research
        
        Provide a comprehensive synthesis as a structured JSON response.
        """
        
        response = await self.client.chat.completions.create(
            model=self.agents["synthesizer"].model,
            messages=[
                {"role": "system", "content": f"You are {self.agents['synthesizer'].name}. {self.agents['synthesizer'].role}"},
                {"role": "user", "content": synthesis_prompt}
            ],
            temperature=0.3
        )
        
        synthesis = json.loads(response.choices[0].message.content)
        task.findings.append(f"Synthesis: {json.dumps(synthesis, indent=2)}")
        task.phase = ResearchPhase.REPORTING
        
    async def _reporting_phase(self, task: ResearchTask) -> str:
        """Phase 5: Generate comprehensive research report."""
        logger.info(f"Reporting phase for: {task.query}")
        
        report_prompt = f"""
        As a Report Generator, create a comprehensive research report for: {task.query}
        
        Research Data:
        - Query: {task.query}
        - Sources: {len(task.sources)} sources analyzed
        - Findings: {json.dumps(task.findings, indent=2)}
        
        Create a professional research report with:
        1. Executive Summary
        2. Key Findings
        3. Detailed Analysis
        4. Conclusions and Recommendations
        5. Sources and Citations
        6. Areas for Further Research
        
        Format the report in clear, professional language suitable for business use.
        """
        
        response = await self.client.chat.completions.create(
            model=self.agents["reporter"].model,
            messages=[
                {"role": "system", "content": f"You are {self.agents['reporter'].name}. {self.agents['reporter'].role}"},
                {"role": "user", "content": report_prompt}
            ],
            temperature=0.4
        )
        
        report = response.choices[0].message.content
        task.findings.append(f"Final Report: {report}")
        
        return report
    
    async def _simulate_web_search(self, query: str) -> List[Dict[str, Any]]:
        """Simulate web search results (replace with real search API in production)."""
        # This is a simulation - in production, integrate with real search APIs
        # like Google Search API, Bing Search API, or web scraping tools
        
        mock_results = [
            {
                "title": f"Research Article: {query}",
                "url": f"https://example.com/research/{query.replace(' ', '-')}",
                "content": f"This is a comprehensive article about {query} that provides detailed insights and analysis.",
                "relevance_score": 0.95,
                "source_type": "academic"
            },
            {
                "title": f"Industry Report: {query}",
                "url": f"https://example.com/industry/{query.replace(' ', '-')}",
                "content": f"An industry analysis of {query} with market trends and future predictions.",
                "relevance_score": 0.88,
                "source_type": "industry"
            },
            {
                "title": f"News Article: {query}",
                "url": f"https://example.com/news/{query.replace(' ', '-')}",
                "content": f"Recent news and developments related to {query}.",
                "relevance_score": 0.82,
                "source_type": "news"
            }
        ]
        
        return mock_results
    
    def get_research_status(self, research_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a research task."""
        if research_id not in self.active_research:
            return None
        
        task = self.active_research[research_id]
        return {
            "research_id": research_id,
            "query": task.query,
            "phase": task.phase.value,
            "status": task.status,
            "sources_count": len(task.sources),
            "findings_count": len(task.findings),
            "created_at": task.created_at.isoformat()
        }
    
    def list_research_history(self) -> List[Dict[str, Any]]:
        """Get list of completed research tasks."""
        return [
            {
                "research_id": task.id,
                "query": task.query,
                "status": task.status,
                "sources_count": len(task.sources),
                "findings_count": len(task.findings),
                "created_at": task.created_at.isoformat()
            }
            for task in self.research_history
        ]

# Example usage and testing
async def main():
    """Example usage of the Deep Research system."""
    # Initialize the system
    research_system = DeepResearchSystem(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        ollama_base_url="http://localhost:11434"
    )
    
    # Conduct research
    query = "What are the latest trends in AI agent development in 2025?"
    result = await research_system.conduct_research(query)
    
    print(f"Research completed: {result['status']}")
    print(f"Report preview: {result['report'][:500]}...")

if __name__ == "__main__":
    asyncio.run(main())

