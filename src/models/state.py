# src/models/state.py
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class FinancialMetrics(BaseModel):
    """Financial metrics for analysis"""
    revenue_growth: float = Field(..., description="Year-over-year revenue growth")
    profit_margin: float = Field(..., description="Net profit margin")
    debt_to_equity: float = Field(..., description="Debt to equity ratio")
    current_ratio: float = Field(..., description="Current ratio")


class AnalysisPoint(BaseModel):
    """Single analysis point from an agent"""
    metric: str = Field(..., description="Metric being analyzed")
    observation: str = Field(..., description="Agent's observation")
    sentiment: float = Field(..., ge=-1, le=1, description="Sentiment score")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")


class AgentState(BaseModel):
    """State for each agent"""
    analysis_points: List[AnalysisPoint] = Field(default_factory=list)
    completed_metrics: List[str] = Field(default_factory=list)
    current_focus: Optional[str] = None


class ResearchState(BaseModel):
    """Overall research state"""
    company_name: str
    metrics: FinancialMetrics
    bull_state: AgentState
    bear_state: AgentState
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    status: str = "initializing"
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    # New fields for workflow control
    metrics_to_analyze: List[str] = Field(default_factory=list)
    current_metric_index: int = 0
    final_report: Optional[Dict[str, Any]] = None

    class Config:
        arbitrary_types_allowed = True
