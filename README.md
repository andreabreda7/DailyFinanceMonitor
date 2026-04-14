# 📊 Market Monitor — Drawdown Tracker per PAC

Strumento gratuito per monitorare il drawdown dai massimi storici (ATH) di ETF e indici.  
Invia notifiche Telegram quando il mercato scende oltre le soglie configurate, e pubblica una dashboard su GitHub Pages aggiornata ogni giorno automaticamente.

---

## ✨ Funzionalità

| Feature | Dettaglio |
|---|---|
| **Dati di mercato** | Yahoo Finance (gratuito, nessuna API key) |
| **Ticker monitorati** | VWCE, SPY, CSPX, IWDA, QQQ — personalizzabili |
| **Soglie di alert** | -10%, -20%, -30% da ATH — personalizzabili |
| **Notifiche** | Bot Telegram gratuito |
| **Dashboard** | GitHub Pages (statica, sempre online) |
| **Automazione** | GitHub Actions, ogni giorno feriale alle 19:30 CET |
| **Costo totale** | 0€ |

---

## 🚀 Setup in 5 minuti

### 1. Forka il repository

Clicca **Fork** in alto a destra su GitHub.

### 2. Crea il tuo Bot Telegram

1. Apri Telegram e cerca **@BotFather**
2. Invia `/newbot` e scegli un nome
3. Copia il **token** che ti viene fornito (es. `123456:ABCdef...`)
4. Cerca **@userinfobot** su Telegram e invia `/start` — ti darà il tuo **Chat ID**

### 3. Aggiungi i Secret su GitHub

Nel tuo repository → **Settings → Secrets and variables → Actions → New repository secret**:

| Nome secret | Valore |
|---|---|
| `TELEGRAM_TOKEN` | Il token del bot (es. `123456:ABCdef...`) |
| `TELEGRAM_CHAT_ID` | Il tuo Chat ID (es. `987654321`) |

### 4. Abilita GitHub Pages

**Settings → Pages → Source: Deploy from a branch → Branch: `main` → Folder: `/docs`**

La dashboard sarà disponibile su: `https://TUO-USERNAME.github.io/market-monitor/`

### 5. Primo test manuale

**Actions → Daily Market Monitor → Run workflow**

Dopo circa 1 minuto vedrai i dati sulla dashboard e riceverai il messaggio su Telegram.

---

## ⚙️ Personalizzazione

Modifica `monitor.py` per adattare il bot alle tue esigenze:

```python
# Aggiungi o rimuovi ticker
TICKERS = {
    "VWCE.DE":  "VWCE – Vanguard All-World",
    "SPY":      "SPY – S&P 500",
    # aggiungi altri ticker Yahoo Finance qui
}

# Cambia le soglie di alert (drawdown % da ATH)
ALERT_THRESHOLDS = [-10, -20, -30]

# Quanti anni di storia usare per calcolare l'ATH
LOOKBACK_DAYS = 365 * 3
```

### Ticker utili per un investitore italiano

```python
"VWCE.DE":   # Vanguard All-World (EUR, Xetra) ⭐ consigliato PAC
"CSPX.L":    # iShares S&P 500 (USD, Londra)
"IWDA.AS":   # iShares MSCI World (EUR, Amsterdam)
"EMIM.AS":   # iShares MSCI EM (mercati emergenti)
"EXW1.DE":   # iShares MSCI World (EUR, Xetra)
"SPY":       # SPDR S&P 500 (USD, NYSE)
"QQQ":       # Invesco Nasdaq 100 (USD)
"^GSPC":     # Indice S&P 500 (solo dashboard, non acquistabile)
"^STOXX50E": # Euro Stoxx 50
```

---

## 📅 Orario di esecuzione

Il workflow gira ogni giorno feriale alle **17:30 UTC = 19:30 CEST** (estate) / **18:30 CET** (inverno).

Per cambiare l'orario, modifica `.github/workflows/daily.yml`:

```yaml
- cron: "30 17 * * 1-5"   # formato: minuto ora giorno-mese mese giorno-settimana
```

---

## 🏃 Esecuzione locale

```bash
git clone https://github.com/TUO-USERNAME/market-monitor
cd market-monitor
pip install -r requirements.txt

# Opzionale: configura Telegram localmente
export TELEGRAM_TOKEN="il-tuo-token"
export TELEGRAM_CHAT_ID="il-tuo-chat-id"

python monitor.py
# Apri docs/index.html nel browser
```

---

## 📁 Struttura del progetto

```
market-monitor/
├── monitor.py                  # Script principale
├── requirements.txt
├── .github/
│   └── workflows/
│       └── daily.yml           # Automazione GitHub Actions
└── docs/                       # GitHub Pages
    ├── index.html              # Dashboard
    └── data.json               # Dati generati (auto-aggiornato)
```

---

## ⚠️ Disclaimer

Questo strumento è solo a scopo informativo e di monitoraggio personale.  
Non costituisce consulenza finanziaria. Investi sempre in modo consapevole e in linea con il tuo profilo di rischio.

---

## 📄 Licenza

MIT — libero di usare, modificare e condividere.
