"""Categorization Agent: Intelligently labels transactions into functional financial buckets.

Uses Mesh API to perform context-aware classification based on merchant semantics,
transaction description, amount, and recurring cadence.
"""

import json
import logging
from typing import List, Dict, Any
from finpilot.core.mesh_client import get_mesh_client

logger = logging.getLogger("finpilot.agents.categorizer")

TAXONOMY = {
    "Fixed Essentials": [
        "Rent & Housing",
        "Utilities",
        "Insurance",
        "Healthcare",
        "Debt & Loans"
    ],
    "Variable Living": [
        "Groceries",
        "Transportation",
        "Household Supplies",
        "Fuel & Charging"
    ],
    "Discretionary Lifestyle": [
        "Dining Out & Delivery",
        "Coffee & Cafes",
        "Shopping & Apparel",
        "Entertainment & Leisure",
        "Travel & Lodging"
    ],
    "Recurring Subscriptions": [
        "Digital Streaming",
        "SaaS & Software",
        "Fitness & Gym",
        "Club & News Membership"
    ],
    "Income": [
        "Salary & Wages",
        "Freelance & Consulting",
        "Investment Dividend",
        "Refunds & Reimbursements"
    ]
}


def rule_based_fallback_categorize(tx: Dict[str, Any]) -> Dict[str, Any]:
    """Robust semantic heuristic fallback when LLM is unavailable."""
    merchant = str(tx.get("merchant", "")).lower()
    desc = str(tx.get("description", "")).lower()
    combined = f"{merchant} {desc}"
    amount = float(tx.get("amount", 0.0))

    if amount < 0 or any(k in combined for k in ["payroll", "salary", "employer", "deposit", "direct dep", "dividend", "neft salary", "imps salary"]):
        return {
            "category": "Salary & Wages" if "salary" in combined or "payroll" in combined else "Income",
            "category_group": "Income",
            "is_recurring": True if "payroll" in combined or "salary" in combined else False,
            "confidence": 0.95,
            "reasoning": "Negative amount or payroll/salary keywords detected"
        }

    # Fixed Essentials (Rent, Maintenance, Utilities)
    if any(k in combined for k in ["rent", "lease", "property mgmt", "nobroker", "mygate", "society maintenance", "apartments"]):
        return {
            "category": "Rent & Housing",
            "category_group": "Fixed Essentials",
            "is_recurring": True,
            "confidence": 0.98,
            "reasoning": "Housing / Rent or Society Maintenance match"
        }
    if any(k in combined for k in ["electric", "water", "coned", "bescom", "tata power", "adani electricity", "cesc", "act fibernet", "jio fiber", "jiofiber", "airtel", "jio", "utilities", "broadband"]):
        return {
            "category": "Utilities",
            "category_group": "Fixed Essentials",
            "is_recurring": True,
            "confidence": 0.92,
            "reasoning": "Indian utility/telecom/broadband provider identified"
        }

    # Subscriptions & Fitness
    if any(k in combined for k in ["netflix", "spotify", "hotstar", "disney+ hotstar", "sonyliv", "zee5", "jiocinema", "amazon prime", "prime video", "youtube premium", "apple.com/bill"]):
        return {
            "category": "Digital Streaming",
            "category_group": "Recurring Subscriptions",
            "is_recurring": True,
            "confidence": 0.97,
            "reasoning": "Recognized OTT/digital streaming subscription"
        }
    if any(k in combined for k in ["cult.fit", "cult fit", "cultpass", "gym", "gold's gym", "anytime fitness", "equinox", "crunch", "crossfit"]):
        return {
            "category": "Fitness & Gym",
            "category_group": "Recurring Subscriptions",
            "is_recurring": True,
            "confidence": 0.95,
            "reasoning": "Fitness club / Cult.fit membership"
        }
    if any(k in combined for k in ["github", "openai", "aws", "notion", "adobe", "google one", "icloud"]):
        return {
            "category": "SaaS & Software",
            "category_group": "Recurring Subscriptions",
            "is_recurring": True,
            "confidence": 0.94,
            "reasoning": "Software/cloud recurring subscription"
        }

    # Food Delivery & Dining
    if any(k in combined for k in ["swiggy", "zomato", "eatclub", "box8", "doordash", "ubereats", "uber eats"]):
        return {
            "category": "Dining Out & Delivery",
            "category_group": "Discretionary Lifestyle",
            "is_recurring": False,
            "confidence": 0.98,
            "reasoning": "Food delivery service platform (Swiggy/Zomato)"
        }
    if any(k in combined for k in ["third wave coffee", "blue tokai", "chai point", "chaayos", "starbucks", "dunkin", "blue bottle", "coffee"]):
        return {
            "category": "Coffee & Cafes",
            "category_group": "Discretionary Lifestyle",
            "is_recurring": False,
            "confidence": 0.94,
            "reasoning": "Cafe / Coffee & Chai chain"
        }
    if any(k in combined for k in ["restaurant", "bistro", "biryani", "dhaba", "barbeque nation", "domino", "mcdonald", "burger", "pizza", "sushi", "chipotle", "bowl", "haldiram"]):
        return {
            "category": "Dining Out & Delivery",
            "category_group": "Discretionary Lifestyle",
            "is_recurring": False,
            "confidence": 0.90,
            "reasoning": "Restaurant dining"
        }


    # Groceries & Quick Commerce
    if any(k in combined for k in ["zepto", "blinkit", "instamart", "bigbasket", "bb daily", "dmart", "nature's basket", "reliance fresh", "more retail", "trader joe", "whole foods", "safeway", "supermarket", "groceries"]):
        return {
            "category": "Groceries",
            "category_group": "Variable Living",
            "is_recurring": False,
            "confidence": 0.95,
            "reasoning": "Quick commerce / Supermarket grocery retailer"
        }

    # Transportation & Fuel
    if any(k in combined for k in ["ola", "rapido", "namma yatri", "uber", "indian oil", "bharat petroleum", "hpcl", "shell", "metro", "fuel"]):
        return {
            "category": "Transportation",
            "category_group": "Variable Living",
            "is_recurring": False,
            "confidence": 0.90,
            "reasoning": "Indian rideshare / fuel / metro transit service"
        }

    # Investments
    if any(k in combined for k in ["zerodha", "groww", "kuvera", "mutual fund", "sip", "uti mf", "hdfc mf", "icici pru"]):
        return {
            "category": "Investments & SIP",
            "category_group": "Income",
            "is_recurring": True,
            "confidence": 0.95,
            "reasoning": "Investment platform or SIP auto-debit"
        }

    # Default Discretionary / Shopping
    return {
        "category": "Shopping & Apparel" if any(k in combined for k in ["myntra", "flipkart", "amazon", "ajio", "nykaa", "zara", "nike"]) else "General Expense",
        "category_group": "Discretionary Lifestyle",
        "is_recurring": False,
        "confidence": 0.75,
        "reasoning": "Discretionary shopping / retail expense"
    }



class CategorizationAgent:
    """Agent that classifies raw transactions using Mesh API."""

    def __init__(self):
        self.mesh_client = get_mesh_client()

    def categorize_batch(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Categorize a batch of transactions using Mesh API, with fallback."""
        if not transactions:
            return []

        # If Mesh API key is available, call Mesh API
        if self.mesh_client.is_configured():
            try:
                system_prompt = (
                    "You are the Categorization Agent of FinPilot. Your job is to classify "
                    "financial transactions into accurate categories and groups based strictly on transaction data.\n"
                    f"Available Taxonomies:\n{json.dumps(TAXONOMY, indent=2)}\n\n"
                    "For each transaction, return a JSON object with a key 'results' which is a list of objects containing:\n"
                    "- id: original transaction id or index\n"
                    "- category: exact category from taxonomy\n"
                    "- category_group: exact group ('Fixed Essentials', 'Variable Living', 'Discretionary Lifestyle', 'Recurring Subscriptions', 'Income')\n"
                    "- is_recurring: boolean (true if recurring subscription, rent, payroll, utility)\n"
                    "- confidence: float 0.0 to 1.0\n"
                    "- reasoning: one sentence explaining why this was chosen\n"
                )

                simplified_txs = [
                    {
                        "id": tx.get("id", idx),
                        "date": tx.get("date"),
                        "merchant": tx.get("merchant"),
                        "amount": tx.get("amount"),
                        "description": tx.get("description", "")
                    }
                    for idx, tx in enumerate(transactions)
                ]

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Classify these transactions:\n{json.dumps(simplified_txs)}"}
                ]

                res = self.mesh_client.json_completion(messages=messages)
                results_list = res.get("results", [])
                res_map = {item["id"]: item for item in results_list if "id" in item}

                categorized = []
                for idx, tx in enumerate(transactions):
                    tx_id = tx.get("id", idx)
                    if tx_id in res_map:
                        item = res_map[tx_id]
                        new_tx = dict(tx)
                        new_tx["category"] = item.get("category", "General Expense")
                        new_tx["category_group"] = item.get("category_group", "Discretionary Lifestyle")
                        new_tx["is_recurring"] = item.get("is_recurring", False)
                        new_tx["confidence"] = item.get("confidence", 0.9)
                        new_tx["reasoning"] = item.get("reasoning", "")
                        categorized.append(new_tx)
                    else:
                        # Fallback for missing item
                        fb = rule_based_fallback_categorize(tx)
                        new_tx = dict(tx)
                        new_tx.update(fb)
                        categorized.append(new_tx)
                return categorized
            except Exception as e:
                logger.warning(f"Mesh API categorizer encountered: {e}. Utilizing fallback heuristics.")

        # Fallback heuristic categorization
        categorized = []
        for tx in transactions:
            fb = rule_based_fallback_categorize(tx)
            new_tx = dict(tx)
            new_tx.update(fb)
            categorized.append(new_tx)
        return categorized

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """LangGraph node execution."""
        txs = state.get("transactions", [])
        categorized = self.categorize_batch(txs)
        
        steps = state.get("execution_steps", [])
        steps.append(f"CategorizationAgent: processed and labeled {len(categorized)} transactions.")
        
        return {
            "categorized_transactions": categorized,
            "execution_steps": steps
        }
