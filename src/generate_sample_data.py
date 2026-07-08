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


def main():
    GENERATED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    internal_trades = build_internal_trades(number_of_trades=50)

    output_file = GENERATED_DATA_DIR / "trades_internal_generated.csv"
    internal_trades.to_csv(output_file, index=False)

    print("Generated sample data successfully.")
    print(f"Internal trades created: {len(internal_trades)}")
    print(f"Output saved to: {output_file}")
    print()
    print(internal_trades.head())


if __name__ == "__main__":
    main()