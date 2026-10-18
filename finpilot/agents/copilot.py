"""Conversational Copilot: Answers natural language questions grounded in user data."""

import json
import logging
from typing import List, Dict, Any
from finpilot.core.mesh_client import get_mesh_client

logger = logging.getLogger("finpilot.agents.copilot")


class CopilotAgent:
    """Agent that handles interactive financial Q&A grounded strictly in user transactions and forecast."""

    def __init__(self):
        self.mesh_client = get_mesh_client()

    def answer_query(
        self,
        query: str,
        transactions: List[Dict[str, Any]],
        forecast: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]],
        goals: List[Dict[str, Any]],
        current_balance: float = 5000.0
    ) -> Dict[str, Any]:
        """Answer user's question with grounded data context."""
        # Assemble compact context
        recent_txs = transactions[-20:] if len(transactions) > 20 else transactions
        simplified_txs = [
            {"date": t.get("date"), "merchant": t.get("merchant"), "amount": t.get("amount"), "category": t.get("category")}
            for t in recent_txs
        ]

        context_summary = {
            "current_balance": current_balance,
            "monthly_burn_rate": forecast.get("monthly_burn_rate", 0.0),
            "projected_end_balance_90d": forecast.get("projected_end_balance", 0.0),
            "savings_rate": forecast.get("projected_savings_rate", 0.0),
            "detected_anomalies_count": len(anomalies),
            "active_recommendations": [r.get("title") for r in recommendations[:3]],
            "active_goals": [{"name": g.get("name"), "target": g.get("target_amount"), "current": g.get("current_amount")} for g in goals],
            "recent_sample_transactions": simplified_txs
        }

        system_prompt = (
            "You are FinPilot Copilot, an elite AI financial advisor grounded strictly in the user's real transactions, "
            "behavioral anomalies, and forward-looking forecast.\n"
            "Rules:\n"
            "1. Ground every statement in their actual numbers provided in the context.\n"
            "2. Be concise, precise, encouraging, and direct.\n"
            "3. If they ask 'can I afford X?', calculate the impact against their balance and 90-day trajectory.\n"
            "4. Return a JSON object with keys: 'reply' (markdown formatted answer), 'data_context_used' (list of key facts referenced), 'suggested_actions' (1-2 quick action buttons)."
        )

        user_content = f"Context:\n{json.dumps(context_summary, indent=2)}\n\nUser Question:\n{query}"

        # If Mesh API is configured, use it
        if self.mesh_client.is_configured():
            try:
                res = self.mesh_client.json_completion(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ]
                )
                if "reply" in res:
                    return {
                        "reply": res.get("reply", ""),
                        "data_context_used": res.get("data_context_used", []),
                        "suggested_actions": res.get("suggested_actions", [])
                    }
            except Exception as e:
                logger.warning(f"Mesh API copilot query failed: {e}. Falling back to rule-grounded response.")

        # Fallback grounded response
        q_lower = query.lower()
        if "afford" in q_lower:
            reply = (
                f"Based on your current balance of **₹{current_balance:,.2f}** and 90-day projected end balance "
                f"of **₹{forecast.get('projected_end_balance', 0.0):,.2f}**, you have cashflow room, but keep an eye "
                f"on your monthly burn rate of **₹{forecast.get('monthly_burn_rate', 0.0):,.2f}**. "
                f"Try running a simulation using the What-If Sandbox to see the exact trajectory impact!"
            )
            actions = ["Simulate in Sandbox", "Check Safety Buffer"]
        elif "subscription" in q_lower or "cancel" in q_lower:
            sub_count = len([a for a in anomalies if a.get("anomaly_type") == "GHOST_SUBSCRIPTION"])
            reply = (
                f"You currently have **{sub_count}** flagged subscription anomalies (such as dormant Cult.fit passes or OTT sprawl). "
                f"Top recommendation: check the Recommendations tab to cancel unused fitness memberships and redundant streaming services."
            )
            actions = ["Review Subscriptions", "Simulate Savings"]
        else:
            reply = (
                f"Your current balance is **₹{current_balance:,.2f}** with an estimated savings rate of **{forecast.get('projected_savings_rate', 0.0)}%**. "
                f"Your 90-day forecast projects you will reach **₹{forecast.get('projected_end_balance', 0.0):,.2f}**. "
                f"Let me know if you would like to simulate a specific purchase or analyze your spending categories!"
            )
            actions = ["What-If Simulation", "View Trajectory"]

        return {
            "reply": reply,
            "data_context_used": [f"Balance: ₹{current_balance:,.2f}", f"90d Forecast: ₹{forecast.get('projected_end_balance', 0.0):,.2f}"],
            "suggested_actions": actions
        }

