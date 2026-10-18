"""FastAPI REST API Endpoints for FinPilot."""

import io
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from finpilot.database import get_db, DBTransaction, DBGoal, DBRecommendation, DBDigest
from finpilot.models.schemas import (
    Transaction,
    FinancialGoal,
    WhatIfScenario,
    WhatIfSimulationResult,
    Recommendation,
    ChatRequest,
    ChatResponse,
    ProactiveDigest
)
from finpilot.agents.orchestrator import get_orchestrator
from finpilot.scheduler.digest_scheduler import get_digest_scheduler
from finpilot.evaluation.evaluate import run_self_evaluation

logger = logging.getLogger("finpilot.api")
router = APIRouter(prefix="/api", tags=["FinPilot"])


@router.post("/transactions/upload")
async def upload_transactions_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload CSV containing columns: date, amount, merchant, description."""
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        required_cols = {"date", "amount", "merchant"}
        if not required_cols.issubset(set(df.columns)):
            raise HTTPException(
                status_code=400,
                detail=f"CSV must include columns: {required_cols}. Found: {list(df.columns)}"
            )

        # Clear existing transactions for clean demonstration
        db.query(DBTransaction).delete()
        db.commit()

        # Ingest and classify transactions through Categorization Agent
        orchestrator = get_orchestrator()
        raw_txs = df.to_dict(orient="records")
        for tx in raw_txs:
            if "description" not in tx or pd.isna(tx["description"]):
                tx["description"] = ""
            tx["amount"] = float(tx["amount"])

        categorized = orchestrator.categorizer.categorize_batch(raw_txs)

        # Persist to database
        db_records = []
        for c in categorized:
            db_records.append(
                DBTransaction(
                    date=str(c["date"]),
                    amount=float(c["amount"]),
                    merchant=str(c["merchant"]),
                    description=str(c.get("description", "")),
                    category=c.get("category", "General Expense"),
                    category_group=c.get("category_group", "Discretionary Lifestyle"),
                    is_recurring=bool(c.get("is_recurring", False)),
                    is_anomaly=bool(c.get("is_anomaly", False)),
                    anomaly_reason=c.get("anomaly_reason")
                )
            )
        db.add_all(db_records)
        db.commit()

        return {
            "message": f"Successfully ingested and categorized {len(db_records)} transactions.",
            "count": len(db_records)
        }
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transactions/load-sample")
def load_sample_dataset(db: Session = Depends(get_db)):
    """Pre-load rich 2-month realistic dataset with seeded anomalies."""
    try:
        csv_path = "data/sample_transactions.csv"
        df = pd.read_csv(csv_path)

        db.query(DBTransaction).delete()
        db.commit()

        orchestrator = get_orchestrator()
        raw_txs = df.to_dict(orient="records")
        for tx in raw_txs:
            if "description" not in tx or pd.isna(tx["description"]):
                tx["description"] = ""
            tx["amount"] = float(tx["amount"])

        categorized = orchestrator.categorizer.categorize_batch(raw_txs)

        db_records = []
        for c in categorized:
            db_records.append(
                DBTransaction(
                    date=str(c["date"]),
                    amount=float(c["amount"]),
                    merchant=str(c["merchant"]),
                    description=str(c.get("description", "")),
                    category=c.get("category", "General Expense"),
                    category_group=c.get("category_group", "Discretionary Lifestyle"),
                    is_recurring=bool(c.get("is_recurring", False)),
                    is_anomaly=bool(c.get("is_anomaly", False)),
                    anomaly_reason=c.get("anomaly_reason")
                )
            )
        db.add_all(db_records)

        # Also add default financial goals if none exist
        if db.query(DBGoal).count() == 0:
            db.add_all([
                DBGoal(
                    name="Emergency Reserve Fund",
                    target_amount=6000.0,
                    current_amount=3800.0,
                    target_date="2026-12-31",
                    priority="high",
                    status="on_track"
                ),
                DBGoal(
                    name="Japan Vacation",
                    target_amount=3200.0,
                    current_amount=1200.0,
                    target_date="2027-03-31",
                    priority="medium",
                    status="on_track"
                )
            ])

        db.commit()
        return {"message": "Sample transactions & goals loaded successfully.", "count": len(db_records)}
    except Exception as e:
        logger.error(f"Load sample failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions")
def list_transactions(db: Session = Depends(get_db)):
    """List all stored transactions."""
    txs = db.query(DBTransaction).order_by(DBTransaction.date.desc()).all()
    return [
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
        for t in txs
    ]


@router.post("/pipeline/run")
def run_orchestrator_pipeline(
    balance: float = 5200.0,
    db: Session = Depends(get_db)
):
    """Run full LangGraph multi-agent pipeline."""
    txs = db.query(DBTransaction).all()
    if not txs:
        # Load sample if empty
        load_sample_dataset(db)
        txs = db.query(DBTransaction).all()

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
        for t in txs
    ]

    goals = db.query(DBGoal).all()
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
        for g in goals
    ]

    orchestrator = get_orchestrator()
    result = orchestrator.run_full_pipeline(
        transactions=tx_dicts,
        current_balance=balance,
        goals=goal_dicts
    )

    # Persist recommendations to DB
    recs = result.get("recommendations", [])
    db.query(DBRecommendation).delete()
    for r in recs:
        db.add(
            DBRecommendation(
                id=r["id"],
                title=r["title"],
                action=r["action"],
                category=r["category"],
                priority=r["priority"],
                projected_monthly_savings=float(r.get("projected_monthly_savings", 0.0)),
                projected_annual_savings=float(r.get("projected_annual_savings", 0.0)),
                trigger_type=r["trigger_type"],
                confidence_score=float(r.get("confidence_score", 0.9)),
                reasoning_trail=r["reasoning_trail"],
                evidence_data=json.dumps(r.get("evidence_data", {})),
                status=r.get("status", "pending")
            )
        )
    db.commit()

    return {
        "anomalies": result.get("anomalies", []),
        "forecast": result.get("forecast", {}),
        "recommendations": recs,
        "execution_steps": result.get("execution_steps", [])
    }


@router.post("/simulate")
def simulate_decision(
    scenario: WhatIfScenario,
    start_balance: float = 5200.0,
    db: Session = Depends(get_db)
):
    """Simulate a what-if scenario against the forecast."""
    txs = db.query(DBTransaction).all()
    tx_dicts = [
        {
            "id": t.id,
            "date": t.date,
            "amount": t.amount,
            "merchant": t.merchant,
            "description": t.description,
            "category": t.category,
            "category_group": t.category_group,
            "is_recurring": t.is_recurring
        }
        for t in txs
    ]

    goals = db.query(DBGoal).all()
    goal_dicts = [
        {
            "id": g.id,
            "name": g.name,
            "target_amount": g.target_amount,
            "current_amount": g.current_amount,
            "target_date": g.target_date
        }
        for g in goals
    ]

    orchestrator = get_orchestrator()
    # Compute current baseline forecast
    forecast = orchestrator.forecaster.compute_forecast(tx_dicts, start_balance=start_balance)
    
    sim_result = orchestrator.simulate_what_if(
        scenario=scenario.model_dump(),
        forecast=forecast,
        goals=goal_dicts
    )

    return sim_result


@router.get("/digest/latest")
def get_latest_digest(db: Session = Depends(get_db)):
    """Retrieve the latest scheduled proactive digest or trigger one."""
    scheduler = get_digest_scheduler()
    if scheduler.latest_digest:
        return scheduler.latest_digest

    latest_db_digest = db.query(DBDigest).order_by(DBDigest.generated_at.desc()).first()
    if latest_db_digest:
        return json.loads(latest_db_digest.full_digest_json)

    # Generate immediately if none exists
    new_digest = scheduler.generate_scheduled_digest()
    return new_digest or {"message": "No transactions available to generate digest."}


@router.post("/chat")
def chat_copilot(
    req: ChatRequest,
    current_balance: float = 5200.0,
    db: Session = Depends(get_db)
):
    """Interactive conversational copilot grounded in user financial data."""
    txs = db.query(DBTransaction).all()
    tx_dicts = [
        {
            "id": t.id,
            "date": t.date,
            "merchant": t.merchant,
            "amount": t.amount,
            "category": t.category,
            "category_group": t.category_group,
            "is_recurring": t.is_recurring,
        }
        for t in txs
    ]

    goals = db.query(DBGoal).all()
    goal_dicts = [
        {"name": g.name, "target_amount": g.target_amount, "current_amount": g.current_amount}
        for g in goals
    ]

    orchestrator = get_orchestrator()
    forecast = orchestrator.forecaster.compute_forecast(tx_dicts, start_balance=current_balance)
    anomalies = orchestrator.analyzer.analyze_patterns(tx_dicts)
    recs = [
        {"title": r.title, "action": r.action, "priority": r.priority}
        for r in db.query(DBRecommendation).all()
    ]

    res = orchestrator.query_copilot(
        query=req.message,
        transactions=tx_dicts,
        forecast=forecast,
        anomalies=anomalies,
        recommendations=recs,
        goals=goal_dicts,
        current_balance=current_balance
    )

    return res


@router.get("/goals")
def list_goals(db: Session = Depends(get_db)):
    """List financial goals."""
    return db.query(DBGoal).all()


@router.post("/goals")
def create_goal(goal: FinancialGoal, db: Session = Depends(get_db)):
    """Create a new financial goal."""
    db_goal = DBGoal(
        name=goal.name,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        target_date=goal.target_date,
        priority=goal.priority,
        status=goal.status
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


@router.get("/evaluation/report")
def get_evaluation_report():
    """Retrieve recorded self-evaluation metrics."""
    report_file = "eval_results/evaluation_report.json"
    if os.path.exists(report_file):
        with open(report_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return run_self_evaluation()
