"""Ground-Truth Benchmark Dataset for FinPilot Self-Evaluation (Indian Conditions).

Contains realistic, labeled multi-month transaction streams in INR (₹) with seeded:
- Ground-truth categories and recurring status
- Ghost / dormant subscriptions (Cult.fit gym pass)
- Overlapping OTT streaming sprawl (Netflix, Spotify, Hotstar, Prime)
- Category velocity surges (Swiggy / Zomato food delivery +62%)
- Weekend quick-commerce and dining spikes
"""

from typing import List, Dict, Any

# Curated ground truth dataset with 56 diverse transactions spanning 2 months in INR (₹)
GROUND_TRUTH_TRANSACTIONS: List[Dict[str, Any]] = [
    # Month 1 - Income & Fixed
    {"date": "2026-08-01", "merchant": "TechCorp India Payroll", "amount": -115000.00, "description": "Direct Deposit Salary", "true_category": "Salary & Wages", "true_group": "Income", "true_recurring": True},
    {"date": "2026-08-01", "merchant": "Prestige Estates Rent", "amount": 28000.00, "description": "Apartment Monthly Rent", "true_category": "Rent & Housing", "true_group": "Fixed Essentials", "true_recurring": True},
    {"date": "2026-08-03", "merchant": "BESCOM Bangalore", "amount": 2150.00, "description": "Electric Utility Bill", "true_category": "Utilities", "true_group": "Fixed Essentials", "true_recurring": True},
    {"date": "2026-08-04", "merchant": "ACT Fibernet", "amount": 1199.00, "description": "Broadband Internet 300Mbps", "true_category": "Utilities", "true_group": "Fixed Essentials", "true_recurring": True},
    
    # Month 1 - Subscriptions
    {"date": "2026-08-05", "merchant": "Netflix India", "amount": 649.00, "description": "Monthly 4K Premium Plan", "true_category": "Digital Streaming", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-08-06", "merchant": "Spotify India", "amount": 179.00, "description": "Family Premium Music", "true_category": "Digital Streaming", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-08-07", "merchant": "Cult.fit", "amount": 2499.00, "description": "Monthly All-Access Cultpass Gym", "true_category": "Fitness & Gym", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-08-08", "merchant": "GitHub Copilot", "amount": 850.00, "description": "Developer Cloud Subscription", "true_category": "SaaS & Software", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-08-09", "merchant": "Disney+ Hotstar", "amount": 299.00, "description": "Digital Entertainment Subscription", "true_category": "Digital Streaming", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-08-10", "merchant": "Amazon Prime India", "amount": 299.00, "description": "Prime membership monthly", "true_category": "Digital Streaming", "true_group": "Recurring Subscriptions", "true_recurring": True},

    # Month 1 - Living & Groceries
    {"date": "2026-08-02", "merchant": "BigBasket", "amount": 1850.00, "description": "Weekly vegetables & grocery haul", "true_category": "Groceries", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-08-09", "merchant": "Zepto", "amount": 2250.00, "description": "Quick groceries & dairy essentials", "true_category": "Groceries", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-08-16", "merchant": "Blinkit", "amount": 1450.00, "description": "Pantry snacks and fruits", "true_category": "Groceries", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-08-23", "merchant": "DMart Supermarket", "amount": 2800.00, "description": "Household essentials, spices & staples", "true_category": "Groceries", "true_group": "Variable Living", "true_recurring": False},

    # Month 1 - Transit & Fuel
    {"date": "2026-08-05", "merchant": "Indian Oil Petrol", "amount": 1600.00, "description": "Fuel fill-up car", "true_category": "Transportation", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-08-12", "merchant": "Namma Yatri", "amount": 420.00, "description": "Auto ride to office tech park", "true_category": "Transportation", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-08-20", "merchant": "Bharat Petroleum", "amount": 1550.00, "description": "Fuel regular", "true_category": "Transportation", "true_group": "Variable Living", "true_recurring": False},

    # Month 1 - Dining (Baseline Month 1: Total ~₹2,030)
    {"date": "2026-08-07", "merchant": "Swiggy", "amount": 450.00, "description": "Biryani dinner delivery", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-08-14", "merchant": "Zomato", "amount": 680.00, "description": "North Indian dinner combo", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-08-15", "merchant": "TechCorp India Payroll", "amount": -115000.00, "description": "Mid-month Incentive Bonus", "true_category": "Salary & Wages", "true_group": "Income", "true_recurring": True},
    {"date": "2026-08-21", "merchant": "Chipotle & Bowl", "amount": 380.00, "description": "Burrito bowl lunch", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-08-28", "merchant": "Swiggy", "amount": 520.00, "description": "Pizza delivery Friday", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},

    # Month 1 - Coffee & Shopping
    {"date": "2026-08-03", "merchant": "Third Wave Coffee", "amount": 280.00, "description": "Flat white single origin", "true_category": "Coffee & Cafes", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-08-11", "merchant": "Chai Point", "amount": 240.00, "description": "Ginger chai and bun maska", "true_category": "Coffee & Cafes", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-08-18", "merchant": "Amazon India", "amount": 1299.00, "description": "USB-C fast charger & cable", "true_category": "Shopping & Apparel", "true_group": "Discretionary Lifestyle", "true_recurring": False},

    # -------------------------------------------------------------
    # Month 2 - Income & Fixed
    {"date": "2026-09-01", "merchant": "TechCorp India Payroll", "amount": -115000.00, "description": "Direct Deposit Salary", "true_category": "Salary & Wages", "true_group": "Income", "true_recurring": True},
    {"date": "2026-09-01", "merchant": "Prestige Estates Rent", "amount": 28000.00, "description": "Apartment Monthly Rent", "true_category": "Rent & Housing", "true_group": "Fixed Essentials", "true_recurring": True},
    {"date": "2026-09-03", "merchant": "BESCOM Bangalore", "amount": 2280.00, "description": "Electric Utility Bill", "true_category": "Utilities", "true_group": "Fixed Essentials", "true_recurring": True},
    {"date": "2026-09-04", "merchant": "ACT Fibernet", "amount": 1199.00, "description": "Broadband Internet 300Mbps", "true_category": "Utilities", "true_group": "Fixed Essentials", "true_recurring": True},

    # Month 2 - Ghost Subscriptions Repeat
    {"date": "2026-09-05", "merchant": "Netflix India", "amount": 649.00, "description": "Monthly 4K Premium Plan", "true_category": "Digital Streaming", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-09-06", "merchant": "Spotify India", "amount": 179.00, "description": "Family Premium Music", "true_category": "Digital Streaming", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-09-07", "merchant": "Cult.fit", "amount": 2499.00, "description": "Monthly All-Access Cultpass Gym (DORMANT)", "true_category": "Fitness & Gym", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-09-08", "merchant": "GitHub Copilot", "amount": 850.00, "description": "Developer Cloud Subscription", "true_category": "SaaS & Software", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-09-09", "merchant": "Disney+ Hotstar", "amount": 299.00, "description": "Digital Entertainment Subscription", "true_category": "Digital Streaming", "true_group": "Recurring Subscriptions", "true_recurring": True},
    {"date": "2026-09-10", "merchant": "Amazon Prime India", "amount": 299.00, "description": "Prime membership monthly", "true_category": "Digital Streaming", "true_group": "Recurring Subscriptions", "true_recurring": True},

    # Month 2 - SEEDED ANOMALY: VELOCITY SURGE IN FOOD DELIVERY (Swiggy/Zomato +75% surge!)
    {"date": "2026-09-02", "merchant": "Swiggy", "amount": 580.00, "description": "Dinner delivery", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-05", "merchant": "Zomato", "amount": 980.00, "description": "Friday night kebab feast", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-08", "merchant": "Swiggy", "amount": 620.00, "description": "Lunch delivery work", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-12", "merchant": "Zomato", "amount": 1150.00, "description": "Weekend gourmet burger delivery", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-15", "merchant": "TechCorp India Payroll", "amount": -115000.00, "description": "Direct Deposit Salary", "true_category": "Salary & Wages", "true_group": "Income", "true_recurring": True},
    {"date": "2026-09-16", "merchant": "Swiggy", "amount": 840.00, "description": "Late night butter chicken delivery", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-19", "merchant": "Zomato", "amount": 950.00, "description": "Saturday family dinner delivery", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-22", "merchant": "Swiggy", "amount": 720.00, "description": "Rolls and biryani delivery", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-26", "merchant": "Zomato", "amount": 1280.00, "description": "Sushi dinner weekend", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-29", "merchant": "Swiggy", "amount": 780.00, "description": "Late comfort food delivery", "true_category": "Dining Out & Delivery", "true_group": "Discretionary Lifestyle", "true_recurring": False},

    # Month 2 - Living & Groceries
    {"date": "2026-09-03", "merchant": "BigBasket", "amount": 1950.00, "description": "Weekly vegetables & pantry", "true_category": "Groceries", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-09-10", "merchant": "Zepto", "amount": 1850.00, "description": "Organic fruits and snacks", "true_category": "Groceries", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-09-17", "merchant": "Blinkit", "amount": 1620.00, "description": "Groceries & cleaning supplies", "true_category": "Groceries", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-09-24", "merchant": "DMart Supermarket", "amount": 2450.00, "description": "Provisions, pulses, oil & dairy", "true_category": "Groceries", "true_group": "Variable Living", "true_recurring": False},

    # Month 2 - Transit
    {"date": "2026-09-06", "merchant": "Indian Oil Petrol", "amount": 1700.00, "description": "Fuel regular", "true_category": "Transportation", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-09-14", "merchant": "Uber India", "amount": 540.00, "description": "Cab to airport", "true_category": "Transportation", "true_group": "Variable Living", "true_recurring": False},
    {"date": "2026-09-21", "merchant": "Bharat Petroleum", "amount": 1650.00, "description": "Fuel fill", "true_category": "Transportation", "true_group": "Variable Living", "true_recurring": False},

    # Month 2 - Shopping & Coffee
    {"date": "2026-09-04", "merchant": "Third Wave Coffee", "amount": 320.00, "description": "Cold brew coffee", "true_category": "Coffee & Cafes", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-11", "merchant": "Chai Point", "amount": 260.00, "description": "Evening tea & snack", "true_category": "Coffee & Cafes", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-18", "merchant": "Nike Store India", "amount": 3499.00, "description": "Running shoes", "true_category": "Shopping & Apparel", "true_group": "Discretionary Lifestyle", "true_recurring": False},
    {"date": "2026-09-25", "merchant": "Myntra", "amount": 2200.00, "description": "Casual shirts & apparel", "true_category": "Shopping & Apparel", "true_group": "Discretionary Lifestyle", "true_recurring": False},
]

# Benchmark Scenarios for What-If Simulator Validation (Indian Conditions)
GROUND_TRUTH_WHAT_IF_SCENARIOS = [
    {
        "scenario": {
            "name": "Affordable Mechanical Keyboard",
            "scenario_type": "ONE_TIME_PURCHASE",
            "amount": 4500.0,
            "frequency": "one_time"
        },
        "expected_verdict": "AFFORDABLE",
        "expected_affordable": True
    },
    {
        "scenario": {
            "name": "Luxury Vacation to Maldives",
            "scenario_type": "ONE_TIME_PURCHASE",
            "amount": 180000.0,
            "frequency": "one_time"
        },
        "expected_verdict": "HIGH_RISK",
        "expected_affordable": False
    },
    {
        "scenario": {
            "name": "Royal Enfield / Car EMI",
            "scenario_type": "RECURRING_EXPENSE",
            "amount": 14000.0,
            "frequency": "monthly"
        },
        "expected_verdict": "HIGH_RISK",
        "expected_affordable": False
    },
    {
        "scenario": {
            "name": "Cancel Dormant Cult.fit and Redundant OTT",
            "scenario_type": "EXPENSE_REDUCTION",
            "amount": 3500.0,
            "frequency": "monthly"
        },
        "expected_verdict": "AFFORDABLE",
        "expected_affordable": True
    }
]
