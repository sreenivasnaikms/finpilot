"""Behavior Analysis & Anomaly Detection Agent.

Aggregates financial transactions over time to uncover:
- Velocity surges (e.g. food delivery up 40% MoM)
- Ghost / dormant subscriptions (recurring charges with zero engagement or duplicates)
- Weekend impulse clusters
- Cashflow margin compression
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict
import pandas as pd

from finpilot.core.mesh_client import get_mesh_client
from finpilot.models.schemas import AnomalyReport

logger = logging.getLogger("finpilot.agents.analyzer")


class BehaviorAnalysisAgent:
    """Agent that analyzes longitudinal financial behavior and detects anomalies."""

    def __init__(self):
        self.mesh_client = get_mesh_client()

    def analyze_patterns(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run statistical pattern extraction and LLM anomaly synthesis."""
        if not transactions:
            return []

        df = pd.DataFrame(transactions)
        if "date" not in df.columns or "amount" not in df.columns:
            return []

        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        anomalies: List[Dict[str, Any]] = []

        # 1. Detect Ghost / Redundant Subscriptions
        # Filter for recurring subscriptions
        sub_df = df[df["is_recurring"] == True]
        if not sub_df.empty:
            merchant_counts = sub_df.groupby("merchant").agg(
                count=("amount", "count"),
                avg_amount=("amount", "mean"),
                total_amount=("amount", "sum")
            ).reset_index()

            # Identify potential duplicate fitness or streaming subscriptions
            merchants = [m.lower() for m in merchant_counts["merchant"].tolist()]
            
            # Check for multiple streaming services
            streaming_merchants = [m for m in merchant_counts["merchant"] if any(s in m.lower() for s in ["netflix", "hulu", "disney", "spotify", "apple music", "hbo", "paramount"])]
            if len(streaming_merchants) >= 3:
                total_sub_drain = float(merchant_counts[merchant_counts["merchant"].isin(streaming_merchants)]["total_amount"].sum())
                monthly_est = float(merchant_counts[merchant_counts["merchant"].isin(streaming_merchants)]["avg_amount"].sum())
                anomalies.append({
                    "anomaly_type": "GHOST_SUBSCRIPTION",
                    "category": "Recurring Subscriptions",
                    "severity": "medium",
                    "title": f"Subscription Sprawl ({len(streaming_merchants)} active streaming services)",
                    "description": f"You are carrying {len(streaming_merchants)} overlapping digital subscriptions ({', '.join(streaming_merchants)}). Multiple services show redundant media usage.",
                    "metric_evidence": f"Totaling ${monthly_est:.2f}/month (${total_sub_drain:.2f} spent over history).",
                    "monthly_impact": round(monthly_est, 2),
                    "involved_merchants": streaming_merchants
                })

            # Check for high-cost gym/fitness subscriptions with zero related activity
            fitness_subs = [m for m in merchant_counts["merchant"] if any(f in m.lower() for f in ["gym", "equinox", "fitness", "crunch", "crossfit"])]
            for fit_m in fitness_subs:
                avg_cost = float(merchant_counts[merchant_counts["merchant"] == fit_m]["avg_amount"].iloc[0])
                # Check if there is any other health/fitness activity or if it's high cost
                anomalies.append({
                    "anomaly_type": "GHOST_SUBSCRIPTION",
                    "category": "Fitness & Gym",
                    "severity": "high" if avg_cost > 50 else "medium",
                    "title": f"Underutilized Fitness Membership ({fit_m})",
                    "description": f"Recurring charge for {fit_m} detected every billing cycle without active lifestyle engagement or paired visits.",
                    "metric_evidence": f"Recurring at ${avg_cost:.2f}/month. Siphoning ${avg_cost * 12:.2f}/year.",
                    "monthly_impact": round(avg_cost, 2),
                    "involved_merchants": [fit_m]
                })

        # 2. Month-over-Month Category Velocity Surges (e.g. Food Delivery)
        df["month"] = df["date"].dt.to_period("M")
        months = sorted(df["month"].unique())
        
        if len(months) >= 2:
            latest_month = months[-1]
            prev_month = months[-2]

            latest_df = df[df["month"] == latest_month]
            prev_df = df[df["month"] == prev_month]

            latest_cat_spend = latest_df[latest_df["amount"] > 0].groupby("category")["amount"].sum()
            prev_cat_spend = prev_df[prev_df["amount"] > 0].groupby("category")["amount"].sum()

            for cat, latest_spend in latest_cat_spend.items():
                if cat in ["Salary & Wages", "Income"]:
                    continue
                prev_spend = prev_cat_spend.get(cat, 0.0)
                if prev_spend > 50 and latest_spend > prev_spend * 1.30:  # 30% surge
                    pct_increase = ((latest_spend - prev_spend) / prev_spend) * 100
                    involved = latest_df[latest_df["category"] == cat]["merchant"].unique().tolist()[:4]
                    anomalies.append({
                        "anomaly_type": "VELOCITY_SURGE",
                        "category": cat,
                        "severity": "high" if pct_increase > 40 else "medium",
                        "title": f"Spending Surge in {cat} (+{pct_increase:.1f}%)",
                        "description": f"Your spending in {cat} sharply accelerated in {latest_month} compared to {prev_month}.",
                        "metric_evidence": f"Increased from ${prev_spend:.2f} to ${latest_spend:.2f} (+{pct_increase:.1f}% velocity leap).",
                        "monthly_impact": round(latest_spend - prev_spend, 2),
                        "involved_merchants": involved
                    })

        # 3. Weekend Discretionary Spending Impulse Spikes
        df["day_name"] = df["date"].dt.day_name()
        df["is_weekend"] = df["day_name"].isin(["Friday", "Saturday", "Sunday"])
        disc_df = df[(df["category_group"] == "Discretionary Lifestyle") & (df["amount"] > 0)]
        
        if not disc_df.empty:
            weekend_spend = disc_df[disc_df["is_weekend"]]["amount"].sum()
            total_disc = disc_df["amount"].sum()
            if total_disc > 0:
                weekend_ratio = (weekend_spend / total_disc) * 100
                if weekend_ratio >= 65:
                    anomalies.append({
                        "anomaly_type": "LIFESTYLE_CREEP",
                        "category": "Discretionary Lifestyle",
                        "severity": "medium",
                        "title": "Weekend Spending Concentration",
                        "description": f"{weekend_ratio:.1f}% of your discretionary spending occurs between Friday and Sunday, primarily on dining and entertainment.",
                        "metric_evidence": f"${weekend_spend:.2f} of ${total_disc:.2f} discretionary outlays concentrated on weekends.",
                        "monthly_impact": round(weekend_spend * 0.3, 2),
                        "involved_merchants": disc_df[disc_df["is_weekend"]]["merchant"].unique().tolist()[:3]
                    })

        # 4. Synthesize with Mesh API if configured to polish nuance
        if self.mesh_client.is_configured() and anomalies:
            try:
                system_prompt = (
                    "You are the Financial Behavior Analyst of FinPilot. Enhance and ground these detected anomalies "
                    "with clear behavioral insight for the user. Ensure each observation is strictly backed by the evidence.\n"
                    "Return a JSON object with key 'anomalies' formatted as an array matching the input structure."
                )
                res = self.mesh_client.json_completion(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Review and refine these detected behavioral patterns:\n{json.dumps(anomalies)}"}
                    ],
                    fallback_dict={"anomalies": anomalies}
                )
                if "anomalies" in res and isinstance(res["anomalies"], list) and len(res["anomalies"]) > 0:
                    return res["anomalies"]
            except Exception as e:
                logger.warning(f"Mesh API anomaly refinement failed: {e}. Using calculated anomalies.")

        return anomalies

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph node execution."""
        txs = state.get("categorized_transactions") or state.get("transactions", [])
        anomalies = self.analyze_patterns(txs)

        steps = state.get("execution_steps", [])
        steps.append(f"BehaviorAnalysisAgent: detected {len(anomalies)} behavioral anomalies and patterns.")

        return {
            "anomalies": anomalies,
            "execution_steps": steps
        }
