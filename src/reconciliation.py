import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"


def load_trade_data():
    """Load internal and custodian trade files."""
    internal_trades = pd.read_csv(DATA_DIR / "trades_internal.csv")
    custodian_trades = pd.read_csv(DATA_DIR / "trades_custodian.csv")

    return internal_trades, custodian_trades


def calculate_trade_value(quantity, price):
    """Calculate estimated dollar value of a trade."""
    return float(quantity) * float(price)


def classify_risk(break_type):
    """Assign operational risk level based on exception type."""
    high_risk_breaks = [
        "missing_from_custodian",
        "missing_from_internal",
        "quantity_mismatch",
        "price_mismatch",
    ]

    medium_risk_breaks = [
        "settlement_date_mismatch",
        "side_mismatch",
        "ticker_mismatch",
        "currency_mismatch",
    ]

    if break_type in high_risk_breaks:
        return "High"
    elif break_type in medium_risk_breaks:
        return "Medium"
    else:
        return "Low"


def recommend_action(break_type):
    """Suggest an operations-style next action for each exception."""
    action_map = {
        "missing_from_custodian": "Confirm trade booking with custodian and investigate settlement status.",
        "missing_from_internal": "Review custodian activity and confirm whether trade should be booked internally.",
        "quantity_mismatch": "Compare order allocation and execution details between internal and custodian records.",
        "price_mismatch": "Review execution price, broker confirmation, and custodian booking details.",
        "settlement_date_mismatch": "Confirm contractual settlement date and update the incorrect record.",
        "side_mismatch": "Review buy/sell direction against order management records.",
        "ticker_mismatch": "Validate security identifier and booking details.",
        "currency_mismatch": "Confirm trade currency and FX treatment.",
        "portfolio_mismatch": "Confirm account mapping between internal and custodian systems.",
        "asset_class_mismatch": "Review security master classification.",
        "trader_mismatch": "Review internal trade ownership assignment.",
    }

    return action_map.get(break_type, "Review exception details and escalate if unresolved.")


def reconcile_trades(internal_trades, custodian_trades):
    """
    Compare internal trade records against custodian trade records
    and return a clean exception report.
    """
    merged = internal_trades.merge(
        custodian_trades,
        on="trade_id",
        how="outer",
        suffixes=("_internal", "_custodian"),
        indicator=True,
    )

    exceptions = []

    for _, row in merged.iterrows():
        trade_id = row["trade_id"]

        if row["_merge"] == "left_only":
            trade_value = calculate_trade_value(
                row["quantity_internal"],
                row["price_internal"],
            )

            break_type = "missing_from_custodian"

            exceptions.append(
                {
                    "source": "Trade Reconciliation",
                    "trade_id": trade_id,
                    "portfolio": row["portfolio_internal"],
                    "ticker": row["ticker_internal"],
                    "asset_class": row["asset_class_internal"],
                    "break_type": break_type,
                    "internal_value": "Present",
                    "custodian_value": "Missing",
                    "estimated_dollar_impact": trade_value,
                    "risk_level": classify_risk(break_type),
                    "recommended_action": recommend_action(break_type),
                    "status": "Open",
                }
            )

        elif row["_merge"] == "right_only":
            trade_value = calculate_trade_value(
                row["quantity_custodian"],
                row["price_custodian"],
            )

            break_type = "missing_from_internal"

            exceptions.append(
                {
                    "source": "Trade Reconciliation",
                    "trade_id": trade_id,
                    "portfolio": row["portfolio_custodian"],
                    "ticker": row["ticker_custodian"],
                    "asset_class": row["asset_class_custodian"],
                    "break_type": break_type,
                    "internal_value": "Missing",
                    "custodian_value": "Present",
                    "estimated_dollar_impact": trade_value,
                    "risk_level": classify_risk(break_type),
                    "recommended_action": recommend_action(break_type),
                    "status": "Open",
                }
            )

        else:
            fields_to_check = [
                "settlement_date",
                "portfolio",
                "ticker",
                "asset_class",
                "side",
                "quantity",
                "price",
                "currency",
                "trader",
            ]

            for field in fields_to_check:
                internal_value = row[f"{field}_internal"]
                custodian_value = row[f"{field}_custodian"]

                if internal_value != custodian_value:
                    trade_value = calculate_trade_value(
                        row["quantity_internal"],
                        row["price_internal"],
                    )

                    break_type = f"{field}_mismatch"

                    exceptions.append(
                        {
                            "source": "Trade Reconciliation",
                            "trade_id": trade_id,
                            "portfolio": row["portfolio_internal"],
                            "ticker": row["ticker_internal"],
                            "asset_class": row["asset_class_internal"],
                            "break_type": break_type,
                            "internal_value": internal_value,
                            "custodian_value": custodian_value,
                            "estimated_dollar_impact": trade_value,
                            "risk_level": classify_risk(break_type),
                            "recommended_action": recommend_action(break_type),
                            "status": "Open",
                        }
                    )

    return pd.DataFrame(exceptions)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    internal_trades, custodian_trades = load_trade_data()

    trade_exceptions = reconcile_trades(internal_trades, custodian_trades)

    output_file = OUTPUT_DIR / "trade_exceptions.csv"
    trade_exceptions.to_csv(output_file, index=False)

    print("Trade reconciliation complete.")
    print(f"Exceptions found: {len(trade_exceptions)}")
    print(f"Output saved to: {output_file}")
    print()
    print(trade_exceptions)


if __name__ == "__main__":
    main()