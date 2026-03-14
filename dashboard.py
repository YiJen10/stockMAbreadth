import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np # NEW: For safe math calculations
import requests
import time
from io import StringIO
import plotly.graph_objects as go 
import gc 
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Market Breadth Dashboard")

# --- HELPER: CLEAN TICKERS ---
def clean_us_ticker(ticker):
    return str(ticker).replace(".", "-")

# --- DATA FETCHING (US) ---
@st.cache_data(ttl=86400)
def get_sp500_tickers():
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        response = requests.get(url, headers=headers)
        df = pd.read_html(StringIO(response.text))[0]
        return [clean_us_ticker(t) for t in df['Symbol'].tolist()]
    except Exception as e:
        return ["AAPL", "MSFT", "GOOGL"]

@st.cache_data(ttl=86400)
def get_nasdaq100_tickers():
    try:
        url = "https://en.wikipedia.org/wiki/Nasdaq-100"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers)
        tables = pd.read_html(StringIO(response.text))
        for table in tables:
            if 'Ticker' in table.columns:
                return [clean_us_ticker(t) for t in table['Ticker'].tolist()]
        return ["AAPL", "MSFT", "NVDA"]
    except Exception as e:
        return ["AAPL", "MSFT", "NVDA"]

# --- INITIALIZE SESSION STATE FOR TICKERS ---
if 'custom_tickers' not in st.session_state:
    st.session_state['custom_tickers'] = {
        "Hang Seng (HSI)": [
            "0001.HK", "0002.HK", "0003.HK", "0005.HK", "0006.HK", "0011.HK", "0012.HK", "0016.HK", "0017.HK", "0027.HK",
            "0066.HK", "0101.HK", "0175.HK", "0241.HK", "0267.HK", "0285.HK", "0288.HK", "0316.HK", "0386.HK", "0388.HK",
            "0522.HK", "0669.HK", "0688.HK", "0700.HK", "0762.HK", "0823.HK", "0857.HK", "0868.HK", "0883.HK", "0939.HK",
            "0941.HK", "0960.HK", "0968.HK", "0981.HK", "0992.HK", "1038.HK", "1044.HK", "1088.HK", "1093.HK", "1109.HK",
            "1113.HK", "1177.HK", "1209.HK", "1211.HK", "1299.HK", "1378.HK", "1398.HK", "1810.HK", "1876.HK", "1928.HK",
            "1929.HK", "1997.HK", "2007.HK", "2015.HK", "2020.HK", "2269.HK", "2313.HK", "2318.HK", "2319.HK", "2331.HK",
            "2382.HK", "2388.HK", "2628.HK", "2688.HK", "2899.HK", "3690.HK", "3692.HK", "3968.HK", "3988.HK", "6098.HK",
            "6618.HK", "6690.HK", "6862.HK", "9618.HK", "9633.HK", "9888.HK", "9961.HK", "9988.HK", "9999.HK", "0019.HK",
            "0836.HK", "1099.HK", "1193.HK", "1972.HK", "3998.HK", "0010.HK", "0031.HK", "0041.HK", "0083.HK" 
        ],
        "Hang Seng Tech": [
            "0700.HK", "9988.HK", "3690.HK", "1810.HK", "9618.HK", "1024.HK", "2015.HK", "0981.HK", 
            "0285.HK", "0780.HK", "0992.HK", "1347.HK", "1797.HK", "2382.HK", "3888.HK", "6618.HK", 
            "9626.HK", "9888.HK", "9961.HK", "9999.HK", "0522.HK", "0772.HK", "1478.HK", "1833.HK", 
            "2013.HK", "2018.HK", "3033.HK", "6060.HK", "6690.HK", "9868.HK"
        ],
        "FBM KLCI": [
            "1155.KL", "1023.KL", "1295.KL", "5347.KL", "5183.KL", "6033.KL", "5285.KL", "4065.KL", 
            "2445.KL", "1961.KL", "4707.KL", "5819.KL", "6947.KL", "5296.KL", "8869.KL", "6012.KL", 
            "3816.KL", "4197.KL", "5225.KL", "5398.KL", "5211.KL", "4863.KL", "1066.KL", "5168.KL", 
            "0166.KL", "7084.KL", "4677.KL", "6742.KL", "5326.KL", "5681.KL"
        ],
        "MYX: Technology": [
            "0002.KL", "0005.KL", "0006.KL", "0008.KL", "0010.KL", "0012.KL", "0018.KL", "0020.KL", 
            "0021.KL", "0022.KL", "0023.KL", "0025.KL", "0029.KL", "0034.KL", "0035.KL", "0036.KL",
            "0040.KL", "0041.KL", "0045.KL", "0051.KL", "0055.KL", "0060.KL", "0065.KL", "0068.KL",
            "0069.KL", "0070.KL", "0079.KL", "0083.KL", "0085.KL", "0086.KL", "0090.KL", "0093.KL",
            "0097.KL", "0104.KL", "0105.KL", "0106.KL", "0107.KL", "0109.KL", "0111.KL", "0112.KL",
            "0113.KL", "0117.KL", "0118.KL", "0119.KL", "0120.KL", "0126.KL", "0127.KL", "0128.KL",
            "0131.KL", "0132.KL", "0138.KL", "0140.KL", "0143.KL", "0145.KL", "0146.KL", "0151.KL", 
            "0152.KL", "0154.KL", "0155.KL", "0156.KL", "0157.KL", "0158.KL", "0163.KL", "0165.KL", 
            "0166.KL", "0167.KL", "0169.KL", "0174.KL", "0175.KL", "0176.KL", "0181.KL", "0191.KL", 
            "0196.KL", "0200.KL", "0201.KL", "0202.KL", "0203.KL", "0205.KL", "0206.KL", "0208.KL", 
            "0209.KL", "0212.KL", "0236.KL", "0246.KL", "0249.KL", "0251.KL", "0253.KL", "0258.KL", 
            "0259.KL", "0263.KL", "0265.KL", "0272.KL", "0275.KL", "0276.KL", "0277.KL", "0278.KL", 
            "0279.KL", "0290.KL", "0305.KL", "0306.KL", "0319.KL", "0328.KL", "0343.KL", "0358.KL", 
            "3867.KL", "4359.KL", "4456.KL", "5005.KL", "5011.KL", "5028.KL", "5036.KL", "5161.KL", 
            "5162.KL", "5195.KL", "5204.KL", "5216.KL", "5286.KL", "5292.KL", "5301.KL", "5309.KL", 
            "5347.KL", "7022.KL", "7160.KL", "7181.KL", "7204.KL", "8338.KL", "9008.KL", "9075.KL", 
            "9334.KL", "9377.KL", "9393.KL"
        ],
        "MYX: Plantation": [
            "2089.KL", "7501.KL", "9695.KL", "2291.KL", "5138.KL", "5112.KL", "5026.KL", "5027.KL",
            "5135.KL", "2569.KL", "5323.KL", "5319.KL", "8966.KL", "7382.KL", "7054.KL", "5223.KL",
            "5222.KL", "5113.KL", "5069.KL", "5029.KL", "5012.KL", "4936.KL", "4383.KL", "4316.KL",
            "3948.KL", "2593.KL", "2542.KL", "2453.KL", "2445.KL", "2135.KL", "2038.KL", "1996.KL",
            "1929.KL", "1902.KL", "1899.KL", "0355.KL", "0189.KL", "5126.KL", "5285.KL", "6262.KL",
            "9059.KL", "2607.KL", "1961.KL", "2054.KL"
        ]
    }

# --- CALCULATION LOGIC (HOLIDAY AWARE) ---
@st.cache_data(ttl=300)
def get_breadth_data(index_name, tickers):
    if not tickers:
        return None, None

    try:
        # 1. Download data (Threads enabled for speed)
        data = yf.download(tickers, period="5y", progress=False, threads=True)
        
        if data.empty:
            return None, None

        # 2. Bulletproof Close Price Extractor 
        # This prevents yfinance from dumping Volume and High/Low prices into the math
        if isinstance(data.columns, pd.MultiIndex):
            if 'Close' in data.columns.get_level_values(0):
                df_close = data['Close'].copy()
            elif 'Close' in data.columns.get_level_values(1):
                df_close = data.xs('Close', level=1, axis=1).copy()
            else:
                return None, None
        elif 'Close' in data.columns:
            df_close = data[['Close']].copy()
        else:
            return None, None

        # Free memory immediately
        del data 
        gc.collect()

        # 3. Safely format Dates and Drop Duplicates
        df_close.index = pd.to_datetime(df_close.index, utc=True).tz_localize(None).normalize()
        df_close = df_close[~df_close.index.duplicated(keep='first')]
        df_close = df_close.sort_index()

        # 4. Clean empty columns and rows
        df_close = df_close.apply(pd.to_numeric, errors='coerce')
        df_close = df_close.dropna(axis=1, how='all').dropna(axis=0, how='all')
        df_close = df_close.ffill()

        if df_close.empty:
            return None, None

        # 5. Calculate MAs 
        ma20 = df_close.rolling(window=20).mean()
        ma50 = df_close.rolling(window=50).mean()
        ma200 = df_close.rolling(window=200).mean()

        # 6. Strict Daily Percentage Math
        # We replace 0 with NaN so we don't divide by zero. 
        # This allows Plotly to start the line on Day 20 instead of drawing false zeros.
        count_20 = ma20.notna().sum(axis=1).replace(0, np.nan)
        count_50 = ma50.notna().sum(axis=1).replace(0, np.nan)
        count_200 = ma200.notna().sum(axis=1).replace(0, np.nan)

        above_20 = (df_close > ma20).sum(axis=1)
        above_50 = (df_close > ma50).sum(axis=1)
        above_200 = (df_close > ma200).sum(axis=1)

        # Build the final dataframe with exact percentages
        history_df = pd.DataFrame(index=df_close.index)
        history_df["% > MA20"] = (above_20 / count_20 * 100).round(2)
        history_df["% > MA50"] = (above_50 / count_50 * 100).round(2)
        history_df["% > MA200"] = (above_200 / count_200 * 100).round(2)
        
        # Drop rows where we have absolutely no breadth data (the first 19 days)
        history_df = history_df.dropna(how='all')

        if history_df.empty:
            return None, None

        # Get the latest Snapshot safely
        latest = {
            "Index": index_name,
            "% > MA20": history_df["% > MA20"].dropna().iloc[-1] if not history_df["% > MA20"].isna().all() else 0,
            "% > MA50": history_df["% > MA50"].dropna().iloc[-1] if not history_df["% > MA50"].isna().all() else 0,
            "% > MA200": history_df["% > MA200"].dropna().iloc[-1] if not history_df["% > MA200"].isna().all() else 0
        }
        
        return latest, history_df

    except Exception as e:
        return None, None

# --- HELPER: VALIDATE TICKER ---
def check_ticker_validity(ticker_symbol):
    try:
        test_data = yf.download(ticker_symbol, period="1d", progress=False)
        if test_data.empty:
            return False, None
            
        tkr = yf.Ticker(ticker_symbol)
        name = tkr.info.get('shortName', 'Name Not Available')
        return True, name
    except:
        return False, None

# --- MAIN APP ---
st.title("📊 Live Market Breadth Dashboard")
myt_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
st.write(f"Last Updated: {myt_time} (MYT)")

# Create Tabs
tab1, tab2 = st.tabs(["📈 Dashboard", "⚙️ Manage Tickers"])

with tab1:
    if st.button('Refresh Data Now'):
        st.cache_data.clear()
        st.rerun()

    with st.spinner("Fetching data..."):
        sp500_list = get_sp500_tickers()
        ndx_list = get_nasdaq100_tickers()

    constituents = {
        "S&P 500 (SPX)": sp500_list,
        "Nasdaq 100 (NDX)": ndx_list,
        "Hang Seng (HSI)": st.session_state['custom_tickers']["Hang Seng (HSI)"],
        "Hang Seng Tech": st.session_state['custom_tickers']["Hang Seng Tech"],
        "FBM KLCI": st.session_state['custom_tickers']["FBM KLCI"],
        "MYX: Technology": st.session_state['custom_tickers']["MYX: Technology"], 
        "MYX: Plantation": st.session_state['custom_tickers']["MYX: Plantation"]
    }

    # PROCESS ALL DATA
    table_data = []
    history_data = {}

    cols = st.columns(len(constituents))
    progress_bar = st.progress(0)

    for i, (name, tickers) in enumerate(constituents.items()):
        cols[i].metric(label=name.split("(")[0], value=len(tickers))
        latest, history = get_breadth_data(name, tickers)
        if latest:
            table_data.append(latest)
            history_data[name] = history
        progress_bar.progress((i + 1) / len(constituents))

    progress_bar.empty()

    # DISPLAY TABLE
    if table_data:
        df_table = pd.DataFrame(table_data)

        def color_breadth(val):
            if isinstance(val, (int, float)):
                if val >= 80: return 'background-color: #4CAF50; color: white'
                if val <= 20: return 'background-color: #FF5252; color: white'
            return ''

        st.subheader("Market Breadth Snapshot")
        st.dataframe(
            df_table.style.map(color_breadth, subset=["% > MA20", "% > MA50", "% > MA200"])
                      .format("{:.2f}", subset=["% > MA20", "% > MA50", "% > MA200"]),
            use_container_width=True
        )
    else:
        st.error("No data available.")

    # DISPLAY INTERACTIVE CHART (PLOTLY)
    st.divider()
    st.subheader("📈 Historical Market Breadth Chart")

    col1, col2 = st.columns([1, 4])

    with col1:
        selected_index = st.selectbox("Select Index:", list(constituents.keys()))
        show_ma20 = st.checkbox("% > MA20", value=False)
        show_ma50 = st.checkbox("% > MA50", value=True) 
        show_ma200 = st.checkbox("% > MA200", value=False)

    with col2:
        if selected_index in history_data:
            df_chart = history_data[selected_index]
            
            fig = go.Figure()
            if show_ma20:
                fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart["% > MA20"], mode='lines', name='% > MA20', line=dict(color='blue')))
            if show_ma50:
                fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart["% > MA50"], mode='lines', name='% > MA50', line=dict(color='red')))
            if show_ma200:
                fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart["% > MA200"], mode='lines', name='% > MA200', line=dict(color='green')))

            fig.update_layout(
                title=f"{selected_index} Breadth History",
                xaxis=dict(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1m", step="month", stepmode="backward"),
                            dict(count=6, label="6m", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1y", step="year", stepmode="backward"),
                            dict(step="all")
                        ])
                    ),
                    rangeslider=dict(visible=True), 
                    type="date"
                ),
                yaxis=dict(range=[0, 100], title="Percentage (%)"),
                height=600,
                hovermode="x unified"
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Data not available for this index.")

# --- TICKER MANAGEMENT TAB ---
with tab2:
    st.subheader("Manage Non-US Index Tickers")
    
    editable_indices = list(st.session_state['custom_tickers'].keys())
    index_to_edit = st.selectbox("Select Index to view/modify:", editable_indices)
    
    st.write(f"**Current Constituents: {index_to_edit} ({len(st.session_state['custom_tickers'][index_to_edit])} stocks)**")
    
    df_display = pd.DataFrame({
        "Ticker Code": st.session_state['custom_tickers'][index_to_edit],
        "Company Name": ["(Fetch on replacement)"] * len(st.session_state['custom_tickers'][index_to_edit])
    })
    st.dataframe(df_display, use_container_width=True, height=250)
    
    st.divider()
    
    st.subheader("🔒 Update a Ticker")
    pwd = st.text_input("Enter password to unlock edit mode:", type="password")
    
    if pwd == "tyqbabi":
        st.success("Access Granted.")
        st.info("Select an outdated ticker below and enter the new one to replace it.")
        
        col_old, col_new = st.columns(2)
        with col_old:
            outdated_ticker = st.selectbox("Select Outdated Ticker:", st.session_state['custom_tickers'][index_to_edit])
        
        with col_new:
            new_ticker = st.text_input("Enter New Ticker (e.g., 0001.HK):").strip().upper()
            
        if st.button("Validate & Replace Ticker"):
            if not new_ticker:
                st.warning("Please enter a new ticker.")
            elif new_ticker == outdated_ticker:
                st.warning("The new ticker is the same as the old one.")
            else:
                with st.spinner(f"Searching Yahoo Finance for '{new_ticker}'..."):
                    is_valid, company_name = check_ticker_validity(new_ticker)
                    
                    if is_valid:
                        st.success(f"✅ Found! {company_name} ({new_ticker})")
                        
                        ticker_list = st.session_state['custom_tickers'][index_to_edit]
                        replace_index = ticker_list.index(outdated_ticker)
                        ticker_list[replace_index] = new_ticker
                        
                        st.cache_data.clear()
                        time.sleep(1.5) 
                        st.rerun() 
                    else:
                        st.error(f"❌ Error: Could not find any trading data for '{new_ticker}'. Please check the symbol.")