#we are developing an one stop web tool#

import streamlit as st
import pandas as pd
import os
import numpy as np
from datetime import datetime, time
import plotly.graph_objects as go
from Updater.oldanalyzer import StockAnalyzerEngine, perform_technical_analysis, CONFIG as CFG_500
from fullmarket import CONFIG as CFG_ALL
from screen_stocks import screen_intraday, screen_swing, INTRADAY_CFG, SWING_CFG

st.set_page_config(page_title="NSE Stock Analyzer Pro", layout="wide", page_icon="📈")

def main():
    st.sidebar.title("🚀 NSE Pro Analyzer")

    # 1. Market Scope Selection
    market_scope = st.sidebar.selectbox("Market Scope", ["Nifty 500", "Full Market"])
    
    # Scope-aware Engine Initialization
    current_cfg = CFG_500 if market_scope == "Nifty 500" else CFG_ALL
    if 'engine' not in st.session_state or st.session_state.get('active_scope') != market_scope:
        st.session_state.engine = StockAnalyzerEngine(config=current_cfg)
        st.session_state.active_scope = market_scope

    # 2. Navigation
    menu = st.sidebar.radio("Navigate", ["Data Engine Settings", "Market Dashboard", "Picks & Screeners", "Options Risk Calc"])

    if menu == "Data Engine Settings":
        render_data_manager()
    elif menu == "Market Dashboard":
        render_dashboard()
    elif menu == "Picks & Screeners":
        render_screeners()
    elif menu == "Options Risk Calc":
        render_options()

def render_dashboard():
    st.title("📊 Market Dashboard")
    snapshot_file = st.session_state.engine.config['ANALYSIS_OUTPUT_FILE']
    
    if os.path.exists(snapshot_file):
        df = pd.read_csv(snapshot_file)
        snap_date = df['date'].iloc[0] if 'date' in df.columns else "Unknown"
        st.info(f"📅 Currently viewing snapshot from: **{snap_date}**")
        
        # --- Dashboard Filters ---
        with st.expander("🔍 Filter Market Universe", expanded=True):
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                sel_sect = st.multiselect("Sectors", sorted(df['sect'].unique()))
            with f2:
                sel_stge = st.multiselect("Weinstein Stages", sorted(df['stge'].unique()))
            with f3:
                sel_tren = st.multiselect("Trends", sorted(df['tren'].unique()))
            with f4:
                sel_patt = st.multiselect("Chart Patterns", sorted(df['mpat'].unique()))

        # Filter logic
        filtered_df = df.copy()
        if sel_sect:
            filtered_df = filtered_df[filtered_df['sect'].isin(sel_sect)]
        if sel_stge:
            filtered_df = filtered_df[filtered_df['stge'].isin(sel_stge)]
        if sel_tren:
            filtered_df = filtered_df[filtered_df['tren'].isin(sel_tren)]
        if sel_patt:
            filtered_df = filtered_df[filtered_df['mpat'].isin(sel_patt)]

        # Top Level Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric(f"Symbols ({st.session_state.active_scope})", len(filtered_df))
        m2.metric("Stage 2 Breakouts", len(filtered_df[filtered_df['stge'].str.contains("Stage 2", na=False)]))
        m3.metric("Market RSI Strength", f"{filtered_df['rsi'].mean():.1f}")

        # Interactive Explorer
        st.subheader("🔍 Symbol Explorer")
        selected_symb = st.selectbox("Search Filtered Results", [""] + sorted(filtered_df['symb'].tolist()))
        
        if selected_symb:
            row = filtered_df[filtered_df['symb'] == selected_symb].iloc[0]
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(f"### {selected_symb}")
                st.info(f"**Sector:** {row.get('sect', 'N/A')}")
                st.write(f"**Current Price:** ₹{row['clos']}")
                st.write(f"**Trend:** {row['tren']} ({row['tstr']})")
                st.write(f"**Weinstein Stage:** {row['stge']}")
                st.write(f"**Detected Pattern:** {row['mpat']} ({row['pcon']}%)")
            
            with c2:
                # Fetch history for chart
                hist = st.session_state.engine.load_data(source='adjusted')
                if not hist.empty and selected_symb in hist['symbols'].values:
                    symb_hist = hist[hist['symbols'] == selected_symb].sort_values('datetime')
                    fig = go.Figure(data=[
                        go.Candlestick(x=symb_hist['datetime'],
                                       open=symb_hist['open'], high=symb_hist['high'],
                                       low=symb_hist['low'], close=symb_hist['close'],
                                       name="Price")
                    ])
                    fig.update_layout(
                        title=f"{selected_symb} - Interactive Price Action",
                        xaxis_rangeslider_visible=False,
                        height=450,
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Historical data for this symbol not found in data.csv. Run 'Update' in Settings.")

        st.divider()
        st.subheader("📋 Market Data Table")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    else:
        st.warning(f"No snapshot found for {st.session_state.active_scope}. Go to Data Engine Settings to generate it.")

def render_screeners():
    st.title("🎯 High Conviction Picks")
    snapshot_file = st.session_state.engine.config['ANALYSIS_OUTPUT_FILE']
    
    if not os.path.exists(snapshot_file):
        st.error("Missing snapshot data. Go to Data Engine Settings to generate it.")
        return

    df = pd.read_csv(snapshot_file)
    snap_date = df['date'].iloc[0] if 'date' in df.columns else "Unknown"
    st.info(f"🎯 Picks generated from snapshot date: **{snap_date}**")
    
    tab1, tab2, tab3 = st.tabs(["🔥 Intraday", "🕒 Weekly Swing", "🛰️ SMA Confluence"])
    
    with tab1:
        res_i, size_i = screen_intraday(df, INTRADAY_CFG)
        st.subheader(f"Top Intraday Candidates (Pool: {size_i})")
        st.table(res_i[['symb', 'clos', 'chan', 'rvol', 'score']])

    with tab2:
        res_s, size_s = screen_swing(df, SWING_CFG)
        st.subheader(f"Top Swing Candidates (Pool: {size_s})")
        st.table(res_s[['symb', 'clos', 'wrsi', 'DlPer', 'score']])

    with tab3:
        st.subheader("Moving Average Confluence (Tightening Setups)")
        st.info("Finds stocks where SMA 20, 50, and 100 are converging near the SMA 200.")
        
        threshold = st.slider("Convergence Threshold (%)", 1.0, 10.0, 5.0, step=0.5) / 100
        
        sma_cols = ['s020', 's050', 's100', 's200']
        # Filter data that has the required SMA columns
        sma_df = df.dropna(subset=sma_cols + ['symb']).copy()
        
        def check_confluence(row):
            base = row['s200']
            if base == 0: return False
            return all(abs(row[col] - base) / base <= threshold for col in ['s020', 's050', 's100'])
        
        confluent_stocks = sma_df[sma_df.apply(check_confluence, axis=1)]
        
        st.write(f"Found {len(confluent_stocks)} stocks within {threshold*100:.1f}% convergence.")
        st.dataframe(confluent_stocks[['symb', 'clos', 's020', 's050', 's100', 's200', 'sect']], use_container_width=True)

def render_options():
    st.title("🎲 Option Probability & Risk Simulation")
    
    if st.button("🌐 Fetch Live Nifty & VIX"):
        import yfinance as yf
        try:
            with st.spinner("Fetching from Yahoo Finance..."):
                nifty = yf.Ticker("^NSEI")
                vix = yf.Ticker("^INDIAVIX")
                
                def get_price(t):
                    p = t.fast_info.get('last_price')
                    if p is None or np.isnan(p) or p <= 0:
                        h = t.history(period='5d')
                        p = h['Close'].iloc[-1] if not h.empty else 0.0
                    return p

                st.session_state.live_nifty = get_price(nifty)
                st.session_state.live_vix = get_price(vix)
                st.success("Market data updated!")
                if st.session_state.live_vix == 0:
                    st.warning("VIX data could not be retrieved; using default.")
        except Exception as e:
            st.error(f"Could not fetch live data: {e}")

    col1, col2, col3 = st.columns(3)
    with col1:
        s0 = st.number_input("Current Nifty Price", 
                             value=st.session_state.get('live_nifty', 24200.0), step=50.0)
        vix = st.number_input("India VIX (%)", 
                              value=st.session_state.get('live_vix', 15.0), step=0.5)
    with col2:
        days = st.slider("Days to Expiry", 1, 10, 2)
        cap = st.number_input("Trading Capital (₹)", value=100000, step=10000)
    with col3:
        lot_size = st.number_input("Nifty Lot Size", value=25)
        risk_pct = st.slider("Risk Per Trade (%)", 0.5, 5.0, 3.0, step=0.5) / 100

    risk_free = 0.068

    if st.button("🔥 Run Comprehensive Monte Carlo Simulation"):
        # 1. 1-Min Scalping Sizing
        st.subheader("🎯 1-Min Scalping Strategy")
        minutes_per_year = 252 * 375
        sigma_1min = (vix / 100) / np.sqrt(minutes_per_year)
        expected_1min_move = s0 * sigma_1min
        stop_distance = 2 * expected_1min_move
        max_risk = cap * risk_pct
        cost_per_lot = stop_distance * lot_size
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Exp. Move (1m)", f"±{expected_1min_move:.1f}")
        c2.metric("2σ Stop Dist", f"{stop_distance:.1f}")
        c3.metric("Risk per Lot", f"₹{cost_per_lot:.0f}")
        if cost_per_lot > 0:
            lot_qty = int(max_risk / cost_per_lot)
            c4.metric(f"Max Lots ({risk_pct*100:.1f}%)", lot_qty)

        # 2. Intraday Monte Carlo
        st.subheader("🕐 Intraday Monte Carlo")
        now = datetime.now()
        target_time = now.replace(hour=15, minute=0, second=0, microsecond=0)
        
        if now.time() < time(9, 15):
            mins_remaining = 345 # 9:15 to 15:00
        elif now >= target_time:
            mins_remaining = 0
        else:
            mins_remaining = int((target_time - now).total_seconds() / 60)

        if mins_remaining > 0:
            n_sim = 10000
            dt_intra = 1 / (252 * 375)
            sigma = vix / 100
            Z_intra = np.random.normal(0, 1, (n_sim, mins_remaining))
            log_ret_intra = (risk_free - 0.5 * sigma**2) * dt_intra + sigma * np.sqrt(dt_intra) * Z_intra
            paths_intra = s0 * np.exp(np.cumsum(log_ret_intra, axis=1))
            final_intra = paths_intra[:, -1]
            
            p1, p2, p3 = st.columns(3)
            p1.metric(f"Prob Bullish ({mins_remaining}m left)", f"{(final_intra > s0).mean()*100:.1f}%")
            p2.metric("Intra Low (5th %)", f"{np.percentile(final_intra, 5):.0f}")
            p3.metric("Intra High (95th %)", f"{np.percentile(final_intra, 95):.0f}")
        else:
            st.info("Intraday trading window (until 15:00) has closed.")

        # 3. Weekly / Expiry Monte Carlo
        st.subheader(f"📅 Expiry Simulation ({days} Days)")
        dt = 1/252
        sigma = vix / 100
        n_sim = 10000
        np.random.seed(42)
        Z = np.random.normal(0, 1, (n_sim, days))
        log_returns = (risk_free - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z
        paths = s0 * np.exp(np.cumsum(log_returns, axis=1))
        final_prices = paths[:, -1]
        
        w1, w2, w3, w4 = st.columns(4)
        w1.metric("Prob Ends Higher", f"{(final_prices > s0).mean()*100:.1f}%")
        w2.metric("Mean Level", f"{final_prices.mean():.0f}")
        w3.metric("Median Level", f"{np.median(final_prices):.0f}")
        w4.metric("Std Dev", f"±{final_prices.std():.0f} pts")

        # 4. R:R Summary
        st.subheader("⚖️ Reward:Risk Summary")
        var_5 = np.percentile(final_prices, 5)
        var_95 = np.percentile(final_prices, 95)
        upside = var_95 - s0
        downside = s0 - var_5
        rr_ratio = upside / downside if downside != 0 else 0
        
        r1, r2, r3 = st.columns(3)
        r1.info(f"Potential Upside: +{upside:.0f} pts")
        r2.info(f"Potential Downside: -{downside:.0f} pts")
        if rr_ratio >= 1.5:
            r3.success(f"Bias: BULLISH (R:R {rr_ratio:.2f})")
        elif rr_ratio <= 0.67:
            r3.error(f"Bias: BEARISH (R:R {rr_ratio:.2f})")
        else:
            r3.warning(f"Bias: NEUTRAL (R:R {rr_ratio:.2f})")

        st.divider()
        st.caption(f"💡 Capital Guide: To trade 1 lot safely with {risk_pct*100:.1f}% risk, you need ₹{cost_per_lot / risk_pct:,.0f} capital.")

def render_data_manager():
    st.title("⚙️ Data Engine")
    engine = st.session_state.engine
    
    col1, col2 = st.columns(2)
    
    # Shared progress container for this page
    progress_container = st.empty()
    
    def update_progress(current, total, text):
        progress_container.progress(current / total, text=f"🚀 {text} ({current}/{total})")

    with col1:
        st.subheader("1. Data Acquisition")
        years = st.number_input("History Period (Years)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)
        if st.button("🚀 Initial Historical Fetch"):
            success, msg = engine.fetch_historical_data(years, progress_callback=update_progress)
            if success: st.success(msg)
            else: st.error(msg)

        if st.button("🔄 Delta Update (New Only)"):
            success, msg = engine.update_data(progress_callback=update_progress)
            if success: st.success(msg)
            else: st.error(msg)
                
    with col2:
        st.subheader("2. Snapshot Generation")
        target_date = st.date_input("Analysis Target Date", value=datetime.now().date())
        if st.button("🔍 Run Full Technical Analysis"):
            data = engine.load_data(source='adjusted')
            if not data.empty:
                target_dt = pd.to_datetime(target_date)
                data_filtered = data[data['datetime'] <= target_dt]
                if not data_filtered.empty:
                    results = perform_technical_analysis(data_filtered, engine.sector_df, engine.logger, progress_callback=update_progress)
                    results.to_csv(engine.config['ANALYSIS_OUTPUT_FILE'], index=False)
                    st.success(f"Analysis complete for {target_date}!")
                else:
                    st.error(f"No data available on or before {target_date}.")
            else:
                st.error("No data available to analyze.")

if __name__ == "__main__":
    main()
