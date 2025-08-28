import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

def build_signals(data):
    data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()
    data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()

    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))

    ema12 = data['Close'].ewm(span=12, adjust=False).mean()
    ema26 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = ema12 - ema26
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()

    conditions = []
    for i in range(len(data)):
        if (
            data['EMA20'].iloc[i] > data['EMA50'].iloc[i]
            and data['RSI'].iloc[i] < 70
            and data['MACD'].iloc[i] > data['Signal_Line'].iloc[i]
        ):
            conditions.append("BUY")
        elif (
            data['EMA20'].iloc[i] < data['EMA50'].iloc[i]
            and data['RSI'].iloc[i] > 30
            and data['MACD'].iloc[i] < data['Signal_Line'].iloc[i]
        ):
            conditions.append("SELL")
        else:
            conditions.append("HOLD")

    data['signal'] = conditions
    return data

st.set_page_config(page_title="Quotex Signal App", layout="wide")

st.title("📊 Quotex Signal App — Advanced (EMA + RSI + MACD)")
st.write("🚨 শুধুমাত্র শিক্ষা/রিসার্চ এর উদ্দেশ্যে। কোনো গ্যারান্টি নেই।")

ticker = st.text_input("টিকার:", "EURUSD=X")
timeframe = st.selectbox("টাইমফ্রেম:", ["5m", "15m", "1h", "1d"])
period = st.selectbox("পিরিয়ড:", ["5d", "1mo", "3mo", "6mo", "1y"])

if st.button("🔍 সিগন্যাল জেনারেট করো"):
    try:
        data = yf.download(ticker, period=period, interval=timeframe)
        if data.empty:
            st.error("⚠️ ডাটা আনা যায়নি। অন্য টিকার/টাইমফ্রেম ট্রাই করো।")
        else:
            signals = build_signals(data)
            st.success("✅ সিগন্যাল জেনারেট হয়েছে!")
            st.dataframe(signals.tail(20))

            latest_signal = signals['signal'].iloc[-1]
            if latest_signal == "BUY":
                st.markdown("### 📈 সর্বশেষ সিগন্যাল: **BUY**")
            elif latest_signal == "SELL":
                st.markdown("### 📉 সর্বশেষ সিগন্যাল: **SELL**")
            else:
                st.markdown("### ⏸ সর্বশেষ সিগন্যাল: **HOLD**")

    except Exception as e:
        st.error(f"Error: {e}")
