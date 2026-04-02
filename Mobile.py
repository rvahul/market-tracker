import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# --- 1. MOBILE OPTIMIZATION SETTINGS ---
st.set_page_config(
    page_title="Market Mobile", 
    layout="wide", 
    initial_sidebar_state="collapsed" # Better for mobile to start with chart
)

# Custom CSS to make buttons and text larger for touch/mobile
st.markdown("""
    <style>
    /* Make metrics more compact for mobile screens */
    [data-testid="stMetricValue"] { font-size: 24px !important; }
    
    /* Rounded corners for a mobile-app feel */
    div[data-testid="stMetric"] {
        background-color: #1e2329;
        border-radius: 15px;
        padding: 10px;
    }
    
    /* Hide the scientific Streamlit footer */
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=300)
def get_market_data(ticker):
    try:
        df = yf.Ticker(ticker).history(period="6mo")
        return df
    except:
        return pd.DataFrame()

def get_signal(df):
    if df.empty or len(df) < 20: return "WAIT", "#808080"
    sma20 = df['Close'].rolling(window=20).mean().iloc[-1]
    current = df['Close'].iloc[-1]
    return ("BUY / ADOPT", "#00ff88") if current > sma20 else ("SELL / CAUTION", "#ff3b3b")

# --- 3. MOBILE NAVIGATION (SIDEBAR) ---
st.sidebar.title("📱 App Navigation")
market_focus = st.sidebar.radio("Market Focus:", ["India (NSE)", "Global (US)"])

trending_in = {"Reliance": "RELIANCE.NS", "HDFC Bank": "HDFCBANK.NS", "Tata Motors": "TATAMOTORS.NS"}
trending_gl = {"NVIDIA": "NVDA", "Apple": "AAPL", "Bitcoin": "BTC-USD"}

if market_focus == "India (NSE)":
    selected_name = st.sidebar.selectbox("Asset:", list(trending_in.keys()))
    target_ticker = trending_in[selected_name]
else:
    selected_name = st.sidebar.selectbox("Asset:", list(trending_gl.keys()))
    target_ticker = trending_gl[selected_name]

# --- 4. TOP KPI ROW ---
# On mobile, these will automatically stack vertically
idx_cols = st.columns(3)
indices = {"Nifty": "^NSEI", "S&P 500": "^GSPC", "BTC": "BTC-USD"}

for col, (name, ticker) in zip(idx_cols, indices.items()):
    data = get_market_data(ticker)
    if not data.empty:
        curr = data['Close'].iloc[-1]
        change = ((curr - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
        col.metric(name, f"{curr:,.0f}", f"{change:.2f}%")

st.divider()

# --- 5. MAIN CHART & ADVICE ---
df_main = get_market_data(target_ticker)
signal, s_color = get_signal(df_main)

# Highlight the Buy/Sell Signal at the top for quick mobile viewing
st.markdown(f"<div style='text-align:center; background-color:{s_color}22; border-radius:10px; border:1px solid {s_color}; padding:10px;'><h2 style='color:{s_color}; margin:0;'>{signal}</h2></div>", unsafe_allow_html=True)

st.subheader(f"{selected_name} Trend")
fig = go.Figure(data=[go.Candlestick(
    x=df_main.index, open=df_main['Open'], high=df_main['High'],
    low=df_main['Low'], close=df_main['Close'],
    increasing_line_color='#00ff88', decreasing_line_color='#ff3b3b'
)])
fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
st.plotly_chart(fig, width='stretch')

st.info(f"**Research Tip:** The signal is based on the 20-day Moving Average. Currently, {selected_name} is in a {'strong' if signal == 'BUY / ADOPT' else 'weak'} phase.")