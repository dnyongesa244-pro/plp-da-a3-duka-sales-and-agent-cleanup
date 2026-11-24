"""Generate the two Week 3 analysis datasets in the current directory."""

import numpy as np
import pandas as pd


def generate_duka_sales():
    """Create 1,000 deterministic Duka Electronics orders for Jan–Jun 2026."""
    rng = np.random.default_rng(2026)
    n = 1_000
    branches = ["Nairobi CBD", "Nairobi West", "Mombasa", "Kisumu", "Nakuru"]
    products = [
        "Laptop",
        "Smartphone",
        "Tablet",
        "Monitor",
        "Printer",
        "Headphones",
    ]
    prices = {
        "Laptop": 72_000,
        "Smartphone": 35_000,
        "Tablet": 28_000,
        "Monitor": 24_000,
        "Printer": 19_000,
        "Headphones": 8_000,
    }
    dates = pd.date_range("2026-01-01", "2026-06-30", freq="D")
    branch_weights = [0.27, 0.21, 0.20, 0.17, 0.15]
    product_weights = [0.13, 0.24, 0.16, 0.17, 0.14, 0.16]
    chosen_products = rng.choice(products, n, p=product_weights)
    sales = pd.DataFrame(
        {
            "order_id": [f"DU{i:05d}" for i in range(1, n + 1)],
            "order_date": rng.choice(dates, n),
            "branch": rng.choice(branches, n, p=branch_weights),
            "product": chosen_products,
            "units": rng.choice([1, 2, 3, 4], n, p=[0.69, 0.21, 0.07, 0.03]),
            "unit_price": [prices[product] for product in chosen_products],
            "channel": rng.choice(["Online", "In-store"], n, p=[0.38, 0.62]),
        }
    )
    sales["order_date"] = pd.to_datetime(sales["order_date"])
    return sales


def generate_agent_data():
    """Reproduce the seed-44 agent register and deliberately imperfect extract."""
    rng = np.random.default_rng(44)
    n = 600
    agents = pd.DataFrame(
        {
            "agent_id": [f"AG{i:03d}" for i in range(1, 21)],
            "county": rng.choice(
                ["Nairobi", "Kiambu", "Nakuru", "Mombasa", "Kisumu"], 20
            ),
            "onboarded": pd.date_range("2024-01-01", periods=20, freq="MS")
            .strftime("%Y-%m-%d"),
        }
    )
    txns = pd.DataFrame(
        {
            "txn_id": [f"TX{i:05d}" for i in range(1, n + 1)],
            "agent_id": rng.choice(agents["agent_id"], n),
            "txn_type": rng.choice(
                ["Deposit", "withdrawal", "DEPOSIT ", "Withdrawal", "deposit"], n
            ),
            "amount": rng.lognormal(7.5, 0.8, n).round(0).astype(str),
            "txn_date": (
                pd.to_datetime("2026-03-01")
                + pd.to_timedelta(rng.integers(0, 60, n), unit="D")
            ).strftime("%Y-%m-%d"),
        }
    )
    idx = rng.choice(n, 30, replace=False)
    txns.loc[idx[:15], "amount"] = np.nan
    txns.loc[idx[15:20], "amount"] = "N/A"
    txns.loc[idx[20:25], "amount"] = "250000"
    txns.loc[idx[25:], "txn_date"] = txns.loc[idx[25:], "txn_date"].str.replace(
        "-", "/"
    )
    txns = pd.concat([txns, txns.sample(12, random_state=1)], ignore_index=True)
    txns.loc[rng.choice(len(txns), 8, replace=False), "agent_id"] = "AG099"
    return txns, agents


if __name__ == "__main__":
    generate_duka_sales().to_csv("duka_sales.csv", index=False, date_format="%Y-%m-%d")
    transactions, agent_register = generate_agent_data()
    agent_register.to_csv("agents.csv", index=False)
    transactions.to_csv("agent_transactions.csv", index=False)
