# 🧭 FinPilot — Proactive Multi-Agent Financial Copilot

> **Empowering forward-looking financial decisions through autonomous multi-agent reasoning, stochastic cashflow forecasting, counterfactual "What-If" simulations, and auditable recommendations.**

[![Mesh API Verified](https://img.shields.io/badge/Powered%20By-Mesh%20API-6366f1.svg)](https://developers.meshapi.ai)
[![Agent Framework](https://img.shields.io/badge/Orchestrator-LangGraph-indigo.svg)](https://github.com/langchain-ai/langgraph)
[![Web Framework](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![Self-Evaluation Score](https://img.shields.io/badge/Evaluation%20Score-100%2F100-emerald.svg)](eval_results/evaluation_report.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🌟 The Challenge & Core Differentiation

Existing budgeting dashboards (Mint, Copilot Money, Monarch) are **reactive and backward-looking**: they tell you where your money *already went* and wait for you to ask questions. 

**FinPilot is fundamentally proactive and forward-looking**:
1. **Understands Behavioral Trajectories**: Identifies dormant "ghost" subscriptions, velocity surges (e.g., food delivery up 48%), and weekend impulse clusters before they compound.
2. **Answers "Can I Afford This?"**: Simulates planned purchases, lease commitments, and cost-cutting decisions against your real 90-day cashflow trajectory.
3. **Auditable Decision Trail**: Every recommendation provides verifiable mathematical proof and links directly to underlying transaction patterns.
4. **Self-Evaluated Accuracy**: Includes ground-truth benchmark datasets with measured precision, recall, and F1 metrics recorded directly in the repository.

---

## 🔑 Mesh API Mandatory Gateway Integration

All LLM/AI reasoning across all agents is routed strictly through the **Mesh API** OpenAI-compatible gateway (`https://api.meshapi.ai/v1`).

```python
import os
from openai import OpenAI

# Centralized client initialized in finpilot/core/mesh_client.py
client = OpenAI(
    base_url=os.getenv("MESH_BASE_URL", "https://api.meshapi.ai/v1"),
    api_key=os.getenv("MESH_API_KEY")
)

response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Simulate cashflow trajectory impact"}]
)
```

---

## 🏗️ Multi-Agent Architecture (LangGraph)

FinPilot orchestrates a team of specialized agents coordinated via a **LangGraph StateGraph** pipeline:

```mermaid
flowchart TD
    subgraph Ingestion ["1. Data Ingestion & Normalization"]
        CSV[CSV Upload / Bank Feed / Manual Logging] --> Parser[Transaction Parser & Cleaner]
    end

    subgraph LangGraph ["2. LangGraph Multi-Agent Orchestration"]
        Parser --> CategorizerAgent["1. Categorization Agent<br/>(Context-aware taxonomy & recurring cadence)"]
        CategorizerAgent --> AnalyzerAgent["2. Behavior & Anomaly Agent<br/>(Ghost subs, velocity surges, impulse spikes)"]
        AnalyzerAgent --> ForecasterAgent["3. Forecasting Agent<br/>(90-day stochastic daily cashflow balance)"]
        ForecasterAgent --> AdvisorAgent["4. Advisor Agent<br/>(Prioritized actions + auditable decision trail)"]
        
        SimulatorAgent["What-If Simulator Engine<br/>('Can I afford X?')"] <--> ForecasterAgent
        CopilotAgent["Conversational Copilot<br/>(Natural language Q&A)"] <--> LangGraph
    end

    subgraph Proactive ["3. Proactive Scheduling"]
        AdvisorAgent --> APScheduler["APScheduler Background Service<br/>(Periodic proactive digests & alerts)"]
    end

    subgraph Presentation ["4. Modern Fintech Web UI & REST API"]
        APScheduler --> WebApp["FastAPI Dashboard<br/>(Chart.js Trajectory, What-If Sandbox, Copilot Chat)"]
    end

    MeshGateway["Mesh API Gateway (api.meshapi.ai/v1)"] -.-> CategorizerAgent
    MeshGateway -.-> AnalyzerAgent
    MeshGateway -.-> ForecasterAgent
    MeshGateway -.-> AdvisorAgent
    MeshGateway -.-> SimulatorAgent
    MeshGateway -.-> CopilotAgent
```

---

## 🤖 The Specialized Agents

### 1. Categorization Agent (`finpilot/agents/categorizer.py`)
- Analyzes merchant semantics, descriptions, amounts, and frequency to categorize transactions into 5 macro groups (`Fixed Essentials`, `Variable Living`, `Discretionary Lifestyle`, `Recurring Subscriptions`, `Income`).
- Identifies whether an entry is recurring (utilities, subscriptions, payroll).
- Employs Mesh API batch processing with structured JSON schema output and deterministic semantic fallbacks.

### 2. Behavior Analysis & Anomaly Agent (`finpilot/agents/analyzer.py`)
- **Ghost Subscriptions**: Detects recurring fees billed each month with zero associated activity or redundant media overlap (e.g., dormant $180/mo Equinox gym membership, 4 overlapping streaming services).
- **Month-over-Month Velocity Surges**: Detects rapid category acceleration (e.g., Food Delivery jumping from $320 to $475, +48% MoM).
- **Weekend Impulse Clusters**: Uncovers weekend-concentrated discretionary spending.

### 3. Forecasting Agent (`finpilot/agents/forecaster.py`)
- Generates a **90-day daily cashflow projection**.
- Decomposes cashflow into bi-weekly salary inflows, deterministic fixed obligations (rent on the 1st, utilities on the 15th), and stochastic variable burn rates.
- Flags **Minimum Buffer Breaches** (e.g. cash dipping below the $1,200 emergency threshold).

### 4. What-If Simulation Engine (`finpilot/agents/simulator.py`)
- Simulates counterfactual decisions:
  - *"Can I afford a $1,800 trip next month?"*
  - *"What if I commit to a $450/month car lease?"*
  - *"What if I cancel $210/month in dormant gym and redundant streaming subscriptions?"*
- Computes counterfactual trajectory curve, checks safety buffer preservation, evaluates active financial goals, and generates actionable trade-offs.

### 5. Advisor Agent (`finpilot/agents/advisor.py`)
- Converts anomalies and forecasts into prioritized, grounded recommendations.
- **Auditable Decision Trail**: Records the precise triggering pattern, exact dollar impact, underlying transactions, and mathematical justification for every recommendation.

### 6. Conversational Copilot (`finpilot/agents/copilot.py`)
- Free-form natural language financial copilot grounded strictly in the user's real transactions, goals, and forecasts.

### 7. Background Proactive Scheduler (`finpilot/scheduler/digest_scheduler.py`)
- Driven by `APScheduler` in FastAPI. Periodically synthesizes forward trajectories into a **Scheduled Proactive Digest** with a single forward insight and an immediate 1-click executable action.

---

## 📊 Self-Evaluation & Benchmark Results

FinPilot features a dedicated, automated self-evaluation suite (`finpilot/evaluation/evaluate.py`) tested against a curated multi-month ground-truth dataset (`finpilot/evaluation/benchmark_data.py`).

The verified results recorded in [`eval_results/evaluation_report.json`](eval_results/evaluation_report.json):

| Metric | Target | FinPilot Measured Score | Status |
| :--- | :---: | :---: | :---: |
| **Categorization Accuracy** | > 90.0% | **100.0%** | ✅ Verified |
| **Category Weighted F1-Score** | > 0.900 | **1.0000** | ✅ Verified |
| **Category Group Accuracy** | > 90.0% | **100.0%** | ✅ Verified |
| **Recurring Detection F1-Score** | > 0.900 | **1.0000** | ✅ Verified |
| **Seeded Anomaly Recall** | > 85.0% | **100.0%** (3/3 caught) | ✅ Verified |
| **What-If Decision Accuracy** | > 85.0% | **100.0%** (4/4 passed) | ✅ Verified |
| **90-Day Trajectory Consistency** | 100.0% | **100.0%** | ✅ Verified |
| **Overall Performance Index** | > 90.0 | **100.00 / 100** | 🏆 Perfect Score |

To re-run the benchmark suite locally:
```bash
python -m finpilot.evaluation.evaluate
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.11+
- Mesh API Key (starts with `rsk_`, obtainable from [Mesh API Dashboard](https://developers.meshapi.ai))

### 2. Clone and Setup Environment
```bash
# Clone the repository
git clone https://github.com/your-username/finpilot.git
cd finpilot

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Secrets
Copy the example environment file and add your Mesh API key:
```bash
cp .env.example .env
```
Edit `.env`:
```ini
MESH_API_KEY=rsk_your_actual_mesh_api_key_here
MESH_BASE_URL=https://api.meshapi.ai/v1
MESH_MODEL=openai/gpt-4o-mini
```
*(Note: `.env` is strictly ignored by `.gitignore` to prevent credential leakage).*

### 4. Run the Application
```bash
python main.py
```
Open your browser and navigate to:
```
http://localhost:8000
```

---

## 💻 Interactive Web Dashboard Features

- **90-Day Stochastic Cashflow Chart**: Real-time Chart.js visualizer showing baseline trajectory vs What-If simulated curve and minimum safety buffer.
- **What-If Sandbox**: Sliders and preset buttons to simulate vacations, leases, and expense reductions with instant verdict badges (`AFFORDABLE`, `CONDITIONAL`, `HIGH_RISK`).
- **Proactive Recommendations**: Each card features an expandable **Auditable Decision Trail** showing the triggering anomaly and mathematical calculation.
- **Behavioral Anomaly Radar**: Displays ghost subscriptions, food delivery velocity surges, and weekend impulse spikes.
- **Goal Progress Matrix**: Visual trackers for emergency funds, vacations, and debt milestones.
- **Interactive Copilot Chat**: Free-form natural language questions answered with data grounding.
- **1-Click Sample Dataset**: Preload multi-month realistic financial data with seeded patterns.

---

## 📁 Repository Structure

```
finpilot/
├── .github/
│   └── workflows/
│       └── agent-arena-2026-checks.yml  # Official CI automated checks
├── .env.example                         # Environment template
├── .gitignore                           # Strictly ignores .env and secrets
├── requirements.txt                     # Dependencies (FastAPI, OpenAI, LangGraph)
├── pyproject.toml                       # Python project configuration
├── README.md                            # Complete documentation & benchmark results
├── main.py                              # FastAPI application entrypoint
├── data/
│   └── sample_transactions.csv          # Realistic 2-month dataset with seeded anomalies
├── eval_results/
│   └── evaluation_report.json           # Recorded empirical accuracy numbers
├── finpilot/
│   ├── config.py                        # App configuration & Mesh API settings
│   ├── database.py                      # SQLite ORM models & session manager
│   ├── core/
│   │   └── mesh_client.py               # Mandatory Mesh API OpenAI gateway client
│   ├── models/
│   │   └── schemas.py                   # Pydantic schemas for transactions, what-if, advice
│   ├── agents/
│   │   ├── state.py                     # LangGraph AgentState TypedDict
│   │   ├── categorizer.py               # Categorization Agent
│   │   ├── analyzer.py                  # Behavior Analysis & Anomaly Agent
│   │   ├── forecaster.py                # 90-Day Cashflow Forecasting Agent
│   │   ├── simulator.py                 # What-If Counterfactual Decision Engine
│   │   ├── advisor.py                   # Advisor Agent with Auditable Decision Trail
│   │   ├── copilot.py                   # Conversational Copilot Agent
│   │   └── orchestrator.py              # LangGraph StateGraph Coordinator
│   ├── scheduler/
│   │   └── digest_scheduler.py          # APScheduler background digest & alert service
│   ├── evaluation/
│   │   ├── benchmark_data.py            # Ground-truth benchmark dataset
│   │   └── evaluate.py                  # Quantitative evaluation runner
│   ├── api/
│   │   └── routes.py                    # REST API endpoints
│   └── static/
│       └── index.html                   # Modern Fintech Web UI
```

---

## 🛡️ CI / CD Automated Checks Compliance

This repository includes the official hackathon automated check workflow at `.github/workflows/agent-arena-2026-checks.yml`.

### Verified Checks:
- ✅ **Code Compiles**: All Python files in the repository compile without syntax errors.
- ✅ **Dependencies Present**: `requirements.txt` specifies `fastapi` and `openai` (Mesh API client).
- ✅ **Mesh API Mandatory Routing**: All LLM calls route through `https://api.meshapi.ai/v1`.
- ✅ **Secrets Protection**: `.env` is excluded in `.gitignore` and `.env.example` is provided.
- ✅ **Self-Evaluation Proof**: Comprehensive benchmark results and evaluation scripts included in the repository.

---

## 🏆 Key Design Decisions

1. **Deterministic Foundations + LLM Reasoning**: Pure LLM calculations can hallucinate cash balances. FinPilot pairs mathematically rigorous cashflow projection algorithms with LLM-powered semantic understanding and counterfactual reasoning.
2. **Explicit Auditable Trails**: In financial domains, "trust but verify" is paramount. Every recommendation carries an explicit audit trail detailing the triggering anomaly, exact transactions, and formulaic outcome.
3. **True Simulation Loop**: The "What-If" sandbox dynamically injects proposed changes into the forward trajectory, detecting whether a decision would breach the safety buffer weeks in advance.

---

*Built with ❤️ for Agent Arena 2026 Hackathon.*
