"""Advisor Agent: Produces grounded, high-leverage recommendations with an auditable decision trail.

Strictly avoids generic financial advice ('spend less'). Every recommendation is
tied directly to detected behavioral anomalies, cashflow trajectories, and user goals.
"""

import uuid
import json
import logging
from typing import List, Dict, Any
from finpilot.core.mesh_client import get_mesh_client
from finpilot.models.schemas import Recommendation

logger = logging.getLogger("finpilot.agents.advisor")


class AdvisorAgent:
    """Agent that translates anomalies and forecasts into auditable actions."""

    def __init__(self):
        self.mesh_client = get_mesh_client()

    def generate_recommendations(
        self,
        anomalies: List[Dict[str, Any]],
        forecast: Dict[str, Any],
        goals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate auditable recommendations backed by data."""
        recommendations: List[Dict[str, Any]] = []

        # 1. Handle Ghost / Dormant Subscriptions
        for anom in anomalies:
            if anom.get("anomaly_type") == "GHOST_SUBSCRIPTION":
                impact = float(anom.get("monthly_impact", 0.0))
                merchants = anom.get("involved_merchants", [])
                m_str = ", ".join(merchants)
                rec_id = f"REC-SUB-{uuid.uuid4().hex[:6]}"

                reasoning = (
                    f"Triggered by Anomaly Detection Engine: Recurring charge of ₹{impact:,.2f}/mo "
                    f"identified for {m_str}. Evidence shows continuous billing without commensurate activity. "
                    f"Canceling these unlocks ₹{impact * 12:,.2f}/year towards financial independence."
                )

                recommendations.append({
                    "id": rec_id,
                    "title": f"Cancel Unused Subscriptions ({m_str})",
                    "action": f"Cancel active recurring billing for {m_str} immediately.",
                    "category": anom.get("category", "Recurring Subscriptions"),
                    "priority": "immediate" if impact > 1500 else "high",
                    "projected_monthly_savings": round(impact, 2),
                    "projected_annual_savings": round(impact * 12, 2),
                    "trigger_type": "GHOST_SUBSCRIPTION",
                    "confidence_score": 0.96,
                    "reasoning_trail": reasoning,
                    "evidence_data": {
                        "merchants": merchants,
                        "monthly_drain": impact,
                        "metric_evidence": anom.get("metric_evidence")
                    },
                    "status": "pending"
                })

            # 2. Handle Velocity Surges (e.g. Food Delivery)
            elif anom.get("anomaly_type") == "VELOCITY_SURGE":
                impact = float(anom.get("monthly_impact", 0.0))
                cat = anom.get("category", "Discretionary Lifestyle")
                rec_id = f"REC-VEL-{uuid.uuid4().hex[:6]}"

                reclaim_target = impact * 0.70  # target 70% reduction in surge
                reasoning = (
                    f"Triggered by Velocity Surge Monitor: Spending in '{cat}' accelerated rapidly "
                    f"({anom.get('metric_evidence')}). Capping out-of-home meal orders to twice weekly "
                    f"recovers ₹{reclaim_target:,.2f}/mo without drastic lifestyle disruption."
                )

                recommendations.append({
                    "id": rec_id,
                    "title": f"Re-anchor Velocity in {cat}",
                    "action": f"Set a hard weekly cap on {cat} to reduce excess spend by ₹{reclaim_target:,.2f}/month.",
                    "category": cat,
                    "priority": "high",
                    "projected_monthly_savings": round(reclaim_target, 2),
                    "projected_annual_savings": round(reclaim_target * 12, 2),
                    "trigger_type": "VELOCITY_SURGE",
                    "confidence_score": 0.92,
                    "reasoning_trail": reasoning,
                    "evidence_data": {
                        "category": cat,
                        "surge_delta": impact,
                        "involved_merchants": anom.get("involved_merchants", [])
                    },
                    "status": "pending"
                })

            # 3. Handle Lifestyle Creep
            elif anom.get("anomaly_type") == "LIFESTYLE_CREEP":
                impact = float(anom.get("monthly_impact", 0.0))
                rec_id = f"REC-LIF-{uuid.uuid4().hex[:6]}"

                reasoning = (
                    f"Triggered by Weekend Spend Concentration: Discretionary outlays disproportionately spike "
                    f"between Friday and Sunday ({anom.get('metric_evidence')}). Establishing a dedicated "
                    f"weekend prepaid UPI wallet recovers ₹{impact:,.2f}/mo."
                )

                recommendations.append({
                    "id": rec_id,
                    "title": "Establish Weekend Discretionary Guardrails",
                    "action": f"Impose a ₹3,500 weekend dining/entertainment envelope to capture ₹{impact:,.2f}/mo savings.",
                    "category": "Discretionary Lifestyle",
                    "priority": "medium",
                    "projected_monthly_savings": round(impact, 2),
                    "projected_annual_savings": round(impact * 12, 2),
                    "trigger_type": "LIFESTYLE_CREEP",
                    "confidence_score": 0.88,
                    "reasoning_trail": reasoning,
                    "evidence_data": {
                        "weekend_drain": impact,
                        "involved_merchants": anom.get("involved_merchants", [])
                    },
                    "status": "pending"
                })

        # 4. Handle Forecast & Goal Alignment
        savings_rate = forecast.get("projected_savings_rate", 0.0)
        burn_rate = forecast.get("monthly_burn_rate", 0.0)
        
        # Check active goals
        for goal in goals:
            g_target = float(goal.get("target_amount", 0.0))
            g_curr = float(goal.get("current_amount", 0.0))
            g_name = goal.get("name", "Savings Goal")
            remaining = max(0.0, g_target - g_curr)
            
            if remaining > 0 and savings_rate < 15.0:
                rec_id = f"REC-GOAL-{uuid.uuid4().hex[:6]}"
                boost_needed = remaining / 6.0  # target 6 months
                reasoning = (
                    f"Triggered by Goal Trajectory Analysis: Current savings rate ({savings_rate:.1f}%) "
                    f"is insufficient to reach goal '{g_name}' (₹{g_target:,.2f}) on schedule. "
                    f"Redirecting reclaimed subscription and surge savings of ₹{boost_needed:,.2f}/mo via automated SIP guarantees arrival."
                )
                recommendations.append({
                    "id": rec_id,
                    "title": f"Accelerate Goal: {g_name}",
                    "action": f"Set automated SIP transfer of ₹{boost_needed:,.2f}/month towards {g_name}.",
                    "category": "Savings & Investments",
                    "priority": "high",
                    "projected_monthly_savings": 0.0,
                    "projected_annual_savings": 0.0,
                    "trigger_type": "GOAL_DEFICIT",
                    "confidence_score": 0.94,
                    "reasoning_trail": reasoning,
                    "evidence_data": {
                        "goal_name": g_name,
                        "remaining_needed": remaining,
                        "current_savings_rate": savings_rate
                    },
                    "status": "pending"
                })


        # 5. Enhance Nuance with Mesh API if online
        if self.mesh_client.is_configured() and recommendations:
            try:
                system_prompt = (
                    "You are the Lead Financial Advisor of FinPilot. Polish the tone of these grounded recommendations. "
                    "Keep them sharp, direct, empathetic, and strictly based on the provided evidence.\n"
                    "Do NOT add generic tips like 'cook at home' unless explicitly supported by the evidence.\n"
                    "Return a JSON object with key 'recommendations' containing the enriched list."
                )
                res = self.mesh_client.json_completion(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Enrich these recommendations:\n{json.dumps(recommendations)}"}
                    ],
                    fallback_dict={"recommendations": recommendations}
                )
                if "recommendations" in res and isinstance(res["recommendations"], list) and len(res["recommendations"]) > 0:
                    return res["recommendations"]
            except Exception as e:
                logger.warning(f"Mesh API recommendation enhancement failed: {e}. Using deterministic advisor.")

        return recommendations

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph node execution."""
        anomalies = state.get("anomalies", [])
        forecast = state.get("forecast", {})
        goals = state.get("goals", [])

        recs = self.generate_recommendations(anomalies, forecast, goals)
        steps = state.get("execution_steps", [])
        steps.append(f"AdvisorAgent: generated {len(recs)} grounded, auditable recommendations.")

        return {
            "recommendations": recs,
            "execution_steps": steps
        }
