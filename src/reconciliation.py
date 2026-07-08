import pandas as pd
from pathlib import Path
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
GENERATED_DATA_DIR = DATA_DIR / "generated"
OUTPUT_DIR = BASE_DIR / "output"

USE_GENERATED_DATA = True
def load_trade_data():
    """
    Load either the original demonstration trade files or the expanded
    generated trade files based on the dataset setting.
    """
    if USE_GENERATED_DATA:
        internal_file = GENERATED_DATA_DIR / "trades_internal_generated.csv"
        custodian_file = GENERATED_DATA_DIR / "trades_custodian_generated.csv"
    else:
        internal_file = DATA_DIR / "trades_internal.csv"
        custodian_file = DATA_DIR / "trades_custodian.csv"

    internal_trades = pd.read_csv(internal_file)
    custodian_trades = pd.read_csv(custodian_file)

    return internal_trades, custodian_trades


def load_holdings_data():
    """
    Load either the original demonstration holdings files or the
    expanded generated holdings files.
    """
    if USE_GENERATED_DATA:
        internal_file = (
            GENERATED_DATA_DIR / "holdings_internal_generated.csv"
        )
        custodian_file = (
            GENERATED_DATA_DIR / "holdings_custodian_generated.csv"
        )
    else:
        internal_file = DATA_DIR / "holdings_internal.csv"
        custodian_file = DATA_DIR / "holdings_custodian.csv"

    internal_holdings = pd.read_csv(internal_file)
    custodian_holdings = pd.read_csv(custodian_file)

    return internal_holdings, custodian_holdings

def load_cash_data():
    """
    Load either the original demonstration cash files or the
    expanded generated cash files.
    """
    if USE_GENERATED_DATA:
        internal_file = (
            GENERATED_DATA_DIR / "cash_internal_generated.csv"
        )
        custodian_file = (
            GENERATED_DATA_DIR / "cash_custodian_generated.csv"
        )
    else:
        internal_file = DATA_DIR / "cash_internal.csv"
        custodian_file = DATA_DIR / "cash_custodian.csv"

    internal_cash = pd.read_csv(internal_file)
    custodian_cash = pd.read_csv(custodian_file)

    return internal_cash, custodian_cash

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
        "cash_balance_mismatch",
    ]

    medium_risk_breaks = [
        "settlement_date_mismatch",
        "market_price_mismatch",
        "side_mismatch",
        "ticker_mismatch",
        "currency_mismatch",
        "as_of_date_mismatch",
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
        "cash_balance_mismatch": "Investigate unsettled trades, custodian cash movements, fees, and income activity causing the cash difference.",
        "as_of_date_mismatch": "Confirm both cash balances are using the same valuation date.",
        "custodian_account_mismatch": "Confirm custodian account mapping and portfolio setup.",
    }

    return action_map.get(break_type, "Review exception details and escalate if unresolved.")

def assign_exception_owner(source, portfolio):
    """Assign a sample operations owner based on workflow and portfolio."""
    if source == "Trade Reconciliation":
        return "Trade Operations Team"
    elif source == "Position Reconciliation":
        return "Portfolio Accounting Team"
    elif source == "Cash Reconciliation":
        return "Cash Operations Team"
    else:
        return "Operations Control Team"


def assign_priority(risk_level, estimated_dollar_impact):
    """Assign priority based on risk level and estimated dollar impact."""
    if risk_level == "High" and estimated_dollar_impact >= 50000:
        return "Critical"
    elif risk_level == "High":
        return "High"
    elif risk_level == "Medium":
        return "Medium"
    else:
        return "Low"


def assign_root_cause_category(break_type):
    """Classify exceptions into operational root cause categories."""
    if break_type in ["missing_from_custodian", "missing_from_internal"]:
        return "Booking Issue"
    elif break_type in ["quantity_mismatch", "side_mismatch"]:
        return "Allocation Issue"
    elif break_type in ["price_mismatch", "market_price_mismatch", "market_value_mismatch"]:
        return "Pricing Issue"
    elif break_type in ["settlement_date_mismatch"]:
        return "Settlement Issue"
    elif break_type in ["cash_balance_mismatch"]:
        return "Cash Movement Issue"
    elif break_type in ["currency_mismatch"]:
        return "Currency / FX Issue"
    elif break_type in ["custodian_account_mismatch", "portfolio_mismatch"]:
        return "Account Mapping Issue"
    else:
        return "Data Quality Issue"


def estimate_days_open(risk_level, estimated_dollar_impact):
    """Create realistic sample aging based on risk and dollar impact."""
    if risk_level == "High" and estimated_dollar_impact >= 50000:
        return 4
    elif risk_level == "High":
        return 2
    elif risk_level == "Medium":
        return 3
    else:
        return 1

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
    """Create a standardized exception record with management fields."""
    risk_level = classify_risk(break_type)
    priority = assign_priority(risk_level, estimated_dollar_impact)

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
        "risk_level": risk_level,
        "priority": priority,
        "exception_owner": assign_exception_owner(source, portfolio),
        "days_open": estimate_days_open(risk_level, estimated_dollar_impact),
        "root_cause_category": assign_root_cause_category(break_type),
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

def reconcile_cash(internal_cash, custodian_cash):
    """
    Compare internal expected cash balances against custodian cash balances
    and return cash exceptions.
    """
    merged = internal_cash.merge(
        custodian_cash,
        on=["portfolio", "currency"],
        how="outer",
        suffixes=("_internal", "_custodian"),
        indicator=True,
    )

    exceptions = []

    for _, row in merged.iterrows():
        portfolio = row["portfolio"]
        currency = row["currency"]
        record_id = f"{portfolio}-{currency}"

        if row["_merge"] == "left_only":
            break_type = "missing_from_custodian"

            exceptions.append(
                create_exception_record(
                    source="Cash Reconciliation",
                    record_id=record_id,
                    portfolio=portfolio,
                    ticker="Cash",
                    asset_class="Cash",
                    break_type=break_type,
                    internal_value="Present",
                    custodian_value="Missing",
                    estimated_dollar_impact=row["internal_cash_balance"],
                )
            )

        elif row["_merge"] == "right_only":
            break_type = "missing_from_internal"

            exceptions.append(
                create_exception_record(
                    source="Cash Reconciliation",
                    record_id=record_id,
                    portfolio=portfolio,
                    ticker="Cash",
                    asset_class="Cash",
                    break_type=break_type,
                    internal_value="Missing",
                    custodian_value="Present",
                    estimated_dollar_impact=row["custodian_cash_balance"],
                )
            )

        else:
            internal_balance = row["internal_cash_balance"]
            custodian_balance = row["custodian_cash_balance"]
            cash_difference = internal_balance - custodian_balance

            if cash_difference != 0:
                break_type = "cash_balance_mismatch"

                exceptions.append(
                    create_exception_record(
                        source="Cash Reconciliation",
                        record_id=record_id,
                        portfolio=portfolio,
                        ticker="Cash",
                        asset_class="Cash",
                        break_type=break_type,
                        internal_value=internal_balance,
                        custodian_value=custodian_balance,
                        estimated_dollar_impact=abs(cash_difference),
                    )
                )

            if row["as_of_date_internal"] != row["as_of_date_custodian"]:
                break_type = "as_of_date_mismatch"

                exceptions.append(
                    create_exception_record(
                        source="Cash Reconciliation",
                        record_id=record_id,
                        portfolio=portfolio,
                        ticker="Cash",
                        asset_class="Cash",
                        break_type=break_type,
                        internal_value=row["as_of_date_internal"],
                        custodian_value=row["as_of_date_custodian"],
                        estimated_dollar_impact=abs(cash_difference),
                    )
                )

            if row["custodian_account_internal"] != row["custodian_account_custodian"]:
                break_type = "custodian_account_mismatch"

                exceptions.append(
                    create_exception_record(
                        source="Cash Reconciliation",
                        record_id=record_id,
                        portfolio=portfolio,
                        ticker="Cash",
                        asset_class="Cash",
                        break_type=break_type,
                        internal_value=row["custodian_account_internal"],
                        custodian_value=row["custodian_account_custodian"],
                        estimated_dollar_impact=abs(cash_difference),
                    )
                )

    return pd.DataFrame(exceptions)
def format_excel_workbook(writer):
    """
    Apply professional formatting to each worksheet in the Excel report.
    """
    workbook = writer.book

    header_fill = PatternFill(
        fill_type="solid",
        fgColor="1F4E78",
    )

    header_font = Font(
        color="FFFFFF",
        bold=True,
    )

    high_risk_fill = PatternFill(
        fill_type="solid",
        fgColor="F4CCCC",
    )

    medium_risk_fill = PatternFill(
        fill_type="solid",
        fgColor="FFF2CC",
    )

    critical_fill = PatternFill(
        fill_type="solid",
        fgColor="E6B8AF",
    )

    currency_headers = {
        "estimated_dollar_impact",
        "Value",
    }

    for worksheet in workbook.worksheets:
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions

        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
            )

        worksheet.row_dimensions[1].height = 22

        for column_cells in worksheet.columns:
            column_letter = get_column_letter(
                column_cells[0].column
            )

            max_length = 0

            for cell in column_cells:
                cell_value = "" if cell.value is None else str(cell.value)
                max_length = max(max_length, len(cell_value))

            adjusted_width = min(max_length + 2, 45)
            worksheet.column_dimensions[column_letter].width = adjusted_width

        header_lookup = {
            cell.value: cell.column
            for cell in worksheet[1]
        }

        for header_name in currency_headers:
            if header_name in header_lookup:
                column_number = header_lookup[header_name]

                for row_number in range(
                    2,
                    worksheet.max_row + 1,
                ):
                    worksheet.cell(
                        row=row_number,
                        column=column_number,
                    ).number_format = '$#,##0.00'

        if "risk_level" in header_lookup:
            risk_column = get_column_letter(
                header_lookup["risk_level"]
            )

            worksheet.conditional_formatting.add(
                f"{risk_column}2:{risk_column}{worksheet.max_row}",
                CellIsRule(
                    operator="equal",
                    formula=['"High"'],
                    fill=high_risk_fill,
                ),
            )

            worksheet.conditional_formatting.add(
                f"{risk_column}2:{risk_column}{worksheet.max_row}",
                CellIsRule(
                    operator="equal",
                    formula=['"Medium"'],
                    fill=medium_risk_fill,
                ),
            )

        if "priority" in header_lookup:
            priority_column = get_column_letter(
                header_lookup["priority"]
            )

            worksheet.conditional_formatting.add(
                f"{priority_column}2:{priority_column}{worksheet.max_row}",
                CellIsRule(
                    operator="equal",
                    formula=['"Critical"'],
                    fill=critical_fill,
                ),
            )

        for row in worksheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(
                    vertical="top",
                    wrap_text=True,
                )
def export_excel_report(all_exceptions, trade_exceptions, position_exceptions, cash_exceptions):
    """
    Export a multi-tab Excel exception report for operations review.
    """
    excel_output_file = OUTPUT_DIR / "Investment_Operations_Exception_Report.xlsx"

    summary_data = {
        "Metric": [
            "Total Exceptions",
            "Trade Exceptions",
            "Position Exceptions",
            "Cash Exceptions",
            "High Risk Exceptions",
            "Medium Risk Exceptions",
            "Low Risk Exceptions",
            "Total Estimated Dollar Impact",
            "Critical Priority Exceptions",
            "Average Days Open",
        ],
        "Value": [
            len(all_exceptions),
            len(trade_exceptions),
            len(position_exceptions),
            len(cash_exceptions),
            len(all_exceptions[all_exceptions["risk_level"] == "High"]),
            len(all_exceptions[all_exceptions["risk_level"] == "Medium"]),
            len(all_exceptions[all_exceptions["risk_level"] == "Low"]),
            all_exceptions["estimated_dollar_impact"].sum(),
            len(all_exceptions[all_exceptions["priority"] == "Critical"]),
            round(all_exceptions["days_open"].mean(), 1),
    ],
    }

    summary_df = pd.DataFrame(summary_data)

    high_risk_exceptions = all_exceptions[
        all_exceptions["risk_level"] == "High"
    ].sort_values("estimated_dollar_impact", ascending=False)

    portfolio_breakdown = (
        all_exceptions.groupby("portfolio")
        .agg(
            exception_count=("record_id", "count"),
            high_risk_count=("risk_level", lambda x: (x == "High").sum()),
            estimated_dollar_impact=("estimated_dollar_impact", "sum"),
        )
        .reset_index()
        .sort_values("estimated_dollar_impact", ascending=False)
    )

    source_breakdown = (
        all_exceptions.groupby("source")
        .agg(
            exception_count=("record_id", "count"),
            estimated_dollar_impact=("estimated_dollar_impact", "sum"),
        )
        .reset_index()
        .sort_values("estimated_dollar_impact", ascending=False)
    )
    root_cause_breakdown = (
        all_exceptions.groupby("root_cause_category")
        .agg(
            exception_count=("record_id", "count"),
            estimated_dollar_impact=("estimated_dollar_impact", "sum"),
        )
        .reset_index()
        .sort_values("estimated_dollar_impact", ascending=False)
    )
    with pd.ExcelWriter(excel_output_file, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        all_exceptions.to_excel(writer, sheet_name="All Exceptions", index=False)
        trade_exceptions.to_excel(writer, sheet_name="Trade Exceptions", index=False)
        position_exceptions.to_excel(writer, sheet_name="Position Exceptions", index=False)
        cash_exceptions.to_excel(writer, sheet_name="Cash Exceptions", index=False)
        high_risk_exceptions.to_excel(writer, sheet_name="High Risk Exceptions", index=False)
        portfolio_breakdown.to_excel(writer, sheet_name="Portfolio Breakdown", index=False)
        source_breakdown.to_excel(writer, sheet_name="Source Breakdown", index=False)
        root_cause_breakdown.to_excel(writer, sheet_name="Root Cause Breakdown", index=False)
        format_excel_workbook(writer)

    return excel_output_file   

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    internal_trades, custodian_trades = load_trade_data()
    internal_holdings, custodian_holdings = load_holdings_data()
    internal_cash, custodian_cash = load_cash_data()

    trade_exceptions = reconcile_trades(internal_trades, custodian_trades)
    position_exceptions = reconcile_holdings(internal_holdings, custodian_holdings)
    cash_exceptions = reconcile_cash(internal_cash, custodian_cash)

    all_exceptions = pd.concat(
        [trade_exceptions, position_exceptions, cash_exceptions],
        ignore_index=True,
    )

    trade_output_file = OUTPUT_DIR / "trade_exceptions.csv"
    position_output_file = OUTPUT_DIR / "position_exceptions.csv"
    cash_output_file = OUTPUT_DIR / "cash_exceptions.csv"
    all_output_file = OUTPUT_DIR / "all_exceptions.csv"

    trade_exceptions.to_csv(trade_output_file, index=False)
    position_exceptions.to_csv(position_output_file, index=False)
    cash_exceptions.to_csv(cash_output_file, index=False)
    all_exceptions.to_csv(all_output_file, index=False)
    excel_output_file = export_excel_report(
        all_exceptions,
        trade_exceptions,
        position_exceptions,
        cash_exceptions,
    )
    dataset_name = (
        "Expanded generated dataset"
        if USE_GENERATED_DATA
        else "Original demonstration dataset"
    )
    print("Reconciliation complete.")
    print(f"Trade dataset: {dataset_name}")
    print(f"Trade exceptions found: {len(trade_exceptions)}")
    print(f"Position exceptions found: {len(position_exceptions)}")
    print(f"Cash exceptions found: {len(cash_exceptions)}")
    print(f"Total exceptions found: {len(all_exceptions)}")
    print(f"Output saved to: {all_output_file}")
    print(f"Excel report saved to: {excel_output_file}")
    print()
    print(all_exceptions)


if __name__ == "__main__":
    main()