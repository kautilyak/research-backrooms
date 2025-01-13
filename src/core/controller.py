# src/core/controller.py
from typing import Dict, List, Tuple, Any
from langgraph.graph import StateGraph, END
from langchain_core.language_models import BaseChatModel
from datetime import datetime
from copy import deepcopy

from langgraph.graph.state import CompiledStateGraph

from ..agents.bear_agent import BearAgent
from ..agents.bull_agent import BullAgent
from src.models.state import ResearchState, FinancialMetrics, AgentState


class ResearchController:
    """Controls the financial research workflow between agents"""

    def __init__(self, llm: BaseChatModel):
        """Initialize the controller with necessary components"""
        self.bull_agent = BullAgent(llm)
        self.bear_agent = BearAgent(llm)
        self.workflow = self._create_workflow()

    def _create_workflow(self) -> CompiledStateGraph:
        """Create the LangGraph workflow"""
        # Initialize the graph
        workflow = StateGraph(ResearchState)

        # Define the nodes
        workflow.add_node("initialize", self._initialize_research)
        workflow.add_node("bull_analysis", self.bull_agent.analyze)
        workflow.add_node("bear_analysis", self.bear_agent.analyze)
        workflow.add_node("check_completion", self._check_completion)
        workflow.add_node("generate_report", self._generate_report)

        # Define the edges
        workflow.add_edge("initialize", "bull_analysis")
        workflow.add_edge("bull_analysis", "bear_analysis")
        workflow.add_edge("bear_analysis", "check_completion")

        # Add conditional edges
        workflow.add_conditional_edges(
            "check_completion",
            self._determine_next_step,
            {
                "continue": "bull_analysis",
                "complete": "generate_report",
            }
        )

        workflow.add_edge("generate_report", END)

        # Set the entry point
        workflow.set_entry_point("initialize")

        return workflow.compile()

    def _initialize_research(self, state: ResearchState) -> ResearchState:
        """Initialize the research state"""
        # Instead of using update(), we create a new state with all required fields
        return ResearchState(
            company_name=state.company_name,
            metrics=state.metrics,
            bull_state=AgentState(
                analysis_points=[],
                completed_metrics=[],
                current_focus=None
            ),
            bear_state=AgentState(
                analysis_points=[],
                completed_metrics=[],
                current_focus=None
            ),
            conversation_history=[],
            status="active",
            started_at=datetime.now(),
            metrics_to_analyze=[
                # include all the metrics from vantage
                "revenue_growth",
                "profit_margin",
                "debt_to_equity",
                "current_ratio",   
                "cash_flow_ratio",
                "inventory_turnover",
                "asset_turnover",
                "return_on_assets",
                "return_on_equity",
                "earnings_per_share",
                "pe_ratio",
                "peg_ratio",
                "book_value",
                "dividend_per_share",
                "dividend_yield",
                "revenue_per_share",
                "operating_margin",
                "gross_profit",
                "quarterly_earnings_growth",
                "market_cap",
                "ebitda"
            ],
            current_metric_index=0
        )

    def _determine_next_step(self, state: ResearchState) -> str:
        """Determine the next step in the workflow"""
        # Check if all metrics have been analyzed
        if state.current_metric_index >= len(state.metrics_to_analyze):
            return "complete"

        # Check if we've exceeded maximum iterations
        if len(state.conversation_history) > 20:  # Prevent infinite loops
            return "complete"

        return "continue"

    def _check_completion(self, state: ResearchState) -> ResearchState:
        """Check if the current metric analysis is complete"""
        current_metric = state.metrics_to_analyze[state.current_metric_index]

        # Create a new state object with updated index if needed
        new_state = deepcopy(state)
        if (current_metric in state.bull_state.completed_metrics and
                current_metric in state.bear_state.completed_metrics):
            new_state.current_metric_index += 1

        return new_state

    def _generate_report(self, state: ResearchState) -> ResearchState:
        """Generate the final analysis report"""
        # Compile insights from both agents
        bull_insights = self._compile_agent_insights(state.conversation_history, "Bull")
        bear_insights = self._compile_agent_insights(state.conversation_history, "Bear")

        # Create new state with the final report
        new_state = deepcopy(state)

        # REMOVED AFTER MAKING FINAL REPORT A PYDANTIC MODEL: CHECK BELOW
        new_state.final_report = {
            "company_name": state.company_name,
            "analysis_duration": (datetime.now() - state.started_at).seconds,
            "bull_analysis": bull_insights,
            "bear_analysis": bear_insights,
            "metrics_analyzed": state.metrics_to_analyze,
            "completion_status": "success"
        }

        # new_state.final_report = FinalReport(
        #     company_name=state.company_name,
        #     analysis_duration=(datetime.now() - state.started_at).seconds,
        #     bull_analysis=bull_insights,
        #     bear_analysis=bear_insights,
        #     metrics_analyzed=state.metrics_to_analyze,
        #     completion_status="success"
        # )
        new_state.status = "completed"
        new_state.completed_at = datetime.now()

        return new_state

    def _compile_agent_insights(self, conversation_history: List[Dict], agent_name: str) -> List[Dict]:
        """Compile insights from a specific agent"""
        return [
            {
                "content": msg["content"],
                "timestamp": msg["timestamp"]
            }
            for msg in conversation_history
            if msg["agent"] == agent_name
        ]

    async def run_research(self, company_name: str, metrics: FinancialMetrics) -> Dict:
        """Run the research workflow"""
        try:
            # Create initial state using Pydantic model
            initial_state = ResearchState(
                company_name=company_name,
                metrics=metrics,
                bull_state=AgentState(),  # Using default values
                bear_state=AgentState(),  # Using default values
                conversation_history=[],
                status="initializing"
            )

            # Run the workflow
            config = {"recursion_limit": 25}  # Prevent infinite loops
            final_state = await self.workflow.ainvoke(
                initial_state,
                config=config
            )

            return final_state['final_report']

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "company_name": company_name,
                "completion_status": "failed"
            }