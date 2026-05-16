"""
Funding Rate Monitor — Multi-Exchange CEX Scanner
--------------------------------------------------
Fetches real-time perpetual funding rates from Binance, Bybit, and OKX
for a configurable list of symbols. Flags opportunities where the funding
rate spread between exchanges exceeds a defined threshold.

Author: Venkata Shiva Datta Botla
Use case: Algo trading operations support, funding rate arbitrage scanning
"""

import requests
import time
from datetime import datetime


# ── Configuration ─────────────────────────────────────────────────────────────

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
ALERT_THRESHOLD = 0.0005      # Flag if funding rate exceeds this (annualised ~54.75%)
SPREAD_THRESHOLD = 0.0003     # Flag cross-exchange spread above this
REFRESH_INTERVAL = 60         # Seconds between each scan cycle


# ── Exchange API Fetchers ──────────────────────────────────────────────────────

def get_binance_funding(symbol: str) -> float | None:
    """Fetch latest funding rate for a symbol from Binance."""
    url = "https://fapi.binance.com/fapi/v1/premiumIndex"
    try:
        r = requests.get(url, params={"symbol": symbol}, timeout=5)
        r.raise_for_status()
        return float(r.json()["lastFundingRate"])
    except Exception as e:
        print(f"  [Binance] Error fetching {symbol}: {e}")
        return None


def get_bybit_funding(symbol: str) -> float | None:
    """Fetch latest funding rate for a symbol from Bybit."""
    url = "https://api.bybit.com/v5/market/tickers"
    try:
        r = requests.get(url, params={"category": "linear", "symbol": symbol}, timeout=5)
        r.raise_for_status()
        items = r.json().get("result", {}).get("list", [])
        if items:
            return float(items[0]["fundingRate"])
        return None
    except Exception as e:
        print(f"  [Bybit] Error fetching {symbol}: {e}")
        return None


def get_okx_funding(symbol: str) -> float | None:
    """
    Fetch latest funding rate from OKX.
    OKX uses instrument IDs like BTC-USDT-SWAP instead of BTCUSDT.
    """
    base = symbol.replace("USDT", "")
    inst_id = f"{base}-USDT-SWAP"
    url = "https://www.okx.com/api/v5/public/funding-rate"
    try:
        r = requests.get(url, params={"instId": inst_id}, timeout=5)
        r.raise_for_status()
        data = r.json().get("data", [])
        if data:
            return float(data[0]["fundingRate"])
        return None
    except Exception as e:
        print(f"  [OKX] Error fetching {symbol}: {e}")
        return None


# ── Analysis Helpers ───────────────────────────────────────────────────────────

def annualise(rate: float, periods_per_day: int = 3) -> float:
    """Convert a single funding period rate to annualised percentage."""
    return rate * periods_per_day * 365 * 100


def format_rate(rate: float | None) -> str:
    if rate is None:
        return "  N/A   "
    return f"{rate*100:+.4f}%"


def check_alerts(symbol: str, rates: dict) -> list[str]:
    """Return a list of alert strings for a given symbol's rate dict."""
    alerts = []
    valid = {ex: r for ex, r in rates.items() if r is not None}

    # Single-exchange high funding alert
    for ex, r in valid.items():
        if abs(r) >= ALERT_THRESHOLD:
            direction = "LONG paying" if r > 0 else "SHORT paying"
            alerts.append(
                f"  ⚠  HIGH FUNDING  {ex:8s} {symbol}: {format_rate(r)} "
                f"({direction}, annualised {annualise(r):.1f}%)"
            )

    # Cross-exchange spread alert
    if len(valid) >= 2:
        exchanges = list(valid.keys())
        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                ex_a, ex_b = exchanges[i], exchanges[j]
                spread = abs(valid[ex_a] - valid[ex_b])
                if spread >= SPREAD_THRESHOLD:
                    alerts.append(
                        f"  💡 SPREAD OPPORTUNITY  {symbol} "
                        f"{ex_a} ({format_rate(valid[ex_a])}) vs "
                        f"{ex_b} ({format_rate(valid[ex_b])})  "
                        f"spread={spread*100:.4f}%"
                    )
    return alerts


# ── Main Scan Loop ─────────────────────────────────────────────────────────────

def run_scan():
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"\n{'═'*65}")
    print(f"  Funding Rate Monitor  |  {timestamp}")
    print(f"{'═'*65}")
    print(f"  {'Symbol':<12} {'Binance':>10} {'Bybit':>10} {'OKX':>10}")
    print(f"  {'-'*52}")

    all_alerts = []

    for symbol in SYMBOLS:
        binance = get_binance_funding(symbol)
        bybit   = get_bybit_funding(symbol)
        okx     = get_okx_funding(symbol)

        rates = {"Binance": binance, "Bybit": bybit, "OKX": okx}

        print(f"  {symbol:<12} {format_rate(binance):>10} "
              f"{format_rate(bybit):>10} {format_rate(okx):>10}")

        all_alerts.extend(check_alerts(symbol, rates))

    if all_alerts:
        print(f"\n  {'─'*52}")
        print("  ALERTS:")
        for alert in all_alerts:
            print(alert)
    else:
        print(f"\n  No alerts — all rates within normal thresholds.")

    print(f"{'═'*65}")


def main():
    print("Funding Rate Monitor started. Press Ctrl+C to stop.")
    print(f"Scanning: {', '.join(SYMBOLS)}")
    print(f"Alert threshold : {ALERT_THRESHOLD*100:.4f}%  |  "
          f"Spread threshold: {SPREAD_THRESHOLD*100:.4f}%")
    print(f"Refresh interval: {REFRESH_INTERVAL}s\n")

    while True:
        try:
            run_scan()
            time.sleep(REFRESH_INTERVAL)
        except KeyboardInterrupt:
            print("\nMonitor stopped.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}. Retrying in {REFRESH_INTERVAL}s...")
            time.sleep(REFRESH_INTERVAL)


if __name__ == "__main__":
    main()
