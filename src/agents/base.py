# src/agents/base.py
from typing import Dict, List

from langchain_core.language_models import BaseChatModel
from langgraph.graph import MessageGraph
from langchain.schema import BaseMessage
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from src.models.state import ResearchState, AgentState, AnalysisPoint
from datetime import datetime
from langchain_core.tools import Tool


class FinancialAnalysisAgent:
    """Base class for financial analysis agents"""

    def __init__(self, llm: BaseChatModel, name: str, role_description: str):
        self.llm = llm
        self.name = name
        self.role_description = role_description

    def analyze(self, state: ResearchState) -> ResearchState:
        """
        Analyze the current state and return updated state.
        This is the main agent function that will be called by the LangGraph workflow.
        """
        # Print analysis context
        current_metric = state.metrics_to_analyze[state.current_metric_index]
        print(f"\n\033[94m{'='*50}\033[0m")
        print(f"\033[94mAnalyzing {current_metric} for {state.company_name}\033[0m")
        print(f"\033[94m{'='*50}\033[0m\n")

        # Create the agent's context from state
        context = self._create_context(state)

        # Get the agent's response
        response = self._get_analysis(context)

        # Update the state with the agent's analysis
        return self._update_state(state, response)

    def _create_context(self, state: ResearchState) -> str:
        """Create context for the agent from the current state"""
        metrics = state.metrics
        current_metric = state.metrics_to_analyze[state.current_metric_index]

        context = f"""
        You are a {self.role_description} analyzing {state.company_name}.
        
        Current focus metric: {current_metric}
        
        Financial metrics:
        {metrics}
        
        Your task is to analyze financial metrics and provide detailed insights.
        Analysis Guidelines:
        1. Focus on the current metric while considering its relationships with other metrics
        2. Use specific numbers and percentages in your analysis
        3. When responding to other agent's points:
           - Acknowledge their perspective
           - Add new insights that build on or respectfully challenge their analysis
           - Support your views with specific data from the metrics
        4. Keep the discussion focused on {state.company_name}'s performance
        5. Avoid speculation about information not provided in the metrics
    
        
        Previous discussion points:
        """

        # Add last 3 messages for context
        recent_messages = state.conversation_history[-3:] if state.conversation_history else []
        for message in recent_messages:
            context += f"\n{message['agent']}: {message['content']}"

        return context

    def _get_analysis(self, context: str) -> str:
        """Get analysis from the LLM with enhanced prompting and validation"""
        messages = [
            SystemMessage(content=f"""{context}. 
            """),
            #HumanMessage(content=context),
            HumanMessage(content=f"""Analyze the current metric in detail. 
            Remember to maintain your perspective as a {self.name} analyst.
            If you see any concerning trends or notable points, highlight them.
            
            Provide a thorough analysis with specific numbers and implications.
            Let's think about it step by step..
            """)
        ]

        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Initialize an empty string to collect the streamed content
                accumulated_content = []

                # Get streaming response
                print(f"\033[92m{self.name}\033[0m:")
                for chunk in self.llm.stream(messages):
                    # Extract content from the chunk
                    if hasattr(chunk, 'content'):
                        content = chunk.content
                    elif isinstance(chunk, dict) and 'content' in chunk:
                        content = chunk['content']
                    else:
                        content = str(chunk)

                    if content:
                        # Print the chunk with agent identification
                        print(f"{content}", end="", flush=True)
                        accumulated_content.append(content)

                # Add a newline after streaming is complete
                print()

                # Combine all chunks into final content
                final_content = "".join(accumulated_content)

                # Validate response
                if not final_content or len(final_content.strip()) < 50:  # Minimum response length
                    retry_count += 1
                    continue

                return final_content

            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    # If all retries failed, return a fallback analysis
                    return self._generate_fallback_analysis(context)

        # If we got here, all retries failed but no exception was raised
        return self._generate_fallback_analysis(context)

    def _generate_fallback_analysis(self, context: str) -> str:
        """Generate a fallback analysis when LLM response fails"""
        # Extract the current metric and its value from context
        import re

        # Parse the metrics from the context
        metrics_dict = {}
        for line in context.split('\n'):
            if ':' in line and '%' in line:
                metric, value = line.split(':')
                metric = metric.strip('- ')
                value = value.strip('% ')
                metrics_dict[metric.lower()] = float(value)

        current_metric = None
        for line in context.split('\n'):
            if 'Current focus metric:' in line:
                current_metric = line.split(':')[1].strip()
                break

        if not current_metric or current_metric not in metrics_dict:
            return f"Based on the available data, the {current_metric} requires careful analysis in the context of overall company performance. Further investigation is recommended to make a comprehensive assessment."

        value = metrics_dict.get(current_metric.lower())

        # Generate a basic analysis based on the metric type
        if 'revenue' in current_metric.lower():
            return f"The {current_metric} of {value}% indicates {'significant growth potential' if value > 10 else 'moderate growth'}. This metric requires careful monitoring in the context of market conditions and competitive landscape."
        elif 'margin' in current_metric.lower():
            return f"The {current_metric} of {value}% suggests {'healthy profitability' if value > 10 else 'potential pressure on profitability'}. Further analysis of cost structures and pricing strategy is recommended."
        elif 'ratio' in current_metric.lower():
            return f"The {current_metric} of {value} indicates {'strong' if value > 2 else 'adequate'} financial health. This should be analyzed alongside other liquidity and solvency metrics."

        return f"The {current_metric} of {value} requires detailed analysis in the context of industry standards and company's strategic objectives."

    def _update_state(self, state: ResearchState, response: str) -> ResearchState:
        """Update the state with the agent's analysis"""
        # Create a new state object to maintain immutability
        new_state = state.model_copy(deep=True)

        # Add the response to conversation history
        new_message = {
            "agent": self.name,
            "content": response,
            "timestamp": datetime.now().isoformat()
        }
        new_state.conversation_history.append(new_message)

        # Update agent-specific state
        current_metric = state.metrics_to_analyze[state.current_metric_index]
        if self.name == "Bull":
            agent_state = new_state.bull_state
        else:
            agent_state = new_state.bear_state

        # Add the metric to completed metrics if not already present
        if current_metric not in agent_state.completed_metrics:
            agent_state.completed_metrics.append(current_metric)

        # Create a new analysis point
        new_point = AnalysisPoint(
            metric=current_metric,
            observation=response,
            sentiment=0.0,  # You might want to add sentiment analysis here
            confidence=0.8  # You might want to calculate this based on the response
        )
        agent_state.analysis_points.append(new_point)

        return new_state