"""What-If Decision Simulation Engine.

Simulates planned purchases, lifestyle changes, and counterfactuals against the
user's real cashflow trajectory and active goals.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from finpilot.core.mesh_client import get_mesh_client
from finpilot.models.schemas import WhatIfScenario, WhatIfSimulationResult

logger = logging.getLogger("finpilot.agents.simulator")


class WhatIfSimulatorAgent:
    """Agent that stress-tests financial decisions against forward trajectories."""

    def __init__(self, min_safety_buffer: float = 1200.0):
        self.min_safety_buffer = min_safety_buffer
        self.mesh_client = get_mesh_client()

    def simulate_decision(
        self,
        scenario: Dict[str, Any],
        baseline_forecast: Dict[str, Any],
        goals: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Simulate a what-if scenario against baseline trajectory."""
        goals = goals or []
        trajectory_points = baseline_forecast.get("trajectory_points", [])
        if not trajectory_points:
            return {
                "scenario": scenario,
                "is_affordable": False,
                "verdict": "HIGH_RISK",
                "verdict_badge": "Data Insufficient",
                "impact_summary": "No baseline forecast available to simulate against.",
                "baseline_end_balance": 0.0,
                "simulated_end_balance": 0.0,
                "net_balance_impact": 0.0,
                "min_buffer_balance": 0.0,
                "buffer_breached": True,
                "affected_goals": [],
                "actionable_trade_offs": [],
                "reasoning_trail": "Cannot simulate without active forecast."
            }

        name = scenario.get("name", "Unnamed Decision")
        sc_type = scenario.get("scenario_type", "ONE_TIME_PURCHASE")
        amount = float(scenario.get("amount", 0.0))
        freq = scenario.get("frequency", "one_time")
        target_date_str = scenario.get("target_date")

        # Parse target date or default to 30 days from start
        today = datetime.now()
        if target_date_str:
            try:
                target_dt = datetime.strptime(target_date_str[:10], "%Y-%m-%d")
            except Exception:
                target_dt = today + timedelta(days=30)
        else:
            target_dt = today + timedelta(days=30)

        simulated_points = []
        min_simulated_bal = float("inf")
        buffer_breached = False
        breach_date = None

        daily_recurring_impact = (amount / 30.4) if freq == "monthly" else 0.0
        applied_one_time = False

        for pt in trajectory_points:
            pt_date = datetime.strptime(pt["date"], "%Y-%m-%d")
            base_bal = pt["baseline_balance"]
            sim_bal = base_bal

            if sc_type == "ONE_TIME_PURCHASE":
                if pt_date >= target_dt:
                    sim_bal = base_bal - amount
            elif sc_type == "RECURRING_EXPENSE":
                if pt_date >= target_dt:
                    days_active = (pt_date - target_dt).days + 1
                    sim_bal = base_bal - (daily_recurring_impact * days_active)
            elif sc_type == "EXPENSE_REDUCTION":
                if pt_date >= target_dt:
                    days_active = (pt_date - target_dt).days + 1
                    sim_bal = base_bal + (daily_recurring_impact * days_active)
            elif sc_type == "INCOME_CHANGE":
                if pt_date >= target_dt:
                    days_active = (pt_date - target_dt).days + 1
                    sim_bal = base_bal + (daily_recurring_impact * days_active)

            if sim_bal < min_simulated_bal:
                min_simulated_bal = sim_bal
                if sim_bal < self.min_safety_buffer and not buffer_breached:
                    buffer_breached = True
                    breach_date = pt["date"]

            pt_copy = dict(pt)
            pt_copy["simulated_balance"] = round(sim_bal, 2)
            simulated_points.append(pt_copy)

        baseline_end = trajectory_points[-1]["baseline_balance"]
        simulated_end = simulated_points[-1]["simulated_balance"]
        net_impact = simulated_end - baseline_end
        monthly_burn = float(baseline_forecast.get("monthly_burn_rate", 3000.0))
        monthly_income = float(baseline_forecast.get("monthly_burn_rate", 3000.0)) + float(baseline_forecast.get("projected_savings_rate", 0.0) * 50)

        # Check impact on goals
        affected_goals = []
        for g in goals:
            g_target = float(g.get("target_amount", 0.0))
            g_name = g.get("name", "Goal")
            if baseline_end >= g_target and simulated_end < g_target:
                affected_goals.append({
                    "goal_name": g_name,
                    "target_amount": g_target,
                    "impact": f"Postpones reaching '{g_name}' by projected horizon end."
                })

        # Assess Structural & Outlay Risk Thresholds
        is_large_outlay = (sc_type == "ONE_TIME_PURCHASE" and amount >= 3500.0)
        is_heavy_recurring_burden = (sc_type == "RECURRING_EXPENSE" and amount >= 600.0)

        # Determine Verdict
        if simulated_end < 0 or min_simulated_bal < 0:
            verdict = "UNSUSTAINABLE"
            verdict_badge = "🚨 Cannot Afford"
            is_affordable = False
        elif buffer_breached or min_simulated_bal < self.min_safety_buffer or is_large_outlay or is_heavy_recurring_burden:
            verdict = "HIGH_RISK"
            verdict_badge = "⚠️ High Risk"
            is_affordable = False
        elif affected_goals or (sc_type == "ONE_TIME_PURCHASE" and amount > 1500.0):
            verdict = "CONDITIONAL"
            verdict_badge = "⚖️ Conditional"
            is_affordable = True
        else:
            verdict = "AFFORDABLE"
            verdict_badge = "✅ Affordable"
            is_affordable = True


        # Generate Actionable Trade-offs
        trade_offs = []
        if verdict in ["CONDITIONAL", "HIGH_RISK", "UNSUSTAINABLE"]:
            monthly_recovery_needed = abs(net_impact) / 3.0  # over 3 months
            trade_offs.append(f"Trim dining out and delivery by ${monthly_recovery_needed * 0.5:.2f}/mo.")
            trade_offs.append(f"Pause unused subscriptions to reclaim ${monthly_recovery_needed * 0.25:.2f}/mo.")
            trade_offs.append("Delay purchase by 45 days to allow cash reserves to replenish.")

        # Grounded reasoning trail
        if is_affordable and verdict == "AFFORDABLE":
            reasoning = (
                f"Approved: After allocating ${amount:,.2f} for '{name}', your minimum reserve remains "
                f"${min_simulated_bal:,.2f} (above safety threshold of ${self.min_safety_buffer:,.2f}), "
                f"and projected 90-day ending balance settles at ${simulated_end:,.2f}."
            )
        elif verdict == "CONDITIONAL":
            reasoning = (
                f"Conditional: You can absorb the ${amount:,.2f} outlay, but your minimum balance "
                f"compresses to ${min_simulated_bal:,.2f} and compromises active goal milestones ({len(affected_goals)} goals delayed)."
            )
        else:
            reasoning = (
                f"Risk Warning: Committing ${amount:,.2f} causes your liquidity to breach the minimum "
                f"safety cushion on {breach_date}, dropping balance to ${min_simulated_bal:,.2f}."
            )

        # Synthesize with Mesh API if online for nuanced natural language
        if self.mesh_client.is_configured():
            try:
                system_prompt = (
                    "You are the Simulation & Decision Reasoner of FinPilot. The user asked if they can afford a decision. "
                    "Review the quantitative simulation results and produce an empathetic, mathematically rigorous explanation "
                    "with clear trade-offs.\n"
                    "Return a JSON object with keys: 'impact_summary', 'reasoning_trail', 'actionable_trade_offs'."
                )
                user_content = {
                    "scenario": scenario,
                    "verdict": verdict,
                    "min_simulated_bal": min_simulated_bal,
                    "baseline_end": baseline_end,
                    "simulated_end": simulated_end,
                    "affected_goals": affected_goals
                }
                res = self.mesh_client.json_completion(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": json.dumps(user_content)}
                    ],
                    fallback_dict={
                        "impact_summary": f"Simulated {name} with net impact of ${net_impact:,.2f}.",
                        "reasoning_trail": reasoning,
                        "actionable_trade_offs": trade_offs
                    }
                )
                if "reasoning_trail" in res:
                    reasoning = res["reasoning_trail"]
                if "actionable_trade_offs" in res and isinstance(res["actionable_trade_offs"], list):
                    trade_offs = res["actionable_trade_offs"]
            except Exception as e:
                logger.warning(f"Mesh API simulation synthesis failed: {e}. Using deterministic reasoner.")

        return {
            "scenario": scenario,
            "is_affordable": is_affordable,
            "verdict": verdict,
            "verdict_badge": verdict_badge,
            "impact_summary": f"Simulated {name} ({freq}) for ${amount:,.2f}. 90-day balance shifts by ${net_impact:,.2f}.",
            "baseline_end_balance": round(baseline_end, 2),
            "simulated_end_balance": round(simulated_end, 2),
            "net_balance_impact": round(net_impact, 2),
            "min_buffer_balance": round(min_simulated_bal, 2),
            "buffer_breached": buffer_breached,
            "affected_goals": affected_goals,
            "actionable_trade_offs": trade_offs,
            "reasoning_trail": reasoning,
            "simulated_points": simulated_points
        }

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph node execution for simulation."""
        scenario = state.get("simulation_scenario")
        forecast = state.get("forecast", {})
        goals = state.get("goals", [])

        if not scenario:
            return {"simulation_result": None}

        sim_res = self.simulate_decision(scenario, forecast, goals)
        steps = state.get("execution_steps", [])
        steps.append(
            f"WhatIfSimulatorAgent: simulated scenario '{scenario.get('name')}' -> Verdict: {sim_res.get('verdict')}."
        )

        return {
            "simulation_result": sim_res,
            "execution_steps": steps
        }
