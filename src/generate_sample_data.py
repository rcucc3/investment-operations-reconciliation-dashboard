from pathlib import Path
import random

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
GENERATED_DATA_DIR = BASE_DIR / "data" / "generated"

RANDOM_SEED = 42
random.seed(RANDOM_SEED)


PORTFOLIOS = [
    {
        "portfolio": "US Growth Fund",
        "account": "GF-1001",
        "strategy": "US Growth Equity",
    },
    {
        "portfolio": "Balanced Allocation Fund",
        "account": "BF-2001",
        "strategy": "Multi-Asset",
    },
    {
        "portfolio": "Core Income Fund",
        "account": "IF-3001",
        "strategy": "Fixed Income",
    },
    {
        "portfolio": "International Equity Fund",
        "account": "IEF-4001",
        "strategy": "International Equity",
    },
    {
        "portfolio": "Short Duration Bond Fund",
        "account": "SDB-5001",
        "strategy": "Short Duration Fixed Income",
    },
]


SECURITIES = [
    {"ticker": "AAPL", "asset_class": "Equity", "currency": "USD", "price": 195.25},
    {"ticker": "MSFT", "asset_class": "Equity", "currency": "USD", "price": 420.10},
    {"ticker": "NVDA", "asset_class": "Equity", "currency": "USD", "price": 122.75},
    {"ticker": "GOOGL", "asset_class": "Equity", "currency": "USD", "price": 178.20},
    {"ticker": "JPM", "asset_class": "Equity", "currency": "USD", "price": 205.15},
    {"ticker": "SPY", "asset_class": "ETF", "currency": "USD", "price": 530.40},
    {"ticker": "XLF", "asset_class": "ETF", "currency": "USD", "price": 43.75},
    {"ticker": "TLT", "asset_class": "Bond ETF", "currency": "USD", "price": 91.30},
    {"ticker": "IEF", "asset_class": "Bond ETF", "currency": "USD", "price": 94.80},
    {"ticker": "AGG", "asset_class": "Bond ETF", "currency": "USD", "price": 97.60},
    {"ticker": "SAP", "asset_class": "Equity", "currency": "EUR", "price": 184.50},
    {"ticker": "ASML", "asset_class": "Equity", "currency": "EUR", "price": 935.20},
    {"ticker": "TM", "asset_class": "ADR", "currency": "USD", "price": 178.40},
    {"ticker": "EWJ", "asset_class": "ETF", "currency": "USD", "price": 69.15},
]


BROKERS = [
    "Morgan Stanley",
    "J.P. Morgan",
    "Goldman Sachs",
    "Citigroup",
    "Bank of America",
]


TRADERS = [
    "J. Miller",
    "A. Patel",
    "S. Lee",
    "M. Chen",
]


def build_internal_trades(number_of_trades=50):
    """Create a deterministic simulated internal trade file."""
    rows = []

    start_date = pd.Timestamp("2026-06-01")

    for trade_number in range(1, number_of_trades + 1):
        portfolio_data = random.choice(PORTFOLIOS)
        security = random.choice(SECURITIES)

        trade_date = start_date + pd.Timedelta(
            days=random.randint(0, 14)
        )

        settlement_days = 1 if security["asset_class"] in ["Equity", "ETF", "ADR"] else 2
        settlement_date = trade_date + pd.Timedelta(days=settlement_days)

        quantity = random.choice(
            [25, 50, 75, 100, 150, 200, 250, 300, 500]
        )

        price_variation = random.uniform(-0.01, 0.01)
        trade_price = round(
            security["price"] * (1 + price_variation),
            2,
        )

        rows.append(
            {
                "trade_id": f"T{trade_number:04d}",
                "trade_date": trade_date.strftime("%Y-%m-%d"),
                "settlement_date": settlement_date.strftime("%Y-%m-%d"),
                "portfolio": portfolio_data["portfolio"],
                "ticker": security["ticker"],
                "asset_class": security["asset_class"],
                "side": random.choice(["BUY", "SELL"]),
                "quantity": quantity,
                "price": trade_price,
                "currency": security["currency"],
                "broker": random.choice(BROKERS),
                "trader": random.choice(TRADERS),
                "custodian_account": portfolio_data["account"],
            }
        )

    return pd.DataFrame(rows)

def build_custodian_trades(internal_trades):
    """
    Create custodian trade records from the internal file and inject
    controlled reconciliation breaks for testing.
    """
    custodian_trades = internal_trades.copy()

    injected_exceptions = []

    # Quantity mismatch
    mask = custodian_trades["trade_id"] == "T0007"
    original_value = custodian_trades.loc[mask, "quantity"].iloc[0]
    custodian_trades.loc[mask, "quantity"] = original_value - 25

    injected_exceptions.append(
        {
            "trade_id": "T0007",
            "exception_type": "quantity_mismatch",
            "internal_value": original_value,
            "custodian_value": original_value - 25,
        }
    )

    # Price mismatch
    mask = custodian_trades["trade_id"] == "T0012"
    original_value = custodian_trades.loc[mask, "price"].iloc[0]
    new_value = round(original_value + 0.35, 2)
    custodian_trades.loc[mask, "price"] = new_value

    injected_exceptions.append(
        {
            "trade_id": "T0012",
            "exception_type": "price_mismatch",
            "internal_value": original_value,
            "custodian_value": new_value,
        }
    )

    # Settlement-date mismatch
    mask = custodian_trades["trade_id"] == "T0018"
    original_value = custodian_trades.loc[mask, "settlement_date"].iloc[0]
    new_value = (
        pd.Timestamp(original_value) + pd.Timedelta(days=1)
    ).strftime("%Y-%m-%d")

    custodian_trades.loc[mask, "settlement_date"] = new_value

    injected_exceptions.append(
        {
            "trade_id": "T0018",
            "exception_type": "settlement_date_mismatch",
            "internal_value": original_value,
            "custodian_value": new_value,
        }
    )

    # Currency mismatch
    mask = custodian_trades["trade_id"] == "T0024"
    original_value = custodian_trades.loc[mask, "currency"].iloc[0]
    new_value = "EUR" if original_value == "USD" else "USD"
    custodian_trades.loc[mask, "currency"] = new_value

    injected_exceptions.append(
        {
            "trade_id": "T0024",
            "exception_type": "currency_mismatch",
            "internal_value": original_value,
            "custodian_value": new_value,
        }
    )

    # Buy/sell direction mismatch
    mask = custodian_trades["trade_id"] == "T0030"
    original_value = custodian_trades.loc[mask, "side"].iloc[0]
    new_value = "SELL" if original_value == "BUY" else "BUY"
    custodian_trades.loc[mask, "side"] = new_value

    injected_exceptions.append(
        {
            "trade_id": "T0030",
            "exception_type": "side_mismatch",
            "internal_value": original_value,
            "custodian_value": new_value,
        }
    )

    # Trades missing from custodian
    missing_from_custodian_ids = ["T0035", "T0041", "T0048"]

    for trade_id in missing_from_custodian_ids:
        injected_exceptions.append(
            {
                "trade_id": trade_id,
                "exception_type": "missing_from_custodian",
                "internal_value": "Present",
                "custodian_value": "Missing",
            }
        )

    custodian_trades = custodian_trades[
        ~custodian_trades["trade_id"].isin(missing_from_custodian_ids)
    ].copy()

    # Extra trade recorded only by custodian
    extra_trade = internal_trades.iloc[0].copy()
    extra_trade["trade_id"] = "T0051"
    extra_trade["ticker"] = "AMZN"
    extra_trade["asset_class"] = "Equity"
    extra_trade["quantity"] = 75
    extra_trade["price"] = 185.50
    extra_trade["side"] = "BUY"
    extra_trade["currency"] = "USD"
    extra_trade["broker"] = "Goldman Sachs"

    custodian_trades = pd.concat(
        [custodian_trades, pd.DataFrame([extra_trade])],
        ignore_index=True,
    )

    injected_exceptions.append(
        {
            "trade_id": "T0051",
            "exception_type": "missing_from_internal",
            "internal_value": "Missing",
            "custodian_value": "Present",
        }
    )

    exception_log = pd.DataFrame(injected_exceptions)

    return custodian_trades, exception_log
def build_internal_holdings():
    """
    Create deterministic portfolio holdings using the same portfolios
    and securities as the generated trade dataset.
    """
    rows = []

    holdings_per_portfolio = 5

    for portfolio_index, portfolio_data in enumerate(PORTFOLIOS):
        for holding_index in range(holdings_per_portfolio):
            security_index = (
                portfolio_index * holdings_per_portfolio + holding_index
            ) % len(SECURITIES)

            security = SECURITIES[security_index]

            quantity = 100 + (holding_index * 75) + (portfolio_index * 25)

            rows.append(
                {
                    "portfolio": portfolio_data["portfolio"],
                    "ticker": security["ticker"],
                    "asset_class": security["asset_class"],
                    "quantity": quantity,
                    "market_price": security["price"],
                    "currency": security["currency"],
                    "custodian_account": portfolio_data["account"],
                }
            )

    return pd.DataFrame(rows)


def build_custodian_holdings(internal_holdings):
    """
    Create custodian holdings and inject controlled position
    reconciliation exceptions.
    """
    custodian_holdings = internal_holdings.copy()
    injected_exceptions = []

    # Quantity mismatch
    row_index = 2
    portfolio = custodian_holdings.loc[row_index, "portfolio"]
    ticker = custodian_holdings.loc[row_index, "ticker"]
    original_value = custodian_holdings.loc[row_index, "quantity"]
    new_value = original_value - 25

    custodian_holdings.loc[row_index, "quantity"] = new_value

    injected_exceptions.append(
        {
            "record_id": f"{portfolio}-{ticker}",
            "exception_type": "quantity_mismatch",
            "internal_value": original_value,
            "custodian_value": new_value,
        }
    )

    # Market-price mismatch
    row_index = 6
    portfolio = custodian_holdings.loc[row_index, "portfolio"]
    ticker = custodian_holdings.loc[row_index, "ticker"]
    original_value = custodian_holdings.loc[row_index, "market_price"]
    new_value = round(original_value + 0.50, 2)

    custodian_holdings.loc[row_index, "market_price"] = new_value

    injected_exceptions.append(
        {
            "record_id": f"{portfolio}-{ticker}",
            "exception_type": "market_price_mismatch",
            "internal_value": original_value,
            "custodian_value": new_value,
        }
    )

    # Currency mismatch
    row_index = 11
    portfolio = custodian_holdings.loc[row_index, "portfolio"]
    ticker = custodian_holdings.loc[row_index, "ticker"]
    original_value = custodian_holdings.loc[row_index, "currency"]
    new_value = "EUR" if original_value == "USD" else "USD"

    custodian_holdings.loc[row_index, "currency"] = new_value

    injected_exceptions.append(
        {
            "record_id": f"{portfolio}-{ticker}",
            "exception_type": "currency_mismatch",
            "internal_value": original_value,
            "custodian_value": new_value,
        }
    )

    # Positions missing from custodian
    missing_row_indices = [15, 21]

    missing_records = custodian_holdings.loc[
        missing_row_indices,
        ["portfolio", "ticker"],
    ].copy()

    for _, record in missing_records.iterrows():
        injected_exceptions.append(
            {
                "record_id": f"{record['portfolio']}-{record['ticker']}",
                "exception_type": "missing_from_custodian",
                "internal_value": "Present",
                "custodian_value": "Missing",
            }
        )

    custodian_holdings = custodian_holdings.drop(
        index=missing_row_indices
    ).reset_index(drop=True)

    # Position present only at custodian
    extra_position = {
        "portfolio": PORTFOLIOS[0]["portfolio"],
        "ticker": "AMZN",
        "asset_class": "Equity",
        "quantity": 100,
        "market_price": 185.50,
        "currency": "USD",
        "custodian_account": PORTFOLIOS[0]["account"],
    }

    custodian_holdings = pd.concat(
        [
            custodian_holdings,
            pd.DataFrame([extra_position]),
        ],
        ignore_index=True,
    )

    injected_exceptions.append(
        {
            "record_id": f"{extra_position['portfolio']}-AMZN",
            "exception_type": "missing_from_internal",
            "internal_value": "Missing",
            "custodian_value": "Present",
        }
    )

    exception_log = pd.DataFrame(injected_exceptions)

    return custodian_holdings, exception_log


def main():
    GENERATED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    internal_trades = build_internal_trades(number_of_trades=50)

    custodian_trades, trade_exception_log = build_custodian_trades(
        internal_trades
    )

    internal_holdings = build_internal_holdings()

    custodian_holdings, holdings_exception_log = (
        build_custodian_holdings(internal_holdings)
    )

    internal_output_file = (
        GENERATED_DATA_DIR / "trades_internal_generated.csv"
    )

    custodian_output_file = (
        GENERATED_DATA_DIR / "trades_custodian_generated.csv"
    )

    trade_exception_log_output_file = (
        GENERATED_DATA_DIR / "injected_trade_exceptions.csv"
    )

    internal_holdings_output_file = (
        GENERATED_DATA_DIR / "holdings_internal_generated.csv"
    )

    custodian_holdings_output_file = (
        GENERATED_DATA_DIR / "holdings_custodian_generated.csv"
    )

    holdings_exception_log_output_file = (
        GENERATED_DATA_DIR / "injected_holdings_exceptions.csv"
    )

    internal_trades.to_csv(
        internal_output_file,
        index=False,
    )

    custodian_trades.to_csv(
        custodian_output_file,
        index=False,
    )

    trade_exception_log.to_csv(
        trade_exception_log_output_file,
        index=False,
    )

    internal_holdings.to_csv(
        internal_holdings_output_file,
        index=False,
    )

    custodian_holdings.to_csv(
        custodian_holdings_output_file,
        index=False,
    )

    holdings_exception_log.to_csv(
        holdings_exception_log_output_file,
        index=False,
    )

    print("Generated sample data successfully.")
    print(f"Internal trades created: {len(internal_trades)}")
    print(f"Custodian trades created: {len(custodian_trades)}")
    print(
        f"Controlled trade exceptions injected: "
        f"{len(trade_exception_log)}"
    )

    print(f"Internal holdings created: {len(internal_holdings)}")
    print(f"Custodian holdings created: {len(custodian_holdings)}")
    print(
        f"Controlled holdings exceptions injected: "
        f"{len(holdings_exception_log)}"
    )

    print()
    print(f"Internal trades file: {internal_output_file}")
    print(f"Custodian trades file: {custodian_output_file}")
    print(f"Trade exception log: {trade_exception_log_output_file}")
    print(f"Internal holdings file: {internal_holdings_output_file}")
    print(f"Custodian holdings file: {custodian_holdings_output_file}")
    print(f"Holdings exception log: {holdings_exception_log_output_file}")


if __name__ == "__main__":
    main()