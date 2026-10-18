"""Pydantic schemas for data validation and API exchange."""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    date: str = Field(..., description="Transaction date in YYYY-MM-DD format")
    amount: float = Field(..., description="Amount (positive for expense, negative for income/refund)")
    merchant: str = Field(..., description="Merchant or payee name")
    description: Optional[str] = Field("", description="Raw transaction description")


class TransactionCreate(TransactionBase):
    pass


class Transaction(TransactionBase):
    id: int
    category: Optional[str] = "Uncategorized"
    category_group: Optional[str] = "Discretionary Lifestyle"
    is_recurring: bool = False
    is_anomaly: bool = False
    anomaly_reason: Optional[str] = None

    class Config:
        from_attributes = True


class FinancialGoal(BaseModel):
    id: Optional[int] = None
    name: str
    target_amount: float
    current_amount: float = 0.0
    target_date: str
    priority: Literal["high", "medium", "low"] = "medium"
    status: Literal["on_track", "at_risk", "behind", "achieved"] = "on_track"


class AnomalyReport(BaseModel):
    anomaly_type: Literal[
        "GHOST_SUBSCRIPTION",
        "VELOCITY_SURGE",
        "LIFESTYLE_CREEP",
        "UNUSUAL_SPIKE",
        "INCOME_GAP"
    ]
    category: str
    severity: Literal["high", "medium", "low"]
    title: str
    description: str
    metric_evidence: str
    monthly_impact: float = 0.0
    involved_merchants: List[str] = []


class ForecastPoint(BaseModel):
    date: str
    baseline_balance: float
    simulated_balance: Optional[float] = None
    projected_income: float = 0.0
    projected_expense: float = 0.0
    net_daily_change: float = 0.0


class ForecastResult(BaseModel):
    projection_days: int = 90
    start_balance: float
    projected_end_balance: float
    monthly_burn_rate: float
    monthly_recurring_fixed: float
    monthly_variable_spend: float
    projected_savings_rate: float
    runway_days: Optional[float] = None
    trajectory_points: List[ForecastPoint] = []
    key_risks: List[str] = []


class WhatIfScenario(BaseModel):
    name: str = Field(..., description="E.g., 'Trip to Japan', 'New Car Lease', 'Cancel Subscriptions'")
    scenario_type: Literal[
        "ONE_TIME_PURCHASE", 
        "RECURRING_EXPENSE", 
        "EXPENSE_REDUCTION", 
        "INCOME_CHANGE"
    ] = "ONE_TIME_PURCHASE"
    amount: float = Field(..., description="Cost or savings magnitude")
    frequency: Literal["one_time", "monthly", "yearly"] = "one_time"
    target_date: Optional[str] = Field(None, description="Date for one-time purchase or start date")
    description: Optional[str] = None


class WhatIfSimulationResult(BaseModel):
    scenario: WhatIfScenario
    is_affordable: bool
    verdict: Literal["AFFORDABLE", "CONDITIONAL", "HIGH_RISK", "UNSUSTAINABLE"]
    verdict_badge: str
    impact_summary: str
    baseline_end_balance: float
    simulated_end_balance: float
    net_balance_impact: float
    min_buffer_balance: float
    buffer_breached: bool
    affected_goals: List[Dict[str, Any]] = []
    actionable_trade_offs: List[str] = []
    reasoning_trail: str


class Recommendation(BaseModel):
    id: str
    title: str
    action: str
    category: str
    priority: Literal["immediate", "high", "medium", "low"]
    projected_monthly_savings: float = 0.0
    projected_annual_savings: float = 0.0
    trigger_type: str
    confidence_score: float
    reasoning_trail: str
    evidence_data: Dict[str, Any] = {}
    status: Literal["pending", "accepted", "dismissed"] = "pending"


class ProactiveDigest(BaseModel):
    generated_at: str
    health_score: int
    key_forward_insight: str
    primary_action: Recommendation
    secondary_actions: List[Recommendation] = []
    forecast_summary: str
    goals_progress: List[Dict[str, Any]] = []


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str
    data_context_used: List[str] = []
    suggested_actions: List[str] = []
