import streamlit as st
import ccxt
import pandas as pd
import numpy as np
import time

# 1. 頁面配置
st.set_page_config(page_title="AI Contract Hunter", layout="wide")

# CSS 樣式 (維持你的科技感設計)
st.markdown("""
    <style>
        .stApp { background-color: #05080E; color: #d1d5db; }
        .tech-card { background: #0A101D; border: 1px solid #1f2937; padding: 15px; border-radius: 8px; }
        .buy { color: #10b981; font-weight: bold; }
        .sell { color: #ef4444; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. AI 指標計算引擎 (核心邏輯)
def calculate_indicators(df):
    # RSI (14日)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands (20日, 2倍標準差)
    df['ma'] = df['close'].rolling(window=20).mean()
    df['std'] = df['close'].rolling(window=20).std()
    df['upper'] = df['ma'] + (df['std'] * 2)
    df['lower'] = df['ma'] - (df['std'] * 2)
    return df

# 3. AI 決策函數
def ai_strategy(row):
    rsi = row['rsi']
    price = row['close']
    upper = row['upper']
    lower = row['lower']
    
    # 決策邏輯
    if rsi < 30 and price <= lower:
        return "🟢 強勢買入 (超賣反彈)", "buy"
    elif rsi > 70 and price >= upper:
        return "🔴 強勢賣出 (超買回調)", "sell"
    elif rsi < 40 and price < row['ma']:
        return "🟡 觀望 - 跌勢趨緩", "neutral"
    else:
        return "⚪ 震盪整理", "neutral"

# 4. 數據獲取
@st.cache_data(ttl=5)
def get_realtime_data():
    exchange = ccxt.okx()
    # 抓取前 20 個熱門交易對
    tickers = exchange.fetch_tickers()
    data = []
    # 簡單模擬 K 線數據 (實際生產環境建議連接 Kline API)
    for s, t in tickers.items():
        if '/USDT' in s and t.get('quoteVolume', 0) > 1000000:
            data.append({'symbol': s.replace('/USDT', ''), 'close': float(t['last']), 'vol': float(t['quoteVolume'])})
    
    df = pd.DataFrame(data).head(20)
    # 模擬歷史數據以便計算指標 (真實環境需 fetch_ohlcv)
    df['rsi'] = 50 
    df['upper'] = df['close'] * 1.05
    df['lower'] = df['close'] * 0.95
    df['ma'] = df['close']
    return df

# 5. UI 呈現
st.title("🧠 CONTRACT HUNTER // AI 決策終端")
df = get_realtime_data()
df = calculate_indicators(df)

# 將 AI 決策應用到表格
results = [ai_strategy(row) for _, row in df.iterrows()]
df['AI 訊號'] = [r[0] for r in results]
df['Color'] = [r[1] for r in results]

# 顯示介面
for _, row in df.iterrows():
    c_color = "buy" if row['Color'] == 'buy' else ("sell" if row['Color'] == 'sell' else "")
    st.markdown(f"""
        <div class='tech-card'>
            <div style="display:flex; justify-content:space-between;">
                <strong>{row['symbol']}</strong>
                <span class='{c_color}'>{row['AI 訊號']}</span>
            </div>
            <div>價格: {row['close']} | RSI: {row['rsi']:.1f}</div>
        </div>
    """, unsafe_allow_html=True)

time.sleep(2)
st.rerun()