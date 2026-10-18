"""Self-evaluation exports."""

from finpilot.evaluation.benchmark_data import (
    GROUND_TRUTH_TRANSACTIONS,
    GROUND_TRUTH_WHAT_IF_SCENARIOS,
)
from finpilot.evaluation.evaluate import run_self_evaluation

__all__ = [
    "GROUND_TRUTH_TRANSACTIONS",
    "GROUND_TRUTH_WHAT_IF_SCENARIOS",
    "run_self_evaluation",
]
