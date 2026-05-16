# Funding Rate Monitor

Real-time perpetual futures funding rate scanner across **Binance**, **Bybit**, and **OKX**.

Built to support algorithmic trading desk operations — monitoring funding rate levels and cross-exchange spreads to flag arbitrage opportunities and high-cost positions.

## What it does

- Fetches live funding rates for configurable symbols across 3 major CEXs
- Flags symbols where funding exceeds a defined threshold (default: 0.05% per period)
- Detects cross-exchange spread opportunities above a configurable threshold
- Displays annualised funding cost for context
- Runs continuously on a configurable refresh cycle (default: 60s)

## Example output

```
═════════════════════════════════════════════════════════════════
  Funding Rate Monitor  |  2025-05-10 08:32:11 UTC
═════════════════════════════════════════════════════════════════
  Symbol        Binance      Bybit        OKX
  ────────────────────────────────────────────────────────
  BTCUSDT       +0.0102%     +0.0098%     +0.0115%
  ETHUSDT       +0.0087%     +0.0091%     +0.0083%
  SOLUSDT       +0.0201%     +0.0189%     +0.0210%
  BNBUSDT       +0.0045%     +0.0048%     +0.0041%

  ────────────────────────────────────────────────────────
  ALERTS:
  ⚠  HIGH FUNDING  Binance  SOLUSDT: +0.0201% (LONG paying, annualised 22.0%)
  💡 SPREAD OPPORTUNITY  SOLUSDT Binance (+0.0201%) vs Bybit (+0.0189%) spread=0.0012%
═════════════════════════════════════════════════════════════════
```

## Setup

```bash
pip install requests
python funding_rate_monitor.py
```

## Configuration

Edit the constants at the top of the script:

| Variable | Default | Description |
|---|---|---|
| `SYMBOLS` | BTC, ETH, SOL, BNB | Symbols to monitor |
| `ALERT_THRESHOLD` | 0.0005 | Per-period rate alert level |
| `SPREAD_THRESHOLD` | 0.0003 | Cross-exchange spread alert level |
| `REFRESH_INTERVAL` | 60s | Scan frequency |

## Use cases

- Algo trading desk operations monitoring
- Funding rate arbitrage signal detection
- Pre-trade cost analysis for perpetual positions
- Post-trade funding cost attribution
