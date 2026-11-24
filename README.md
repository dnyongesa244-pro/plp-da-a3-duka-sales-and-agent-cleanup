# Week 3 Data Analysis Deliverables

This repository contains two reproducible analytics engagements: a half-year
sales review for Duka Electronics and a data-quality, cleaning and reporting
workflow for a mobile-money agent network. The sales engagement derives order
metrics, explains branch, product, weekday/weekend and monthly performance, and
exports a focused customer segment plus an Excel branch/channel summary. The
agent engagement audits deliberately injected data-quality problems, cleans and
merges the transaction extract, preserves unknown-agent transactions, and
produces county and weekly summaries with a reusable cleaning log.

## Executive Summary — Duka Electronics

- Across **1,000 orders**, the dataset covers January–June 2026.
- **Nairobi CBD** led branch revenue with **KES 10,512,000** from **284 orders**.
- **Laptops** led revenue at **KES 11,520,000**, while **smartphones** led volume
  with **313 units**.
- **May** was the best month at **KES 7,458,000** and **February** the weakest at
  **KES 5,852,000**, a **27.4%** increase from the low to the high.
- Weekend orders averaged **KES 41,702** across **302 orders**, versus **KES
  40,567** on weekdays; weekday orders still generated more total revenue
  (**KES 28,316,000** versus **KES 12,594,000**).

## Regenerate and run

Install the listed Python libraries, then generate all three source extracts:

```bash
python -m pip install -r requirements.txt
python generate_data.py
```

`generate_data.py` uses seed **2026** for the 1,000-row `duka_sales.csv` and
seed **44** for `agents.csv` and `agent_transactions.csv`. It recreates the
intentionally injected agent-data issues, including duplicate transactions,
inconsistent transaction types, missing/invalid amounts, outliers, alternate
date separators and unknown agent IDs. These raw CSVs are generated locally
and are intentionally not included in the submission. Each notebook also
generates its own required input files from `generate_data.py` when they are
missing, so it can be run directly from the project root.

Run either notebook from the project root after generating the CSVs:

```bash
jupyter nbconvert --to notebook --execute --inplace duka_sales_exploration.ipynb
jupyter nbconvert --to notebook --execute --inplace agent_cleanup.ipynb
```

The Duka notebook writes `outputs/premium_online_coast_capital.csv` and
`excel/duka_branch_summary.xlsx`. The agent notebook writes
`outputs/agent_transactions_clean.csv`. All generated deliverables are saved
with their notebooks' visible results; run both notebooks top to bottom after
restarting the kernel before submission.

## Agent transaction row counts

The generated transaction extract has **612 rows before cleaning**. Removing
**12 duplicate transaction IDs** leaves **600 unique transactions**. The
cleaning pipeline retains all 600 unique transactions, including **7** that
reference unknown agents; those rows have a missing county and are not silently
dropped or assigned to a county.

Missing or nonnumeric amounts are median-imputed by transaction type and marked
with `amount_imputed`. The IQR rule is used to flag—not delete or cap—
statistical outliers. The KES 250,000 records are retained for review against
authoritative transaction evidence.

## Privacy

The supplied extracts contain no customer phone numbers. If they did, phone
numbers would be personal data under the Kenya Data Protection Act, 2019. They
should be minimized, access-restricted, encrypted in transit and at rest, and
excluded or masked in analysis outputs unless strictly necessary; any use or
sharing should have a lawful basis, a defined retention period and appropriate
data-subject safeguards.
