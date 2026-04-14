"""
Market Monitor - Daily drawdown tracker for ETF/Index investing
Sends Telegram alerts when market drops >X% from ATH
Updates a static GitHub Pages dashboard
"""

import os
import json
import datetime
import yfinance as yf
import requests
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────────
TICKERS = {
    "VWCE.DE":   "VWCE – Vanguard All-World",
    "SPY":       "SPY – S&P 500",
    "CSPX.L":    "CSPX – S&P 500 (LSE)",
    "IWDA.AS":   "IWDA – MSCI World",
    "QQQ":       "QQQ – Nasdaq 100",
}

ALERT_THRESHOLDS = [-10, -20, -30]   # % drawdown triggers
LOOKBACK_DAYS    = 365 * 3           # years of history for ATH calculation

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

DOCS_DIR = Path("docs")
DATA_FILE = DOCS_DIR / "data.json"
# ───────────────────────────────────────────────────────────────────────────────


def fetch_data(ticker: str) -> dict | None:
    """Download price history and compute drawdown from ATH."""
    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(period=f"{LOOKBACK_DAYS}d")
        if hist.empty:
            print(f"[WARN] No data for {ticker}")
            return None

        close = hist["Close"]
        current_price = round(float(close.iloc[-1]), 4)
        ath           = round(float(close.max()), 4)
        ath_date      = close.idxmax().strftime("%Y-%m-%d")
        drawdown_pct  = round((current_price - ath) / ath * 100, 2)

        # 1-day and 5-day change
        change_1d = round((current_price / float(close.iloc[-2]) - 1) * 100, 2) if len(close) >= 2 else 0
        change_5d = round((current_price / float(close.iloc[-6]) - 1) * 100, 2) if len(close) >= 6 else 0

        # 52-week high/low
        last_year = close.iloc[-252:] if len(close) >= 252 else close
        high_52w  = round(float(last_year.max()), 4)
        low_52w   = round(float(last_year.min()), 4)

        # simple YTD
        year_start_prices = close[close.index.year == datetime.date.today().year]
        ytd = round((current_price / float(year_start_prices.iloc[0]) - 1) * 100, 2) if not year_start_prices.empty else 0

        return {
            "ticker":        ticker,
            "name":          TICKERS[ticker],
            "price":         current_price,
            "ath":           ath,
            "ath_date":      ath_date,
            "drawdown_pct":  drawdown_pct,
            "change_1d":     change_1d,
            "change_5d":     change_5d,
            "high_52w":      high_52w,
            "low_52w":       low_52w,
            "ytd":           ytd,
            "currency":      tk.info.get("currency", ""),
        }
    except Exception as e:
        print(f"[ERROR] {ticker}: {e}")
        return None


def send_telegram(message: str):
    """Send a message via Telegram Bot API."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[INFO] Telegram not configured — skipping notification")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       message,
        "parse_mode": "HTML",
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        print("[OK] Telegram message sent")
    except Exception as e:
        print(f"[ERROR] Telegram: {e}")


def build_alert_message(results: list[dict]) -> str | None:
    """Return an alert message if any ticker crosses a threshold, else None."""
    alerts = []
    for r in results:
        dd = r["drawdown_pct"]
        for threshold in sorted(ALERT_THRESHOLDS, reverse=True):
            if dd <= threshold:
                emoji = "🔴" if threshold <= -20 else "🟡"
                alerts.append(
                    f"{emoji} <b>{r['name']}</b>\n"
                    f"   Prezzo: {r['price']} {r['currency']}\n"
                    f"   ATH: {r['ath']} ({r['ath_date']})\n"
                    f"   Drawdown: <b>{dd}%</b> (soglia {threshold}%)\n"
                    f"   Variazione oggi: {r['change_1d']:+.2f}%"
                )
                break  # only fire the lowest threshold hit

    if not alerts:
        return None

    date_str = datetime.date.today().strftime("%d/%m/%Y")
    header   = f"📊 <b>Market Monitor — {date_str}</b>\n\n⚠️ Soglie di drawdown raggiunte:\n\n"
    footer   = "\n\n💡 Considera un ingresso aggiuntivo nel tuo PAC su VWCE!"
    return header + "\n\n".join(alerts) + footer


def save_data(results: list[dict]):
    """Persist results to docs/data.json for the dashboard."""
    DOCS_DIR.mkdir(exist_ok=True)

    # Load history if exists
    history = {}
    if DATA_FILE.exists():
        try:
            existing = json.loads(DATA_FILE.read_text())
            history = existing.get("history", {})
        except Exception:
            pass

    today = datetime.date.today().isoformat()
    for r in results:
        t = r["ticker"]
        if t not in history:
            history[t] = []
        # keep last 365 entries
        history[t].append({"date": today, "price": r["price"], "drawdown": r["drawdown_pct"]})
        history[t] = history[t][-365:]

    payload = {
        "updated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "results":    results,
        "history":    history,
        "thresholds": ALERT_THRESHOLDS,
    }
    DATA_FILE.write_text(json.dumps(payload, indent=2))
    print(f"[OK] Data saved to {DATA_FILE}")


def main():
    print(f"=== Market Monitor — {datetime.date.today()} ===")

    results = []
    for ticker in TICKERS:
        print(f"Fetching {ticker}...")
        data = fetch_data(ticker)
        if data:
            results.append(data)
            dd = data["drawdown_pct"]
            print(f"  {data['name']}: {data['price']} | Drawdown: {dd}% | 1d: {data['change_1d']:+.2f}%")

    if not results:
        print("[ERROR] No data retrieved — aborting")
        return

    save_data(results)

    alert_msg = build_alert_message(results)
    if alert_msg:
        print("[ALERT] Threshold crossed — sending Telegram notification")
        send_telegram(alert_msg)
    else:
        print("[OK] No thresholds crossed today")

        # Send a daily summary anyway (optional — comment out if too noisy)
        date_str = datetime.date.today().strftime("%d/%m/%Y")
        summary_lines = [f"📊 <b>Market Monitor — {date_str}</b>\n\nRiepilogo giornaliero:\n"]
        for r in results:
            icon = "🟢" if r["change_1d"] >= 0 else "🔴"
            summary_lines.append(
                f"{icon} <b>{r['name']}</b>: {r['change_1d']:+.2f}% oggi | "
                f"Drawdown da ATH: {r['drawdown_pct']}%"
            )
        summary_lines.append("\n✅ Nessuna soglia di acquisto raggiunta oggi.")
        send_telegram("\n".join(summary_lines))

    print("=== Done ===")


if __name__ == "__main__":
    main()
