"""SwingTrader 1.0 — educational daily-price screener, not trade execution."""
from datetime import date
import pandas as pd
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="SwingTrader 1.0", page_icon="📈", layout="wide")
st.title("📈 SwingTrader 1.0")
st.caption("Experimentell swingtrading-screener • dagsdata • ingen automatisk handel")
st.warning("Det här är ett forsknings- och testverktyg, inte personliga köpråd. Signalerna är regler, inte verifierade vinstsannolikheter. Historisk utveckling garanterar inget framtida resultat.")

# 40 illustrative Swedish listings across sectors. Symbols may change or be delisted.
TICKERS = {
    "ABB": "ABB.ST", "Alfa Laval": "ALFA.ST", "Assa Abloy B": "ASSA-B.ST", "Atlas Copco A": "ATCO-A.ST",
    "Autoliv": "ALIV-SDB.ST", "Axfood": "AXFO.ST", "Boliden": "BOL.ST", "Castellum": "CAST.ST",
    "Epiroc A": "EPI-A.ST", "Ericsson B": "ERIC-B.ST", "Essity B": "ESSITY-B.ST", "Evolution": "EVO.ST",
    "Getinge B": "GETI-B.ST", "Handelsbanken A": "SHB-A.ST", "H&M B": "HM-B.ST", "Hexagon B": "HEXA-B.ST",
    "Husqvarna B": "HUSQ-B.ST", "Industrivärden C": "INDU-C.ST", "Investor B": "INVE-B.ST", "Kinnevik B": "KINV-B.ST",
    "Latour B": "LATO-B.ST", "Lifco B": "LIFCO-B.ST", "Nibe B": "NIBE-B.ST", "Nordea": "NDA-SE.ST",
    "Saab B": "SAAB-B.ST", "Sandvik": "SAND.ST", "SCA B": "SCA-B.ST", "SEB A": "SEB-A.ST",
    "Securitas B": "SECU-B.ST", "Sinch": "SINCH.ST", "SKF B": "SKF-B.ST", "SSAB A": "SSAB-A.ST",
    "Swedbank A": "SWED-A.ST", "Tele2 B": "TEL2-B.ST", "Telia": "TELIA.ST", "Trelleborg B": "TREL-B.ST",
    "Volvo B": "VOLV-B.ST", "Volvo Cars B": "VOLCAR-B.ST", "Vitec B": "VIT-B.ST", "Sivers Semiconductors": "SIVE.ST",
}

@st.cache_data(ttl=60 * 60 * 4, show_spinner=False)
def get_prices(symbol: str) -> pd.DataFrame:
    raw = yf.download(symbol, period="1y", interval="1d", auto_adjust=True, progress=False, threads=False)
    if raw is None or raw.empty:
        return pd.DataFrame()
    # yfinance versions may return MultiIndex columns even for a single symbol.
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    if "Close" not in raw.columns:
        return pd.DataFrame()
    return raw.dropna(subset=["Close"])


def evaluate(df: pd.DataFrame):
    close = df["Close"].astype(float)
    if len(close) < 65:
        return None
    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()
    delta = close.diff()
    avg_up = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    avg_down = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rs = avg_up / avg_down.replace(0, float("nan"))
    rsi = (100 - 100 / (1 + rs)).iloc[-1]
    last = float(close.iloc[-1])
    trend = bool(last > ma20.iloc[-1] > ma50.iloc[-1])
    pullback = bool(last > ma50.iloc[-1] and last < ma20.iloc[-1] and pd.notna(rsi) and rsi < 45)
    momentum = float((last / close.iloc[-21] - 1) * 100)
    score = (2 if trend else 0) + (2 if pullback else 0) + (1 if momentum > 3 else 0)
    signal = "Trend" if trend else "Rekyl" if pullback else "Avvakta"
    return {"Senaste kurs (SEK)": round(last, 2), "20 d (%)": round(momentum, 1),
            "RSI 14": round(float(rsi), 1) if pd.notna(rsi) else None,
            "Signal": signal, "Poäng": score, "Senaste handelsdag": close.index[-1].strftime("%Y-%m-%d")}

with st.sidebar:
    st.header("Simuleringsantaganden")
    initial_capital = st.number_input("Fiktivt startkapital (SEK)", 1000, 1000000, 10000, step=1000)
    fee_pct = st.number_input("Courtage per order (%)", 0.0, 5.0, 0.25, step=0.05)
    min_fee = st.number_input("Minsta courtage per order (SEK)", 0.0, 1000.0, 1.0)
    spread_pct = st.number_input("Antagen total spread (%)", 0.0, 10.0, 0.20, step=0.05)
    order_size = initial_capital / 3
    one_way = max(order_size * fee_pct / 100, min_fee)
    estimated_cost = 2 * one_way + order_size * spread_pct / 100
    st.metric("Uppskattad tur-och-retur-kostnad per affär", f"{estimated_cost:.2f} kr")
    st.caption("Kostnadsexemplet antar oförändrat ordervärde och inkluderar två courtage och en ungefärlig total spread. Kontrollera aktuella villkor hos Nordnet.")

st.subheader("Svensk aktiescreener")
st.write("Vi testar 40 svenska aktier från flera branscher. Analysen bygger på dagliga kurser från Yahoo Finance via yfinance, som kan vara fördröjda eller saknas.")
if st.button("Hämta/uppdatera analys", type="primary"):
    st.cache_data.clear()

rows = []
errors = []
progress = st.progress(0, text="Hämtar kursdata …")
for idx, (name, symbol) in enumerate(TICKERS.items(), 1):
    try:
        result = evaluate(get_prices(symbol))
        if result:
            rows.append({"Bolag": name, "Ticker": symbol, **result})
        else:
            errors.append(symbol)
    except Exception:
        errors.append(symbol)
    progress.progress(idx / len(TICKERS), text=f"Hämtar kursdata: {idx}/{len(TICKERS)}")
progress.empty()

if rows:
    table = pd.DataFrame(rows).sort_values(["Poäng", "20 d (%)"], ascending=False)
    st.dataframe(table, hide_index=True, use_container_width=True)
    st.download_button("Ladda ned analys (CSV)", table.to_csv(index=False).encode("utf-8-sig"), "swingtrader_signaler.csv", "text/csv")
    st.info(f"Analyserade {len(rows)} av {len(TICKERS)} aktier. {len(errors)} saknar användbara data just nu.")
    st.subheader("Vad betyder signalerna?")
    st.write("**Trend:** kursen över 20-dagars medelvärde, som ligger över 50-dagars medelvärde. **Rekyl:** kursen över 50-dagars medelvärde men under 20-dagars, med RSI under 45. **Avvakta:** inget av villkoren uppfyllt.")
    st.write("Poängen är endast en enkel sorteringsregel. Ingen backtest, handelslogg, statistiskt säkerställd träffsäkerhet eller automatisk portföljhandel ingår ännu.")
else:
    st.error("Kunde inte hämta användbara kurser. Yahoo kan tillfälligt begränsa hämtningar. Försök senare.")

st.caption(f"Visad {date.today().isoformat()}. För produktion krävs granskade data- och användningsvillkor samt korrekt backtest med kostnader.")
