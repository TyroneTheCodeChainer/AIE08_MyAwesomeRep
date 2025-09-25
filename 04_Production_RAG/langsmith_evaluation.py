"""
Session 04: LangSmith Evaluation and Monitoring
==============================================

This module provides comprehensive evaluation and monitoring capabilities
using LangSmith, aligning with the AI MakerSpace curriculum requirements
for metrics-driven development and production-grade LLM applications.

INDUSTRY ALIGNMENT:
- Implements Metrics Driven Development (MDD) principles
- Provides production-grade monitoring and evaluation
- Enables iterative improvement through quantitative metrics
- Aligns with LangChain's evaluation best practices

EVALUATION CAPABILITIES:
- RAG system performance metrics
- Response quality assessment
- Retrieval accuracy measurement
- Cost and latency tracking
- A/B testing support
- Custom metric definitions
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np

from langsmith import Client
from langchain_core.tracers import LangChainTracer
from langchain_core.runnables import Runnable
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types of evaluation metrics."""
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    COHERENCE = "coherence"
    COMPLETENESS = "completeness"
    LATENCY = "latency"
    COST = "cost"
    RETRIEVAL_QUALITY = "retrieval_quality"
    CUSTOM = "custom"

@dataclass
class EvaluationResult:
    """Result of a single evaluation metric."""
    metric_name: str
    metric_type: MetricType
    value: float
    confidence: float
    details: Dict[str, Any]
    timestamp: datetime
    run_id: str

@dataclass
class EvaluationSuite:
    """A suite of evaluation metrics for a specific use case."""
    name: str
    description: str
    metrics: List[Callable]
    threshold: float = 0.8
    weight: float = 1.0

class LangSmithEvaluator:
    """
    Comprehensive evaluation system using LangSmith for RAG applications.
    
    This class provides production-grade evaluation capabilities including
    automated testing, performance monitoring, and iterative improvement.
    """
    
    def __init__(self, 
                 langsmith_api_key: str,
                 project_name: str = "rag-evaluation",
                 dataset_name: str = "rag-test-dataset"):
        """Initialize the LangSmith evaluator."""
        self.client = Client(api_key=langsmith_api_key)
        self.project_name = project_name
        self.dataset_name = dataset_name
        
        # Initialize or get project
        self.project = self._get_or_create_project()
        
        # Initialize or get dataset
        self.dataset = self._get_or_create_dataset()
        
        # Evaluation suites
        self.evaluation_suites = {}
        
        # Results storage
        self.evaluation_results = []
        
        # Initialize default evaluation suites
        self._initialize_default_suites()
    
    def _get_or_create_project(self):
        """Get or create a LangSmith project."""
        try:
            projects = list(self.client.list_projects())
            for project in projects:
                if project.name == self.project_name:
                    return project
            
            # Create new project
            return self.client.create_project(
                project_name=self.project_name,
                description=f"RAG System Evaluation - {datetime.now().strftime('%Y-%m-%d')}"
            )
        except Exception as e:
            logger.error(f"Error managing project: {str(e)}")
            raise
    
    def _get_or_create_dataset(self):
        """Get or create a LangSmith dataset."""
        try:
            datasets = list(self.client.list_datasets())
            for dataset in datasets:
                if dataset.name == self.dataset_name:
                    return dataset
            
            # Create new dataset
            return self.client.create_dataset(
                dataset_name=self.dataset_name,
                description=f"RAG Test Dataset - {datetime.now().strftime('%Y-%m-%d')}"
            )
        except Exception as e:
            logger.error(f"Error managing dataset: {str(e)}")
            raise
    
    def _initialize_default_suites(self):
        """Initialize default evaluation suites."""
        # RAG Quality Suite
        self.evaluation_suites["rag_quality"] = EvaluationSuite(
            name="RAG Quality",
            description="Comprehensive evaluation of RAG system quality",
            metrics=[
                self._evaluate_answer_relevance,
                self._evaluate_answer_completeness,
                self._evaluate_answer_accuracy,
                self._evaluate_retrieval_quality,
                self._evaluate_response_coherence
            ],
            threshold=0.8
        )
        
        # Performance Suite
        self.evaluation_suites["performance"] = EvaluationSuite(
            name="Performance",
            description="Performance metrics including latency and cost",
            metrics=[
                self._evaluate_response_latency,
                self._evaluate_cost_efficiency,
                self._evaluate_throughput
            ],
            threshold=0.7
        )
        
        # Retrieval Suite
        self.evaluation_suites["retrieval"] = EvaluationSuite(
            name="Retrieval Quality",
            description="Quality of document retrieval and ranking",
            metrics=[
                self._evaluate_retrieval_precision,
                self._evaluate_retrieval_recall,
                self._evaluate_retrieval_relevance
            ],
            threshold=0.75
        )
    
    async def evaluate_rag_system(self, 
                                rag_chain: Runnable,
                                test_questions: List[str],
                                expected_answers: List[str] = None,
                                suite_name: str = "rag_quality") -> Dict[str, Any]:
        """
        Evaluate a RAG system using the specified evaluation suite.
        
        Args:
            rag_chain: The RAG chain to evaluate
            test_questions: List of test questions
            expected_answers: Optional expected answers for comparison
            suite_name: Name of the evaluation suite to use
            
        Returns:
            Dictionary containing evaluation results and metrics
        """
        if suite_name not in self.evaluation_suites:
            raise ValueError(f"Evaluation suite '{suite_name}' not found")
        
        suite = self.evaluation_suites[suite_name]
        results = []
        
        logger.info(f"Starting evaluation with suite: {suite_name}")
        
        for i, question in enumerate(test_questions):
            logger.info(f"Evaluating question {i+1}/{len(test_questions)}: {question[:50]}...")
            
            # Generate response
            start_time = datetime.now()
            try:
                response = await rag_chain.ainvoke({"query": question})
                end_time = datetime.now()
                
                # Extract response content
                if isinstance(response, dict):
                    answer = response.get("answer", str(response))
                else:
                    answer = str(response)
                
                # Calculate metrics
                question_results = {}
                for metric_func in suite.metrics:
                    try:
                        metric_result = await metric_func(
                            question=question,
                            answer=answer,
                            expected_answer=expected_answers[i] if expected_answers else None,
                            response_time=(end_time - start_time).total_seconds(),
                            rag_chain=rag_chain
                        )
                        question_results[metric_result.metric_name] = metric_result
                    except Exception as e:
                        logger.error(f"Error calculating metric {metric_func.__name__}: {str(e)}")
                
                results.append({
                    "question": question,
                    "answer": answer,
                    "expected_answer": expected_answers[i] if expected_answers else None,
                    "response_time": (end_time - start_time).total_seconds(),
                    "metrics": question_results
                })
                
            except Exception as e:
                logger.error(f"Error evaluating question {i+1}: {str(e)}")
                results.append({
                    "question": question,
                    "answer": None,
                    "error": str(e),
                    "metrics": {}
                })
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics(results, suite)
        
        # Store results
        evaluation_result = {
            "suite_name": suite_name,
            "timestamp": datetime.now().isoformat(),
            "total_questions": len(test_questions),
            "successful_evaluations": len([r for r in results if "error" not in r]),
            "overall_metrics": overall_metrics,
            "detailed_results": results
        }
        
        self.evaluation_results.append(evaluation_result)
        
        return evaluation_result
    
    async def _evaluate_answer_relevance(self, 
                                       question: str, 
                                       answer: str, 
                                       expected_answer: str = None,
                                       response_time: float = None,
                                       rag_chain: Runnable = None) -> EvaluationResult:
        """Evaluate how relevant the answer is to the question."""
        # This is a simplified relevance evaluation
        # In production, you might use more sophisticated methods
        
        if not answer:
            return EvaluationResult(
                metric_name="answer_relevance",
                metric_type=MetricType.RELEVANCE,
                value=0.0,
                confidence=1.0,
                details={"error": "No answer provided"},
                timestamp=datetime.now(),
                run_id=""
            )
        
        # Simple keyword overlap scoring
        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())
        
        if len(question_words) == 0:
            relevance_score = 0.0
        else:
            overlap = len(question_words.intersection(answer_words))
            relevance_score = overlap / len(question_words)
        
        return EvaluationResult(
            metric_name="answer_relevance",
            metric_type=MetricType.RELEVANCE,
            value=min(relevance_score, 1.0),
            confidence=0.8,
            details={
                "question_words": len(question_words),
                "answer_words": len(answer_words),
                "overlap": len(question_words.intersection(answer_words))
            },
            timestamp=datetime.now(),
            run_id=""
        )
    
    async def _evaluate_answer_completeness(self, 
                                          question: str, 
                                          answer: str, 
                                          expected_answer: str = None,
                                          response_time: float = None,
                                          rag_chain: Runnable = None) -> EvaluationResult:
        """Evaluate how complete the answer is."""
        if not answer:
            return EvaluationResult(
                metric_name="answer_completeness",
                metric_type=MetricType.COMPLETENESS,
                value=0.0,
                confidence=1.0,
                details={"error": "No answer provided"},
                timestamp=datetime.now(),
                run_id=""
            )
        
        # Simple completeness scoring based on answer length and structure
        word_count = len(answer.split())
        sentence_count = len([s for s in answer.split('.') if s.strip()])
        
        # Basic completeness heuristics
        completeness_score = 0.0
        
        if word_count > 10:
            completeness_score += 0.3
        if word_count > 50:
            completeness_score += 0.3
        if sentence_count > 1:
            completeness_score += 0.2
        if '?' in question and '?' not in answer:  # Question answered
            completeness_score += 0.2
        
        return EvaluationResult(
            metric_name="answer_completeness",
            metric_type=MetricType.COMPLETENESS,
            value=min(completeness_score, 1.0),
            confidence=0.7,
            details={
                "word_count": word_count,
                "sentence_count": sentence_count
            },
            timestamp=datetime.now(),
            run_id=""
        )
    
    async def _evaluate_answer_accuracy(self, 
                                      question: str, 
                                      answer: str, 
                                      expected_answer: str = None,
                                      response_time: float = None,
                                      rag_chain: Runnable = None) -> EvaluationResult:
        """Evaluate the accuracy of the answer."""
        if not answer:
            return EvaluationResult(
                metric_name="answer_accuracy",
                metric_type=MetricType.ACCURACY,
                value=0.0,
                confidence=1.0,
                details={"error": "No answer provided"},
                timestamp=datetime.now(),
                run_id=""
            )
        
        if expected_answer:
            # Compare with expected answer using simple similarity
            from difflib import SequenceMatcher
            similarity = SequenceMatcher(None, answer.lower(), expected_answer.lower()).ratio()
            accuracy_score = similarity
        else:
            # Without expected answer, use heuristics
            # Check for common accuracy indicators
            accuracy_indicators = [
                "according to",
                "based on",
                "research shows",
                "studies indicate",
                "evidence suggests"
            ]
            
            indicator_count = sum(1 for indicator in accuracy_indicators if indicator in answer.lower())
            accuracy_score = min(indicator_count / 3, 1.0)
        
        return EvaluationResult(
            metric_name="answer_accuracy",
            metric_type=MetricType.ACCURACY,
            value=accuracy_score,
            confidence=0.6,
            details={
                "expected_answer_provided": expected_answer is not None,
                "similarity_score": similarity if expected_answer else None
            },
            timestamp=datetime.now(),
            run_id=""
        )
    
    async def _evaluate_retrieval_quality(self, 
                                        question: str, 
                                        answer: str, 
                                        expected_answer: str = None,
                                        response_time: float = None,
                                        rag_chain: Runnable = None) -> EvaluationResult:
        """Evaluate the quality of document retrieval."""
        # This would require access to the retrieval component
        # For now, we'll use a simplified approach
        
        if not answer:
            return EvaluationResult(
                metric_name="retrieval_quality",
                metric_type=MetricType.RETRIEVAL_QUALITY,
                value=0.0,
                confidence=1.0,
                details={"error": "No answer provided"},
                timestamp=datetime.now(),
                run_id=""
            )
        
        # Simple retrieval quality heuristics
        quality_indicators = [
            "source",
            "reference",
            "document",
            "study",
            "research",
            "according to"
        ]
        
        indicator_count = sum(1 for indicator in quality_indicators if indicator in answer.lower())
        quality_score = min(indicator_count / 3, 1.0)
        
        return EvaluationResult(
            metric_name="retrieval_quality",
            metric_type=MetricType.RETRIEVAL_QUALITY,
            value=quality_score,
            confidence=0.5,
            details={
                "quality_indicators_found": indicator_count,
                "total_indicators": len(quality_indicators)
            },
            timestamp=datetime.now(),
            run_id=""
        )
    
    async def _evaluate_response_coherence(self, 
                                         question: str, 
                                         answer: str, 
                                         expected_answer: str = None,
                                         response_time: float = None,
                                         rag_chain: Runnable = None) -> EvaluationResult:
        """Evaluate the coherence of the response."""
        if not answer:
            return EvaluationResult(
                metric_name="response_coherence",
                metric_type=MetricType.COHERENCE,
                value=0.0,
                confidence=1.0,
                details={"error": "No answer provided"},
                timestamp=datetime.now(),
                run_id=""
            )
        
        # Simple coherence scoring
        sentences = [s.strip() for s in answer.split('.') if s.strip()]
        
        if len(sentences) < 2:
            coherence_score = 0.5
        else:
            # Check for transition words and logical flow
            transition_words = [
                "first", "second", "third", "next", "then", "finally",
                "however", "moreover", "furthermore", "additionally",
                "therefore", "consequently", "as a result"
            ]
            
            transition_count = sum(1 for word in transition_words if word in answer.lower())
            coherence_score = min(0.5 + (transition_count / len(sentences)) * 0.5, 1.0)
        
        return EvaluationResult(
            metric_name="response_coherence",
            metric_type=MetricType.COHERENCE,
            value=coherence_score,
            confidence=0.6,
            details={
                "sentence_count": len(sentences),
                "transition_words_found": transition_count
            },
            timestamp=datetime.now(),
            run_id=""
        )
    
    async def _evaluate_response_latency(self, 
                                       question: str, 
                                       answer: str, 
                                       expected_answer: str = None,
                                       response_time: float = None,
                                       rag_chain: Runnable = None) -> EvaluationResult:
        """Evaluate response latency."""
        if response_time is None:
            return EvaluationResult(
                metric_name="response_latency",
                metric_type=MetricType.LATENCY,
                value=0.0,
                confidence=0.0,
                details={"error": "Response time not provided"},
                timestamp=datetime.now(),
                run_id=""
            )
        
        # Score based on response time (lower is better)
        if response_time < 1.0:
            latency_score = 1.0
        elif response_time < 3.0:
            latency_score = 0.8
        elif response_time < 5.0:
            latency_score = 0.6
        elif response_time < 10.0:
            latency_score = 0.4
        else:
            latency_score = 0.2
        
        return EvaluationResult(
            metric_name="response_latency",
            metric_type=MetricType.LATENCY,
            value=latency_score,
            confidence=1.0,
            details={
                "response_time_seconds": response_time,
                "threshold_met": response_time < 5.0
            },
            timestamp=datetime.now(),
            run_id=""
        )
    
    async def _evaluate_cost_efficiency(self, 
                                      question: str, 
                                      answer: str, 
                                      expected_answer: str = None,
                                      response_time: float = None,
                                      rag_chain: Runnable = None) -> EvaluationResult:
        """Evaluate cost efficiency."""
        # This would require actual cost tracking
        # For now, we'll use response time as a proxy
        
        if response_time is None:
            return EvaluationResult(
                metric_name="cost_efficiency",
                metric_type=MetricType.COST,
                value=0.0,
                confidence=0.0,
                details={"error": "Response time not provided"},
                timestamp=datetime.now(),
                run_id=""
            )
        
        # Simple cost efficiency based on response time and answer quality
        word_count = len(answer.split()) if answer else 0
        efficiency_score = word_count / max(response_time, 0.1)  # Words per second
        
        # Normalize to 0-1 scale
        normalized_efficiency = min(efficiency_score / 10, 1.0)
        
        return EvaluationResult(
            metric_name="cost_efficiency",
            metric_type=MetricType.COST,
            value=normalized_efficiency,
            confidence=0.7,
            details={
                "words_per_second": efficiency_score,
                "response_time": response_time,
                "word_count": word_count
            },
            timestamp=datetime.now(),
            run_id=""
        )
    
    async def _evaluate_throughput(self, 
                                 question: str, 
                                 answer: str, 
                                 expected_answer: str = None,
                                 response_time: float = None,
                                 rag_chain: Runnable = None) -> EvaluationResult:
        """Evaluate system throughput."""
        if response_time is None:
            return EvaluationResult(
                metric_name="throughput",
                metric_type=MetricType.LATENCY,
                value=0.0,
                confidence=0.0,
                details={"error": "Response time not provided"},
                timestamp=datetime.now(),
                run_id=""
            )
        
        # Throughput as questions per minute
        throughput = 60 / max(response_time, 0.1)
        
        # Score based on throughput (higher is better)
        if throughput > 60:  # More than 1 question per second
            throughput_score = 1.0
        elif throughput > 30:  # 1 question per 2 seconds
            throughput_score = 0.8
        elif throughput > 12:  # 1 question per 5 seconds
            throughput_score = 0.6
        elif throughput > 6:   # 1 question per 10 seconds
            throughput_score = 0.4
        else:
            throughput_score = 0.2
        
        return EvaluationResult(
            metric_name="throughput",
            metric_type=MetricType.LATENCY,
            value=throughput_score,
            confidence=1.0,
            details={
                "questions_per_minute": throughput,
                "response_time_seconds": response_time
            },
            timestamp=datetime.now(),
            run_id=""
        )
    
    async def _evaluate_retrieval_precision(self, 
                                          question: str, 
                                          answer: str, 
                                          expected_answer: str = None,
                                          response_time: float = None,
                                          rag_chain: Runnable = None) -> EvaluationResult:
        """Evaluate retrieval precision."""
        # This would require access to retrieved documents
        # For now, we'll use a simplified approach
        
        if not answer:
            return EvaluationResult(
                metric_name="retrieval_precision",
                metric_type=MetricType.RETRIEVAL_QUALITY,
                value=0.0,
                confidence=1.0,
                details={"error": "No answer provided"},
                timestamp=datetime.now(),
                run_id=""
            )
        
        # Simple precision scoring based on answer quality
        precision_score = 0.5  # Default baseline
        
        # Add points for quality indicators
        if len(answer.split()) > 20:
            precision_score += 0.2
        if any(word in answer.lower() for word in ["according", "research", "study", "data"]):
            precision_score += 0.3
        
        return EvaluationResult(
            metric_name="retrieval_precision",
            metric_type=MetricType.RETRIEVAL_QUALITY,
            value=min(precision_score, 1.0),
            confidence=0.6,
            details={"baseline_score": 0.5},
            timestamp=datetime.now(),
            run_id=""
        )
    
    async def _evaluate_retrieval_recall(self, 
                                       question: str, 
                                       answer: str, 
                                       expected_answer: str = None,
                                       response_time: float = None,
                                       rag_chain: Runnable = None) -> EvaluationResult:
        """Evaluate retrieval recall."""
        if not answer:
            return EvaluationResult(
                metric_name="retrieval_recall",
                metric_type=MetricType.RETRIEVAL_QUALITY,
                value=0.0,
                confidence=1.0,
                details={"error": "No answer provided"},
                timestamp=datetime.now(),
                run_id=""
            )
        
        # Simple recall scoring
        recall_score = 0.5  # Default baseline
        
        # Add points for comprehensive answers
        if len(answer.split()) > 50:
            recall_score += 0.3
        if answer.count('.') > 2:  # Multiple sentences
            recall_score += 0.2
        
        return EvaluationResult(
            metric_name="retrieval_recall",
            metric_type=MetricType.RETRIEVAL_QUALITY,
            value=min(recall_score, 1.0),
            confidence=0.6,
            details={"baseline_score": 0.5},
            timestamp=datetime.now(),
            run_id=""
        )
    
    async def _evaluate_retrieval_relevance(self, 
                                          question: str, 
                                          answer: str, 
                                          expected_answer: str = None,
                                          response_time: float = None,
                                          rag_chain: Runnable = None) -> EvaluationResult:
        """Evaluate retrieval relevance."""
        if not answer:
            return EvaluationResult(
                metric_name="retrieval_relevance",
                metric_type=MetricType.RETRIEVAL_QUALITY,
                value=0.0,
                confidence=1.0,
                details={"error": "No answer provided"},
                timestamp=datetime.now(),
                run_id=""
            )
        
        # Use the same logic as answer relevance
        return await self._evaluate_answer_relevance(question, answer, expected_answer, response_time, rag_chain)
    
    def _calculate_overall_metrics(self, results: List[Dict[str, Any]], suite: EvaluationSuite) -> Dict[str, Any]:
        """Calculate overall metrics from individual results."""
        if not results:
            return {}
        
        # Extract all metric values
        all_metrics = {}
        for result in results:
            if "metrics" in result:
                for metric_name, metric_result in result["metrics"].items():
                    if metric_name not in all_metrics:
                        all_metrics[metric_name] = []
                    all_metrics[metric_name].append(metric_result.value)
        
        # Calculate averages
        overall_metrics = {}
        for metric_name, values in all_metrics.items():
            if values:
                overall_metrics[metric_name] = {
                    "average": np.mean(values),
                    "median": np.median(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "count": len(values)
                }
        
        # Calculate overall score
        if overall_metrics:
            overall_score = np.mean([metrics["average"] for metrics in overall_metrics.values()])
            overall_metrics["overall_score"] = overall_score
            overall_metrics["threshold_met"] = overall_score >= suite.threshold
        
        return overall_metrics
    
    def create_custom_evaluation_suite(self, 
                                     name: str, 
                                     description: str,
                                     metrics: List[Callable],
                                     threshold: float = 0.8) -> None:
        """Create a custom evaluation suite."""
        self.evaluation_suites[name] = EvaluationSuite(
            name=name,
            description=description,
            metrics=metrics,
            threshold=threshold
        )
    
    def get_evaluation_history(self) -> List[Dict[str, Any]]:
        """Get evaluation history."""
        return self.evaluation_results
    
    def export_evaluation_results(self, filepath: str) -> None:
        """Export evaluation results to a file."""
        with open(filepath, 'w') as f:
            json.dump(self.evaluation_results, f, indent=2, default=str)
    
    def generate_evaluation_report(self) -> str:
        """Generate a comprehensive evaluation report."""
        if not self.evaluation_results:
            return "No evaluation results available."
        
        report = f"# LangSmith Evaluation Report\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for i, result in enumerate(self.evaluation_results):
            report += f"## Evaluation {i+1}\n\n"
            report += f"**Suite:** {result['suite_name']}\n"
            report += f"**Timestamp:** {result['timestamp']}\n"
            report += f"**Questions:** {result['total_questions']}\n"
            report += f"**Successful:** {result['successful_evaluations']}\n\n"
            
            if 'overall_metrics' in result:
                report += f"### Overall Metrics\n\n"
                for metric_name, metrics in result['overall_metrics'].items():
                    if isinstance(metrics, dict) and 'average' in metrics:
                        report += f"- **{metric_name}:** {metrics['average']:.3f} (avg), {metrics['std']:.3f} (std)\n"
                    else:
                        report += f"- **{metric_name}:** {metrics}\n"
                report += "\n"
        
        return report

# Example usage and testing
async def main():
    """Example usage of the LangSmith evaluator."""
    # Initialize the evaluator
    evaluator = LangSmithEvaluator(
        langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
        project_name="rag-evaluation-demo",
        dataset_name="rag-test-dataset"
    )
    
    # Example test questions
    test_questions = [
        "What is machine learning?",
        "How does neural network training work?",
        "What are the benefits of using Python for AI development?"
    ]
    
    # Example expected answers
    expected_answers = [
        "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
        "Neural network training involves feeding data through the network, calculating errors, and adjusting weights through backpropagation.",
        "Python offers extensive libraries, simple syntax, and strong community support for AI development."
    ]
    
    # Note: In a real scenario, you would have an actual RAG chain
    # For this example, we'll create a mock chain
    class MockRAGChain:
        async def ainvoke(self, inputs):
            return {"answer": f"Mock answer for: {inputs['query']}"}
    
    mock_rag_chain = MockRAGChain()
    
    # Run evaluation
    results = await evaluator.evaluate_rag_system(
        rag_chain=mock_rag_chain,
        test_questions=test_questions,
        expected_answers=expected_answers,
        suite_name="rag_quality"
    )
    
    print("Evaluation Results:")
    print(json.dumps(results, indent=2, default=str))
    
    # Generate report
    report = evaluator.generate_evaluation_report()
    print("\nEvaluation Report:")
    print(report)

if __name__ == "__main__":
    asyncio.run(main())

