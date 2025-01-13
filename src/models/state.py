# src/models/state.py
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class FinancialMetrics(BaseModel):
    """Financial metrics for analysis"""
    revenue_growth: float = Field(..., description="Year-over-year revenue growth"),
    profit_margin: float = Field(..., description="Net profit margin"),
    return_on_assets: float = Field(..., description="Return on assets"),
    return_on_equity: float = Field(..., description="Return on equity"),
    earnings_per_share: float = Field(..., description="Earnings per share"),
    pe_ratio: float = Field(..., description="Price-to-earnings ratio"),
    peg_ratio: float = Field(..., description="Price-to-earnings growth ratio"),
    book_value: float = Field(..., description="Book value per share"),
    dividend_per_share: float = Field(..., description="Dividend per share"),
    dividend_yield: float = Field(..., description="Dividend yield"),
    revenue_per_share: float = Field(..., description="Revenue per share"),
    operating_margin: float = Field(..., description="Operating margin"),
    gross_profit: float = Field(..., description="Gross profit"),
    quarterly_earnings_growth: float = Field(..., description="Quarterly earnings growth"),
    market_cap: float = Field(..., description="Market capitalization"),
    ebitda: float = Field(..., description="EBITDA"),  


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
