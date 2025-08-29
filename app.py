import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Quotex Signal App", page_icon="📊")

st.title("📊 Quotex Signal App — Advanced (EMA + RSI + MACD)")
st.markdown("🚨 শুধুমাত্র শিক্ষা/রিসার্চ এর উদ্দেশ্যে। কোনো গ্যারান্টি নেই।")

# --- টিকার লিস্ট ---
tickers = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "AUD/USD": "AUDUSD=X",
    "NZD/USD": "NZDUSD=X",
    "USD/CAD": "USDCAD=X",
    "USD/CHF": "USDCHF=X",
    "Gold (XAU/USD)": "XAUUSD=X",
    "Silver (XAG/USD)": "XAGUSD=X",
    "Crude Oil": "CL=F",
    "Bitcoin (BTC/USD)": "BTC-USD",
    "Ethereum (ETH/USD)": "ETH-USD",
}

# --- Dropdown ---
symbol = st.selectbox("টিকার সিলেক্ট করো:", options=list(tickers.keys()))
ticker = tickers[symbol]

# --- Input options ---
timeframe = st.selectbox("টাইমফ্রেম:", ["1m", "5m", "15m", "30m", "1h"])
period = st.selectbox("পিরিয়ড:", ["1d", "5d", "1mo", "3mo"])

if st.button("🔍 সিগন্যাল জেনারেট করো"):
    df = yf.download(ticker, period=period, interval=timeframe)

    if df.empty:
        st.error("❌ ডাটা পাওয়া যায়নি, অন্য টিকার বা টাইমফ্রেম চেষ্টা করো।")
    else:
        # Indicator calculations
        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
        df["RSI"] = 100 - (100 / (1 + df["Close"].pct_change().rolling(14).mean()))
        df["MACD"] = df["Close"].ewm(span=12, adjust=False).mean() - df["Close"].ewm(span=26, adjust=False).mean()

        last = df.iloc[-1]

        signal = "❌ No Clear Signal"
        if last["EMA20"] > last["EMA50"] and last["RSI"] < 70 and last["MACD"] > 0:
            signal = "🟢 BUY"
        elif last["EMA20"] < last["EMA50"] and last["RSI"] > 30 and last["MACD"] < 0:
            signal = "🔴 SELL"

        st.subheader(f"Signal for {symbol} ({ticker})")
        st.write(signal)
        st.line_chart(df[["Close", "EMA20", "EMA50"]])
