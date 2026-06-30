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


def load_holdings_data():
    """Load internal and custodian holdings files."""
    internal_holdings = pd.read_csv(DATA_DIR / "holdings_internal.csv")
    custodian_holdings = pd.read_csv(DATA_DIR / "holdings_custodian.csv")

    return internal_holdings, custodian_holdings


def calculate_dollar_value(quantity, price):
    """Calculate estimated dollar value using quantity and price."""
    return float(quantity) * float(price)


def classify_risk(break_type):
    """Assign operational risk level based on exception type."""
    high_risk_breaks = [
        "missing_from_custodian",
        "missing_from_internal",
        "quantity_mismatch",
        "price_mismatch",
        "market_value_mismatch",
    ]

    medium_risk_breaks = [
        "settlement_date_mismatch",
        "market_price_mismatch",
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
        "missing_from_custodian": "Confirm record with custodian and investigate whether the position or trade failed to book externally.",
        "missing_from_internal": "Review custodian activity and confirm whether the record should be booked internally.",
        "quantity_mismatch": "Compare internal allocation records against custodian position or trade details.",
        "price_mismatch": "Review execution price, broker confirmation, and custodian booking details.",
        "market_price_mismatch": "Review pricing source, valuation date, and custodian market price feed.",
        "market_value_mismatch": "Compare quantity and price inputs used to calculate market value.",
        "settlement_date_mismatch": "Confirm contractual settlement date and update the incorrect record.",
        "side_mismatch": "Review buy/sell direction against order management records.",
        "ticker_mismatch": "Validate security identifier and booking details.",
        "currency_mismatch": "Confirm currency and FX treatment.",
        "portfolio_mismatch": "Confirm account mapping between internal and custodian systems.",
        "asset_class_mismatch": "Review security master classification.",
        "trader_mismatch": "Review internal trade ownership assignment.",
        "custodian_account_mismatch": "Confirm custodian account mapping and portfolio setup.",
    }

    return action_map.get(break_type, "Review exception details and escalate if unresolved.")


def create_exception_record(
    source,
    record_id,
    portfolio,
    ticker,
    asset_class,
    break_type,
    internal_value,
    custodian_value,
    estimated_dollar_impact,
):
    """Create a standardized exception record."""
    return {
        "source": source,
        "record_id": record_id,
        "portfolio": portfolio,
        "ticker": ticker,
        "asset_class": asset_class,
        "break_type": break_type,
        "internal_value": internal_value,
        "custodian_value": custodian_value,
        "estimated_dollar_impact": estimated_dollar_impact,
        "risk_level": classify_risk(break_type),
        "recommended_action": recommend_action(break_type),
        "status": "Open",
    }


def reconcile_trades(internal_trades, custodian_trades):
    """
    Compare internal trade records against custodian trade records
    and return trade exceptions.
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
            trade_value = calculate_dollar_value(
                row["quantity_internal"],
                row["price_internal"],
            )

            exceptions.append(
                create_exception_record(
                    source="Trade Reconciliation",
                    record_id=trade_id,
                    portfolio=row["portfolio_internal"],
                    ticker=row["ticker_internal"],
                    asset_class=row["asset_class_internal"],
                    break_type="missing_from_custodian",
                    internal_value="Present",
                    custodian_value="Missing",
                    estimated_dollar_impact=trade_value,
                )
            )

        elif row["_merge"] == "right_only":
            trade_value = calculate_dollar_value(
                row["quantity_custodian"],
                row["price_custodian"],
            )

            exceptions.append(
                create_exception_record(
                    source="Trade Reconciliation",
                    record_id=trade_id,
                    portfolio=row["portfolio_custodian"],
                    ticker=row["ticker_custodian"],
                    asset_class=row["asset_class_custodian"],
                    break_type="missing_from_internal",
                    internal_value="Missing",
                    custodian_value="Present",
                    estimated_dollar_impact=trade_value,
                )
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
                    trade_value = calculate_dollar_value(
                        row["quantity_internal"],
                        row["price_internal"],
                    )

                    break_type = f"{field}_mismatch"

                    exceptions.append(
                        create_exception_record(
                            source="Trade Reconciliation",
                            record_id=trade_id,
                            portfolio=row["portfolio_internal"],
                            ticker=row["ticker_internal"],
                            asset_class=row["asset_class_internal"],
                            break_type=break_type,
                            internal_value=internal_value,
                            custodian_value=custodian_value,
                            estimated_dollar_impact=trade_value,
                        )
                    )

    return pd.DataFrame(exceptions)


def reconcile_holdings(internal_holdings, custodian_holdings):
    """
    Compare internal portfolio holdings against custodian holdings
    and return position exceptions.
    """
    merged = internal_holdings.merge(
        custodian_holdings,
        on=["portfolio", "ticker"],
        how="outer",
        suffixes=("_internal", "_custodian"),
        indicator=True,
    )

    exceptions = []

    for _, row in merged.iterrows():
        portfolio = row["portfolio"]
        ticker = row["ticker"]

        if row["_merge"] == "left_only":
            position_value = calculate_dollar_value(
                row["quantity_internal"],
                row["market_price_internal"],
            )

            record_id = f"{portfolio}-{ticker}"

            exceptions.append(
                create_exception_record(
                    source="Position Reconciliation",
                    record_id=record_id,
                    portfolio=portfolio,
                    ticker=ticker,
                    asset_class=row["asset_class_internal"],
                    break_type="missing_from_custodian",
                    internal_value="Present",
                    custodian_value="Missing",
                    estimated_dollar_impact=position_value,
                )
            )

        elif row["_merge"] == "right_only":
            position_value = calculate_dollar_value(
                row["quantity_custodian"],
                row["market_price_custodian"],
            )

            record_id = f"{portfolio}-{ticker}"

            exceptions.append(
                create_exception_record(
                    source="Position Reconciliation",
                    record_id=record_id,
                    portfolio=portfolio,
                    ticker=ticker,
                    asset_class=row["asset_class_custodian"],
                    break_type="missing_from_internal",
                    internal_value="Missing",
                    custodian_value="Present",
                    estimated_dollar_impact=position_value,
                )
            )

        else:
            fields_to_check = [
                "asset_class",
                "quantity",
                "market_price",
                "currency",
                "custodian_account",
            ]

            for field in fields_to_check:
                internal_value = row[f"{field}_internal"]
                custodian_value = row[f"{field}_custodian"]

                if internal_value != custodian_value:
                    position_value = calculate_dollar_value(
                        row["quantity_internal"],
                        row["market_price_internal"],
                    )

                    break_type = f"{field}_mismatch"
                    record_id = f"{portfolio}-{ticker}"

                    exceptions.append(
                        create_exception_record(
                            source="Position Reconciliation",
                            record_id=record_id,
                            portfolio=portfolio,
                            ticker=ticker,
                            asset_class=row["asset_class_internal"],
                            break_type=break_type,
                            internal_value=internal_value,
                            custodian_value=custodian_value,
                            estimated_dollar_impact=position_value,
                        )
                    )

    return pd.DataFrame(exceptions)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    internal_trades, custodian_trades = load_trade_data()
    internal_holdings, custodian_holdings = load_holdings_data()

    trade_exceptions = reconcile_trades(internal_trades, custodian_trades)
    position_exceptions = reconcile_holdings(internal_holdings, custodian_holdings)

    all_exceptions = pd.concat(
        [trade_exceptions, position_exceptions],
        ignore_index=True,
    )

    trade_output_file = OUTPUT_DIR / "trade_exceptions.csv"
    position_output_file = OUTPUT_DIR / "position_exceptions.csv"
    all_output_file = OUTPUT_DIR / "all_exceptions.csv"

    trade_exceptions.to_csv(trade_output_file, index=False)
    position_exceptions.to_csv(position_output_file, index=False)
    all_exceptions.to_csv(all_output_file, index=False)

    print("Reconciliation complete.")
    print(f"Trade exceptions found: {len(trade_exceptions)}")
    print(f"Position exceptions found: {len(position_exceptions)}")
    print(f"Total exceptions found: {len(all_exceptions)}")
    print(f"Output saved to: {all_output_file}")
    print()
    print(all_exceptions)


if __name__ == "__main__":
    main()