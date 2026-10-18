"""APScheduler Background Service: Automated Proactive Digests & Alerts.

Periodically evaluates transactions and forecasts in the background,
generating weekly / periodic proactive digests with a single key forward insight
and an immediate action item.
"""

import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from finpilot.config import settings
from finpilot.database import SessionLocal, DBTransaction, DBGoal, DBRecommendation, DBDigest
from finpilot.agents.orchestrator import get_orchestrator
from finpilot.models.schemas import ProactiveDigest, Recommendation

logger = logging.getLogger("finpilot.scheduler")


class DigestSchedulerService:
    """Manages scheduled background proactive analysis cycles."""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.latest_digest: Optional[Dict[str, Any]] = None

    def start(self):
        """Start background scheduler."""
        if not self.scheduler.running:
            self.scheduler.add_job(
                func=self.generate_scheduled_digest,
                trigger=IntervalTrigger(hours=settings.DIGEST_INTERVAL_HOURS),
                id="proactive_digest_job",
                name="Generate Proactive Financial Digest",
                replace_existing=True,
            )
            self.scheduler.start()
            logger.info("DigestScheduler started successfully.")

    def shutdown(self):
        """Shutdown background scheduler cleanly."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("DigestScheduler shut down.")

    def generate_scheduled_digest(self) -> Optional[Dict[str, Any]]:
        """Run background digest generation cycle."""
        logger.info("Running background proactive digest cycle...")
        db = SessionLocal()
        try:
            # Load transactions from DB
            db_txs = db.query(DBTransaction).all()
            if not db_txs:
                logger.info("No transactions found in database for digest.")
                return None

            tx_dicts = [
                {
                    "id": t.id,
                    "date": t.date,
                    "amount": t.amount,
                    "merchant": t.merchant,
                    "description": t.description,
                    "category": t.category,
                    "category_group": t.category_group,
                    "is_recurring": t.is_recurring,
                    "is_anomaly": t.is_anomaly
                }
                for t in db_txs
            ]

            # Load active goals
            db_goals = db.query(DBGoal).all()
            goal_dicts = [
                {
                    "id": g.id,
                    "name": g.name,
                    "target_amount": g.target_amount,
                    "current_amount": g.current_amount,
                    "target_date": g.target_date,
                    "priority": g.priority,
                    "status": g.status
                }
                for g in db_goals
            ]

            # Run Multi-Agent Orchestrator
            orchestrator = get_orchestrator()
            pipeline_result = orchestrator.run_full_pipeline(
                transactions=tx_dicts,
                current_balance=5000.0,
                goals=goal_dicts
            )

            forecast = pipeline_result.get("forecast", {})
            anomalies = pipeline_result.get("anomalies", [])
            recommendations = pipeline_result.get("recommendations", [])

            # Compute Financial Health Score (0 - 100)
            savings_rate = forecast.get("projected_savings_rate", 10.0)
            health = int(min(100, max(20, 60 + (savings_rate * 1.5) - (len(anomalies) * 8))))

            # Formulate key forward insight
            end_bal = forecast.get("projected_end_balance", 5000.0)
            if anomalies:
                top_anom = anomalies[0]
                insight = (
                    f"90-Day Trajectory: You are on path to reach ${end_bal:,.2f}, but "
                    f"{top_anom.get('title')} is draining ${top_anom.get('monthly_impact', 0.0):.2f}/mo. "
                    f"Taking immediate action protects your runway buffer."
                )
            else:
                insight = (
                    f"90-Day Trajectory: Stable cashflow projected to finish at ${end_bal:,.2f} "
                    f"with a {savings_rate:.1f}% savings rate. All buffers intact."
                )

            top_rec = recommendations[0] if recommendations else {
                "id": "REC-DEF-001",
                "title": "Maintain Reserve Buffer",
                "action": "Keep monthly savings rate above 20%.",
                "category": "Savings & Investments",
                "priority": "medium",
                "projected_monthly_savings": 0.0,
                "projected_annual_savings": 0.0,
                "trigger_type": "BASELINE_MONITOR",
                "confidence_score": 0.9,
                "reasoning_trail": "Stable financial metrics detected.",
                "evidence_data": {},
                "status": "pending"
            }

            digest_payload = {
                "generated_at": datetime.utcnow().isoformat(),
                "health_score": health,
                "key_forward_insight": insight,
                "primary_action": top_rec,
                "secondary_actions": recommendations[1:4] if len(recommendations) > 1 else [],
                "forecast_summary": f"Burn rate: ${forecast.get('monthly_burn_rate', 0.0):,.2f}/mo. End balance: ${end_bal:,.2f}.",
                "goals_progress": goal_dicts
            }

            # Save digest to DB
            db_digest = DBDigest(
                generated_at=datetime.utcnow(),
                health_score=health,
                key_forward_insight=insight,
                top_action_id=top_rec.get("id"),
                full_digest_json=json.dumps(digest_payload)
            )
            db.add(db_digest)
            db.commit()

            self.latest_digest = digest_payload
            logger.info("Proactive digest generated and persisted successfully.")
            return digest_payload
        except Exception as e:
            logger.error(f"Error generating scheduled digest: {e}")
            return None
        finally:
            db.close()


# Scheduler singleton
_scheduler_service: Optional[DigestSchedulerService] = None


def get_digest_scheduler() -> DigestSchedulerService:
    """Retrieve or create the DigestSchedulerService singleton."""
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = DigestSchedulerService()
    return _scheduler_service
