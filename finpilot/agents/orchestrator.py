"""Multi-Agent Orchestrator using LangGraph.

Coordinates specialized agents:
1. CategorizationAgent
2. BehaviorAnalysisAgent
3. ForecastingAgent
4. AdvisorAgent
5. WhatIfSimulatorAgent
6. CopilotAgent
"""

import logging
from typing import List, Dict, Any, Optional

from langgraph.graph import StateGraph, START, END

from finpilot.agents.state import AgentState
from finpilot.agents.categorizer import CategorizationAgent
from finpilot.agents.analyzer import BehaviorAnalysisAgent
from finpilot.agents.forecaster import ForecastingAgent
from finpilot.agents.advisor import AdvisorAgent
from finpilot.agents.simulator import WhatIfSimulatorAgent
from finpilot.agents.copilot import CopilotAgent

logger = logging.getLogger("finpilot.agents.orchestrator")


class FinPilotOrchestrator:
    """Central coordinator for multi-agent execution pipeline."""

    def __init__(self):
        self.categorizer = CategorizationAgent()
        self.analyzer = BehaviorAnalysisAgent()
        self.forecaster = ForecastingAgent(projection_days=90)
        self.advisor = AdvisorAgent()
        self.simulator = WhatIfSimulatorAgent()
        self.copilot = CopilotAgent()

        self.graph = self._build_graph()

    def _build_graph(self):
        """Construct the LangGraph StateGraph pipeline."""
        builder = StateGraph(AgentState)

        # Add Nodes
        builder.add_node("categorizer", self.categorizer.run)
        builder.add_node("analyzer", self.analyzer.run)
        builder.add_node("forecaster", self.forecaster.run)
        builder.add_node("advisor", self.advisor.run)

        # Define Edges: START -> categorizer -> analyzer -> forecaster -> advisor -> END
        builder.add_edge(START, "categorizer")
        builder.add_edge("categorizer", "analyzer")
        builder.add_edge("analyzer", "forecaster")
        builder.add_edge("forecaster", "advisor")
        builder.add_edge("advisor", END)

        return builder.compile()

    def run_full_pipeline(
        self,
        transactions: List[Dict[str, Any]],
        current_balance: float = 5000.0,
        goals: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Execute the complete multi-agent pipeline."""
        initial_state: AgentState = {
            "transactions": transactions,
            "current_balance": current_balance,
            "goals": goals or [],
            "execution_steps": [],
            "errors": []
        }

        result = self.graph.invoke(initial_state)
        return result

    def simulate_what_if(
        self,
        scenario: Dict[str, Any],
        forecast: Dict[str, Any],
        goals: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Simulate a what-if scenario directly using simulator agent."""
        return self.simulator.simulate_decision(
            scenario=scenario,
            baseline_forecast=forecast,
            goals=goals
        )

    def query_copilot(
        self,
        query: str,
        transactions: List[Dict[str, Any]],
        forecast: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]],
        goals: List[Dict[str, Any]],
        current_balance: float = 5000.0
    ) -> Dict[str, Any]:
        """Run conversational query."""
        return self.copilot.answer_query(
            query=query,
            transactions=transactions,
            forecast=forecast,
            anomalies=anomalies,
            recommendations=recommendations,
            goals=goals,
            current_balance=current_balance
        )


# Singleton orchestrator
_orchestrator: Optional[FinPilotOrchestrator] = None


def get_orchestrator() -> FinPilotOrchestrator:
    """Retrieve or create the FinPilot orchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = FinPilotOrchestrator()
    return _orchestrator
