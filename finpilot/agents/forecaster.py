"""Forecasting Agent: Generates forward-looking cashflow and savings projections.

Projects daily financial trajectory across 30, 60, and 90 days based on:
- Recurring income cadences (payroll)
- Fixed obligations (rent, utilities, active subscriptions on bill dates)
- Stochastic variable living burn rate
- Minimum cash safety buffer analysis
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd

from finpilot.models.schemas import ForecastPoint, ForecastResult

logger = logging.getLogger("finpilot.agents.forecaster")


class ForecastingAgent:
    """Agent that projects forward cashflow balances and detects runway/safety risks."""

    def __init__(self, projection_days: int = 90):
        self.projection_days = projection_days

    def compute_forecast(
        self,
        transactions: List[Dict[str, Any]],
        start_balance: float = 5000.0
    ) -> Dict[str, Any]:
        """Generate daily cashflow projections."""
        if not transactions:
            return {
                "projection_days": self.projection_days,
                "start_balance": start_balance,
                "projected_end_balance": start_balance,
                "monthly_burn_rate": 0.0,
                "monthly_recurring_fixed": 0.0,
                "monthly_variable_spend": 0.0,
                "projected_savings_rate": 0.0,
                "runway_days": None,
                "trajectory_points": [],
                "key_risks": ["Insufficient transaction data to establish forecast."]
            }

        df = pd.DataFrame(transactions)
        df["date"] = pd.to_datetime(df["date"])
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        if "category_group" not in df.columns:
            df["category_group"] = "Discretionary Lifestyle"
        if "is_recurring" not in df.columns:
            df["is_recurring"] = False

        # 1. Calculate Monthly Inflows (Salary / Income)
        # Income is recorded either as negative amount or category Income / Salary
        income_df = df[(df["amount"] < 0) | (df["category_group"] == "Income")]
        if not income_df.empty:
            total_income = abs(income_df["amount"].sum())
            days_span = max(1, (df["date"].max() - df["date"].min()).days)
            monthly_income = (total_income / days_span) * 30.4
        else:
            monthly_income = 4500.0  # sensible default baseline

        # 2. Decompose Expenses into Fixed vs Variable
        expense_df = df[(df["amount"] > 0) & (df["category_group"] != "Income")]
        days_span = max(1, (df["date"].max() - df["date"].min()).days)

        fixed_df = expense_df[expense_df["is_recurring"] == True]
        variable_df = expense_df[expense_df["is_recurring"] == False]

        monthly_fixed = (fixed_df["amount"].sum() / days_span) * 30.4 if not fixed_df.empty else 1800.0
        monthly_variable = (variable_df["amount"].sum() / days_span) * 30.4 if not variable_df.empty else 1600.0
        monthly_burn = monthly_fixed + monthly_variable

        daily_variable = monthly_variable / 30.4

        # Net monthly savings
        net_monthly_cashflow = monthly_income - monthly_burn
        savings_rate = (net_monthly_cashflow / monthly_income * 100) if monthly_income > 0 else 0.0

        # Runway calculation
        runway_days = (start_balance / (monthly_burn / 30.4)) if net_monthly_cashflow < 0 and monthly_burn > 0 else None

        # 3. Simulate Forward Daily Balances
        today = datetime.now()
        current_bal = float(start_balance)
        trajectory: List[Dict[str, Any]] = []
        min_balance = current_bal
        min_bal_day = None

        key_risks: List[str] = []

        # Known recurring bills calendar mapping
        # E.g. Rent on 1st, Utilities on 15th, Salary on 1st and 15th (or monthly)
        salary_per_check = monthly_income / 2.0  # bi-weekly assumption
        rent_amount = monthly_fixed * 0.70       # approx 70% of fixed is rent/mortgage
        other_fixed_daily = (monthly_fixed * 0.30) / 30.4

        for d in range(self.projection_days):
            current_date = today + timedelta(days=d)
            day_of_month = current_date.day
            is_weekend = current_date.weekday() in [5, 6]

            daily_in = 0.0
            daily_out = 0.0

            # Paycheck on 1st and 15th
            if day_of_month in [1, 15]:
                daily_in += salary_per_check

            # Rent on 1st
            if day_of_month == 1:
                daily_out += rent_amount

            # Other fixed prorated
            daily_out += other_fixed_daily

            # Variable spend (slightly higher on weekends)
            v_spend = daily_variable * 1.35 if is_weekend else daily_variable * 0.85
            daily_out += v_spend

            net_change = daily_in - daily_out
            current_bal += net_change

            if current_bal < min_balance:
                min_balance = current_bal
                min_bal_day = current_date.strftime("%Y-%m-%d")

            trajectory.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "baseline_balance": round(current_bal, 2),
                "simulated_balance": round(current_bal, 2),
                "projected_income": round(daily_in, 2),
                "projected_expense": round(daily_out, 2),
                "net_daily_change": round(net_change, 2)
            })

        # Assess Risks
        if min_balance < 1000:
            key_risks.append(
                f"Emergency buffer risk: Cash balance projected to dip to ${min_balance:.2f} on {min_bal_day}."
            )
        if net_monthly_cashflow < 0:
            key_risks.append(
                f"Deficit warning: Spending exceeds income by ${abs(net_monthly_cashflow):.2f}/month."
            )
        if savings_rate < 15.0 and savings_rate >= 0:
            key_risks.append(
                f"Low savings buffer: Current trajectory yields only {savings_rate:.1f}% savings rate."
            )

        return {
            "projection_days": self.projection_days,
            "start_balance": round(start_balance, 2),
            "projected_end_balance": round(current_bal, 2),
            "monthly_burn_rate": round(monthly_burn, 2),
            "monthly_recurring_fixed": round(monthly_fixed, 2),
            "monthly_variable_spend": round(monthly_variable, 2),
            "projected_savings_rate": round(savings_rate, 1),
            "runway_days": round(runway_days, 1) if runway_days else None,
            "trajectory_points": trajectory,
            "key_risks": key_risks
        }

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph node execution."""
        txs = state.get("categorized_transactions") or state.get("transactions", [])
        start_bal = state.get("current_balance", 5000.0)

        forecast = self.compute_forecast(txs, start_balance=start_bal)
        steps = state.get("execution_steps", [])
        steps.append(
            f"ForecastingAgent: projected {self.projection_days}-day trajectory "
            f"(end balance: ${forecast['projected_end_balance']:,.2f}, savings rate: {forecast['projected_savings_rate']}%)."
        )

        return {
            "forecast": forecast,
            "execution_steps": steps
        }
