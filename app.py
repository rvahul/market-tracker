import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# --- 1. SETTINGS & STYLING ---
st.set_page_config(page_title="ProMarket Terminal", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0e11; }
    div[data-testid="stMetric"] {
        background-color: #1e2329;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=300)
def get_market_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        return df
    except:
        return pd.DataFrame()

def get_signal(df):
    if df.empty or len(df) < 20: 
        return "NEUTRAL", "#808080", "Connecting to exchange..."
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    current = df['Close'].iloc[-1]
    if current > sma20:
        return "BUY / ADOPT", "#00ff88", "Bullish Trend: Price > 20MA"
    else:
        return "SELL / CAUTION", "#ff3b3b", "Bearish Trend: Price < 20MA"

# --- 3. SIDEBAR: THE SWITCH LOGIC ---
st.sidebar.title("🔥 Trending Assets")

# Market Type Selector (This is the "Brain" that fixes your issue)
market_focus = st.sidebar.radio("Choose Market to Analyze:", ["India (NSE)", "Global (US)"])

# Define Asset Lists
trending_in = {"Reliance": "RELIANCE.NS", "HDFC Bank": "HDFCBANK.NS", "Tata Motors": "TATAMOTORS.NS"}
trending_gl = {"NVIDIA": "NVDA", "Apple": "AAPL", "Bitcoin": "BTC-USD"}

if market_focus == "India (NSE)":
    selected_name = st.sidebar.selectbox("Select Indian Stock", list(trending_in.keys()))
    target_ticker = trending_in[selected_name]
else:
    selected_name = st.sidebar.selectbox("Select Global Asset", list(trending_gl.keys()))
    target_ticker = trending_gl[selected_name]

# --- 4. TOP METRICS (FIXED HEADERS) ---
st.title("📊 Global Intelligence Terminal")
st.caption(f"Viewing: {selected_name} ({target_ticker})")

indices = {"Nifty 50": "^NSEI", "S&P 500": "^GSPC", "Bitcoin": "BTC-USD"}
top_cols = st.columns(3)

for col, (name, ticker) in zip(top_cols, indices.items()):
    data = get_market_data(ticker)
    if not data.empty:
        curr = data['Close'].iloc[-1]
        prev = data['Close'].iloc[-2]
        change = ((curr - prev) / prev) * 100
        col.metric(name, f"{curr:,.2f}", f"{change:.2f}%")

st.divider()

# --- 5. MAIN CHART & SIGNAL ---
left_col, right_col = st.columns([3, 1])
df_main = get_market_data(target_ticker)

with left_col:
    st.subheader(f"{selected_name} Live Analysis")
    if not df_main.empty:
        fig = go.Figure(data=[go.Candlestick(
            x=df_main.index, open=df_main['Open'], high=df_main['High'],
            low=df_main['Low'], close=df_main['Close'],
            increasing_line_color='#00ff88', decreasing_line_color='#ff3b3b'
        )])
        fig.update_layout(template="plotly_dark", height=500, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, width='stretch')
    else:
        st.error("Unable to fetch data. Please check ticker symbol or internet.")

with right_col:
    st.subheader("Smart Signal")
    signal, s_color, reason = get_signal(df_main)
    
    st.markdown(f"""
        <div style="background-color:{s_color}22; padding:20px; border-radius:10px; border:2px solid {s_color}; text-align:center;">
            <h1 style="color:{s_color}; margin:0; font-size:25px;">{signal}</h1>
            <p style="color:white; margin-top:10px; font-size:14px;">{reason}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("Market Sentiment")
    sentiment_val = 75 if signal == "BUY / ADOPT" else 30
    st.progress(sentiment_val)
    st.caption(f"Sentiment Score: {sentiment_val}%")