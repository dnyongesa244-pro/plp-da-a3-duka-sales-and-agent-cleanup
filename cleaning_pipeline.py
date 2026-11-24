"""Reusable cleaning steps for the mobile-money agent transaction extract."""

import pandas as pd


def clean_agent_data(txns, agents):
    """Return cleaned transactions merged to agents and a row-level cleaning log.

    Duplicate transaction IDs are removed, transaction types are standardized,
    invalid amounts are median-imputed and flagged, dates are parsed, and an
    IQR-based outlier flag is added. A left merge preserves unknown-agent rows.
    """
    required_txn_columns = {"txn_id", "agent_id", "txn_type", "amount", "txn_date"}
    required_agent_columns = {"agent_id", "county"}
    missing_txn_columns = required_txn_columns.difference(txns.columns)
    missing_agent_columns = required_agent_columns.difference(agents.columns)
    if missing_txn_columns or missing_agent_columns:
        raise ValueError(
            "Missing required columns: "
            f"transactions={sorted(missing_txn_columns)}, "
            f"agents={sorted(missing_agent_columns)}"
        )

    clean = txns.copy()
    log = []

    duplicate_mask = clean["txn_id"].duplicated(keep="first")
    duplicate_count = int(duplicate_mask.sum())
    clean = clean.loc[~duplicate_mask].copy()
    log.append(
        {
            "step": "deduplicate",
            "rows_affected": duplicate_count,
            "details": "Removed later rows with a repeated txn_id; kept first.",
        }
    )

    normalized_type = clean["txn_type"].astype("string").str.strip().str.lower()
    type_map = {"deposit": "Deposit", "withdrawal": "Withdrawal"}
    standardized_type = normalized_type.map(type_map)
    invalid_type = standardized_type.isna()
    if invalid_type.any():
        examples = clean.loc[invalid_type, "txn_type"].drop_duplicates().tolist()
        raise ValueError(f"Unrecognized txn_type values: {examples}")
    type_changes = int((clean["txn_type"].astype("string") != standardized_type).sum())
    clean["txn_type"] = standardized_type
    log.append(
        {
            "step": "standardize_txn_type",
            "rows_affected": type_changes,
            "details": "Trimmed whitespace and standardized case.",
        }
    )

    raw_amount = clean["amount"]
    numeric_amount = pd.to_numeric(raw_amount, errors="coerce")
    invalid_amount_mask = raw_amount.notna() & numeric_amount.isna()
    negative_amount_mask = numeric_amount < 0
    numeric_amount = numeric_amount.mask(negative_amount_mask)
    missing_amount_mask = numeric_amount.isna()
    imputed_count = int(missing_amount_mask.sum())
    fallback = numeric_amount.median()
    if pd.isna(fallback):
        raise ValueError("Cannot impute amounts because no valid numeric values remain.")
    medians_by_type = numeric_amount.groupby(clean["txn_type"]).transform("median")
    numeric_amount = numeric_amount.fillna(medians_by_type).fillna(fallback)
    clean["amount_imputed"] = missing_amount_mask
    clean["amount"] = numeric_amount.astype("float64")
    log.append(
        {
            "step": "coerce_and_impute_amount",
            "rows_affected": imputed_count,
            "details": (
                "Coerced nonnumeric and negative amounts to missing; imputed "
                "with the transaction-type median (overall median fallback)."
            ),
        }
    )
    log.append(
        {
            "step": "invalid_amount_values",
            "rows_affected": int(invalid_amount_mask.sum() + negative_amount_mask.sum()),
            "details": "Nonnumeric or negative source values were treated as missing.",
        }
    )

    raw_date = clean["txn_date"].astype("string")
    normalized_date = raw_date.str.replace("/", "-", regex=False)
    parsed_date = pd.to_datetime(normalized_date, format="%Y-%m-%d", errors="coerce")
    invalid_date_count = int(parsed_date.isna().sum())
    if invalid_date_count:
        raise ValueError(f"Could not parse {invalid_date_count} transaction dates.")
    reformatted_count = int((raw_date != normalized_date).sum())
    clean["txn_date"] = parsed_date
    log.append(
        {
            "step": "parse_txn_date",
            "rows_affected": reformatted_count,
            "details": "Normalized slash-separated dates and parsed ISO dates.",
        }
    )

    q1 = clean["amount"].quantile(0.25)
    q3 = clean["amount"].quantile(0.75)
    upper_bound = q3 + 1.5 * (q3 - q1)
    lower_bound = q1 - 1.5 * (q3 - q1)
    clean["is_outlier"] = (clean["amount"] < lower_bound) | (
        clean["amount"] > upper_bound
    )
    outlier_count = int(clean["is_outlier"].sum())
    log.append(
        {
            "step": "flag_iqr_outliers",
            "rows_affected": outlier_count,
            "details": (
                f"Flagged amounts outside IQR fences [{lower_bound:.2f}, "
                f"{upper_bound:.2f}]; values retained."
            ),
        }
    )

    merged = clean.merge(
        agents[["agent_id", "county"]], on="agent_id", how="left", validate="many_to_one"
    )
    unknown_count = int(merged["county"].isna().sum())
    log.append(
        {
            "step": "left_merge_agent_register",
            "rows_affected": unknown_count,
            "details": "Unknown agents retained with a missing county.",
        }
    )
    return merged, log
