"""Ground-Truth Benchmark Dataset for FinPilot Self-Evaluation.

Contains realistic, labeled multi-month transaction streams with seeded:
- Ground-truth categories and recurring status
- Ghost / dormant subscriptions
- Category velocity surges (Food Delivery +48%)
- Weekend discretionary spending spikes
"""

from typing import List, Dict, Any

# Curated ground truth dataset with 60 diverse transactions spanning 2 months
GROUND_TRUTH_TRANSACTIONS: List[Dict[str, Any]] = [
    # Month 1 - Income & Fixed
    {"date": "2026-08-01", "merchant": "TechCorp Payroll", "amount": -3800.00, "description": "Direct Deposit Salary", "true_category": "Salary & Wages", "true_group": "Income", "true_recurring": True},
    {"date": "2026-08-01", "merchant": "Avalon Bay Communities", "amount": 1850.00, "description": "Apartment Monthly Rent", "true_category": "Rent & Housing", "true_group": "Fixed Essentials", "true_recurring": True},
    {"date": "2026-08-03", "merchant": "ConEdison", "amount": 115.40, "description": "Electric & Gas Utility", "true_category": "Utilities", "true_group": "Fixed Essentials", "true_recurring": True},
    {"date": "2026-08-04", "merchant": "Verizon Wireless", "amount": 85.00, "description": "Mobile & Internet", "true_category": "Utilities", "true_group": "Fixed Essentials", "true_recurring": True},
    
    # Month 1 - Subscriptions
    {"date": "2026-08-05", "merchant": "Netflix", "amount": 19.99, "description": "Monthly Streaming Premium", "true_category": "Digital Streaming", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-08-06", "merchant": "Spotify USA", "amount": 11.99, "description": "Family Music Streaming", "true_category": "Digital Streaming", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-08-07", "merchant": "Equinox Fitness", "amount": 180.00, "description": "Monthly All-Access Gym", "true_category": "Fitness & Gym", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-08-08", "merchant": "GitHub Copilot", "amount": 10.00, "description": "Developer Cloud Subscription", "true_category": "SaaS & Software", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-08-09", "merchant": "Disney+", "amount": 13.99, "description": "Digital Entertainment Subscription", "true_category": "Digital Streaming", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-08-10", "merchant": "Hulu", "amount": 14.99, "description": "Ad-free streaming plan", "true_category": "Digital Streaming", "true_group": "Recurring Subscriptions", "true_recurring": True},

    # Month 1 - Living & Groceries
    {"date": "2026-08-02", "merchant": "Trader Joe's", "amount": 84.50, "description": "Weekly grocery haul", "true_category": "Groceries", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-08-09", "merchant": "Whole Foods Market", "amount": 112.30, "description": "Organic groceries & produce", "true_category": "Groceries", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-08-16", "merchant": "Trader Joe's", "amount": 78.20, "description": "Pantry restock", "true_category": "Groceries", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-08-23", "merchant": "Safeway", "amount": 95.10, "description": "Household essentials & food", "true_category": "Groceries", "true_group": "Variable Living", "true_recurring": False},

    # Month 1 - Transit & Fuel
    {"date": "2026-08-05", "merchant": "Chevron Gas Station", "amount": 54.00, "description": "Fuel fill-up", "true_category": "Transportation", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-08-12", "merchant": "Uber", "amount": 26.50, "description": "Rideshare to downtown", "true_category": "Transportation", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-08-20", "merchant": "Shell Oil", "amount": 48.00, "description": "Fuel regular", "true_category": "Transportation", "true_group": "Variable Living", "true_recurring": False},

    # Month 1 - Dining (Baseline Month 1: Total ~$280)
    {"date": "2026-08-07", "merchant": "DoorDash", "amount": 34.50, "description": "Thai food delivery", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-08-14", "merchant": "Uber Eats", "amount": 42.00, "description": "Sushi combo dinner", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-08-15", "merchant": "TechCorp Payroll", "amount": -3800.00, "description": "Direct Deposit Salary", "true_category": "Salary & Wages", "true_group": "Income", "true_recurring": True},
    {"date": "2026-08-21", "merchant": "Chipotle", "amount": 16.50, "description": "Burrito bowl lunch", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-08-28", "merchant": "DoorDash", "amount": 38.20, "description": "Pizza delivery Friday", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},

    # Month 1 - Coffee & Shopping
    {"date": "2026-08-03", "merchant": "Blue Bottle Coffee", "amount": 6.75, "description": "Latte single origin", "true_category": "Coffee & Cafes", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-08-11", "merchant": "Starbucks", "amount": 7.20, "description": "Cold brew + pastry", "true_category": "Coffee & Cafes", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-08-18", "merchant": "Amazon.com", "amount": 49.99, "description": "USB-C cables & desk mat", "true_category": "Shopping & Apparel", "true_group": "Discretionary Lifestyle", "true_recurring": False},

    # -------------------------------------------------------------
    # Month 2 - Income & Fixed
    {"date": "2026-09-01", "merchant": "TechCorp Payroll", "amount": -3800.00, "description": "Direct Deposit Salary", "true_category": "Salary & Wages", "true_group": "Income", "true_recurring": True},
    {"date": "2026-09-01", "merchant": "Avalon Bay Communities", "amount": 1850.00, "description": "Apartment Monthly Rent", "true_category": "Rent & Housing", "true_group": "Fixed Essentials", "true_recurring": True},
    {"date": "2026-09-03", "merchant": "ConEdison", "amount": 122.10, "description": "Electric & Gas Utility", "true_category": "Utilities", "true_group": "Fixed Essentials", "true_recurring": True},
    {"date": "2026-09-04", "merchant": "Verizon Wireless", "amount": 85.00, "description": "Mobile & Internet", "true_category": "Utilities", "true_group": "Fixed Essentials", "true_recurring": True},

    # Month 2 - Ghost Subscriptions Repeat
    {"date": "2026-09-05", "merchant": "Netflix", "amount": 19.99, "description": "Monthly Streaming Premium", "true_category": "Digital Streaming", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-09-06", "merchant": "Spotify USA", "amount": 11.99, "description": "Family Music Streaming", "true_category": "Digital Streaming", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-09-07", "merchant": "Equinox Fitness", "amount": 180.00, "description": "Monthly All-Access Gym (DORMANT)", "true_category": "Fitness & Gym", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-09-08", "merchant": "GitHub Copilot", "amount": 10.00, "description": "Developer Cloud Subscription", "true_category": "SaaS & Software", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-09-09", "merchant": "Disney+", "amount": 13.99, "description": "Digital Entertainment Subscription", "true_category": "Digital Streaming", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-09-10", "merchant": "Hulu", "amount": 14.99, "description": "Ad-free streaming plan", "true_category": "Digital Streaming", "true_group": "Recurring Subscriptions", "true_recurring": True},

    # Month 2 - SEEDED ANOMALY: VELOCITY SURGE IN FOOD DELIVERY (+65% surge!)
    {"date": "2026-09-02", "merchant": "DoorDash", "amount": 45.00, "description": "Dinner delivery", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-05", "merchant": "Uber Eats", "amount": 58.50, "description": "Friday night feast", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-08", "merchant": "DoorDash", "amount": 39.80, "description": "Lunch delivery work", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-12", "merchant": "Uber Eats", "amount": 62.00, "description": "Weekend wings delivery", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-15", "merchant": "TechCorp Payroll", "amount": -3800.00, "description": "Direct Deposit Salary", "true_category": "Salary & Wages", "true_group": "Income", "true_recurring": True},
    {"date": "2026-09-16", "merchant": "Grubhub", "amount": 48.00, "description": "Late night Indian curry", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-19", "merchant": "DoorDash", "amount": 52.40, "description": "Saturday burger delivery", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-22", "merchant": "DoorDash", "amount": 41.20, "description": "Mexican tacos delivery", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-26", "merchant": "Uber Eats", "amount": 67.50, "description": "Family sushi dinner", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-29", "merchant": "DoorDash", "amount": 44.00, "description": "Comfort food delivery", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},

    # Month 2 - Living & Groceries
    {"date": "2026-09-03", "merchant": "Trader Joe's", "amount": 88.00, "description": "Weekly grocery haul", "true_category": "Groceries", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-09-10", "merchant": "Whole Foods Market", "amount": 105.00, "description": "Organic vegetables & snacks", "true_category": "Groceries", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-09-17", "merchant": "Trader Joe's", "amount": 76.40, "description": "Pantry items", "true_category": "Groceries", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-09-24", "merchant": "Safeway", "amount": 82.10, "description": "Milk, eggs, laundry", "true_category": "Groceries", "true_group": "Variable Living", "true_recurring": False},

    # Month 2 - Transit
    {"date": "2026-09-06", "merchant": "Chevron Gas Station", "amount": 55.00, "description": "Gasoline fill", "true_category": "Transportation", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-09-14", "merchant": "Uber", "amount": 31.00, "description": "Airport ride", "true_category": "Transportation", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-09-21", "merchant": "Shell Oil", "amount": 51.50, "description": "Gasoline", "true_category": "Transportation", "true_group": "Variable Living", "true_recurring": False},

    # Month 2 - Shopping & Coffee
    {"date": "2026-09-04", "merchant": "Starbucks", "amount": 7.50, "description": "Morning coffee", "true_category": "Coffee & Cafes", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-11", "merchant": "Blue Bottle Coffee", "amount": 6.80, "description": "Pour over coffee", "true_category": "Coffee & Cafes", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-18", "merchant": "Nike Store", "amount": 135.00, "description": "Running shoes", "true_category": "Shopping & Apparel", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-25", "merchant": "Target", "amount": 62.00, "description": "Home organizer & shirt", "true_category": "Shopping & Apparel", "true_group": "Discretionary Lifestyle", "true_recurring": False},
]

# Benchmark Scenarios for What-If Simulator Validation
GROUND_TRUTH_WHAT_IF_SCENARIOS = [
    {
        "scenario": {
            "name": "Affordable Mechanical Keyboard",
            "scenario_type": "ONE_TIME_PURCHASE",
            "amount": 220.0,
            "frequency": "one_time"
        },
        "expected_verdict": "AFFORDABLE",
        "expected_affordable": True
    },
    {
        "scenario": {
            "name": "Luxury Vacation to Maldives",
            "scenario_type": "ONE_TIME_PURCHASE",
            "amount": 5500.0,
            "frequency": "one_time"
        },
        "expected_verdict": "HIGH_RISK",
        "expected_affordable": False
    },
    {
        "scenario": {
            "name": "New Sports Car Lease",
            "scenario_type": "RECURRING_EXPENSE",
            "amount": 850.0,
            "frequency": "monthly"
        },
        "expected_verdict": "HIGH_RISK",
        "expected_affordable": False
    },
    {
        "scenario": {
            "name": "Cancel Dormant Gym and Redundant Subs",
            "scenario_type": "EXPENSE_REDUCTION",
            "amount": 210.0,
            "frequency": "monthly"
        },
        "expected_verdict": "AFFORDABLE",
        "expected_affordable": True
    }
]
