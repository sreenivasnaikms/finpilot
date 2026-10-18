"""State definition for LangGraph multi-agent orchestration."""

from typing import List, Dict, Any, Optional, TypedDict


class AgentState(TypedDict, total=False):
    # Core user financial context
    current_balance: float
    transactions: List[Dict[str, Any]]
    goals: List[Dict[str, Any]]
    
    # Inter-agent outputs
    categorized_transactions: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    forecast: Optional[Dict[str, Any]]
    
    # What-if simulation loop
    simulation_scenario: Optional[Dict[str, Any]]
    simulation_result: Optional[Dict[str, Any]]
    
    # Final grounded recommendations
    recommendations: List[Dict[str, Any]]
    
    # Audit log and execution trail
    execution_steps: List[str]
    errors: List[str]
