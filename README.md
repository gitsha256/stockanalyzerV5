# NSE Stock Analyzer V5

A comprehensive, institutional-grade technical analysis suite for the National Stock Exchange (NSE). V5 introduces a proprietary Manual RRG engine, structural chart pattern recognition, and Weinstein stage analysis to identify high-conviction trading opportunities.

# run requirements
`pip install -r requirements.txt`

## 🚀 Project Components

| Script | Description |
| :--- | :--- |
| `sectoralanalysis.py` | **The Master Strategy Bridge.** A proprietary Manual RRG engine that synthesizes sector indices, calculates multi-factor Rotational Scores, and enforces sector-specific trade filters. |
| `analyzer.py` | **The V5 Core Engine.** Handles data ingestion, split adjustments, and complex technical computation including **Structural Pattern recognition** and **Weinstein Stage Analysis**. |
| `formatter.py` | **The Visualization Engine.** Converts snapshots to professional multi-sheet Excel reports with automated heat-mapping. |
| `analyzerall.py` | Full-market version of the analyzer. Processes a larger set of symbols from `symbolsall.csv`. |
| `screen_stocks.py` | **The Ranking Engine.** Applies multi-weighted scoring algorithms to produce top-tier Intraday and Weekly Swing candidates. |
| `test_screen_stocks.py` | **The Sandbox Engine.** Experimental version of the screener used to test quality-of-entry improvements (EMA distance, pullbacks, contraction) before deployment. |
| `sma_filter.py` | Utility to find stocks where multiple SMAs (20, 50, 100, 200) are converging (volatility confluence). |
| `montecarlo.py` | **Risk Management.** Fetches live Nifty/VIX data to provide position sizing and Monte Carlo price simulations for professional options trading. |

> Before running `montecarlo.py`, create and activate a Python virtual environment to keep dependencies isolated.
> ```powershell
> python -m venv venv
> .\venv\Scripts\Activate.ps1
> ```

## 🔄 Sector Rotation & RRG Analysis (`sectoralanalysis.py`)

V5 places `sectoralanalysis.py` at the heart of the workflow. It acts as the "Bridge" between raw market data and actionable trades. Unlike standard scanners, it uses a **Manual RRG (Relative Rotation Graph) Engine** to identify where institutional money is flowing.

### Key Features:
- **Index Synthesis**: Automatically builds equal-weighted sector indices directly from your local historical data (`data.csv`).
- **Manual RRG Calculation**: Calculates **RS-Ratio** (trend) and **RS-Momentum** (velocity) against the Nifty 50 benchmark without needing external expensive data feeds.
- **Rotational Scoring**: An institutional-grade multi-factor score (0-100) based on:
    - **RSI Breadth**: % of stocks in the sector with RSI >= 50.
    - **EMA Breadth**: % of stocks trading above their 50-day SMA.
    - **Delivery Conviction**: Average delivery percentage across the sector.
    - **Heading Score**: Rewards sectors accelerating North-East towards the "Leading" quadrant.
- **Automatic Filtering**: Only permits swing candidates from "Leading" or "Improving" sectors, ensuring you are always trading with the wind at your back.

## 📈 V5 Structural Analysis Features
The analyzer now performs deep structural scans:
- **Weinstein Stages**: Automatically classifies stocks into Stage 1 (Base), Stage 2 (Uptrend), Stage 3 (Top), or Stage 4 (Downtrend).
- **Dual-Zone Analysis**: V5 provides two distinct structural positioning layers to evaluate risk-to-reward:
    - **Long-Term Zone (ZONE)**: Calculated using `order=252` anchors (52-week extremes).
    - **Medium-Term Zone (MT_Zone)**: Calculated using `order=60` anchors to reflect the stock's position within the most recent ~3 month swing structure.
    - Both utilize adaptive percentile logic (Discount, Equilibrium, Premium) to normalize positioning across different stock volatilities.
- **Pattern Engine**: Detects complex patterns including Cup and Handle, Rounding Bottoms, Wedges, Channels, and Triangles using multi-timeframe pivot analysis.

## 📊 Abbreviation Dictionary

The analysis outputs (e.g., `29-05-26snapshot_all.csv`) use the following column headers:

### Core Data
- **symb**: Stock Symbol.
- **clos**: Adjusted Closing Price.
- **open**: Market Opening Price.
- **high / low**: Daily High and Low prices.
- **chan**: Daily percentage change from Open to Close.
- **volu**: Total Traded Volume.
- **DlPer**: Delivery Percentage (Genuine accumulation indicator).
- **date**: The trading date of the record.
- **sect**: The industry sector the stock belongs to.
- **ascr / arnk**: Activity Score (Liquidity in ₹) and its Rank across the market.

### Technical Indicators
- **rsi / wrsi**: Daily and Weekly Relative Strength Index (Momentum).
- **adx**: Average Directional Index (Trend Strength).
- **obv**: On-Balance Volume (Cumulative volume flow).
- **s020 / s050 / s100 / s200**: Simple Moving Averages (20, 50, 100, 200 days).
- **g200 / g050 / g020**: Boolean - is price above the 200, 50, or 20 SMA?
- **ws30**: Weekly 30-period SMA (Weinstein's preferred indicator).
- **vola**: Annualized Volatility (based on 21-day standard deviation).
- **bbup / bbdn**: Boolean - is price breaking out above the upper or below the lower Bollinger Band?
- **bbbw**: Bollinger Bandwidth (Volatility measurement).
- **bbsq**: Bollinger Squeeze (Boolean) - true if volatility is at a 300-day relative low.
- **bbdn**: Boolean - price closing below the lower Bollinger Band.
- **CMF_20**: 20-day Chaikin Money Flow (volume-weighted accumulation/distribution).
- **SUPERT_7_3.0 / SUPERTd_7_3.0**: Supertrend indicator values and trend direction.
- **STOCHk_14_3_3 / STOCHd_14_3_3**: Stochastic oscillator %K and %D values.
- **EMA_21**: 21-day exponential moving average.
- **SQZ_ON / SQZ_OFF / SQZ_NO**: Squeeze state flags for volatility compression/breakout.
- **WILLR_14**: Williams %R momentum oscillator.
- **EFI_13**: Elder Force Index (volume-based momentum).
- **RSI_2**: Short-term 2-period Relative Strength Index.

### Trend & Stage Analysis
- **stge**: Weinstein Stage (Stage 1: Base, Stage 2: Uptrend, Stage 3: Top, Stage 4: Downtrend).
- **tren**: Trend Direction (Uptrend, Sideways, Downtrend).
- **tstr**: Trend Strength (Strong, Moderate, Weak).
- **zone**: Price Location (Premium, Near Premium, Equilibrium, Near Discount, Discount).
- **MT_Zone**: Medium-term Price Location (position within the recent 60-day swing range).
- **vrnk / rrnk**: Volume Rank and Relative Volume Rank.
- **delt**: Percentage distance currently below the 52-week high.
- **h52h / l52l**: 52-Week High and Low prices.
- **shgh / slw**: Most recent Swing High and Swing Low prices.
- **eqb**: Equilibrium price (Midpoint between Swing High and Swing Low).

### Volume & Activity
- **rvol**: Relative Volume (Current volume vs. 20-day average).
- **vspk**: Volume Spike (Boolean - true if volume is > 2x average).
- **vtrd**: Volume Trend (Increasing or Decreasing).
- **ascr**: Activity Score (Price × Volume / 10 Million) - measures ₹ liquidity.
- **arnk**: Activity Rank (Ranked liquidity across the processed list).

### Chart Patterns
- **mpat**: Main chart pattern detected (e.g., Cup and Handle, Double Bottom).
- **pcon**: Pattern Confidence score (0–99).
- **patt**: String containing all detected patterns and their scores.
- **xpat**: Miscellaneous patterns detected in the background.
- **ppnt**: Pivot points (Date@Price) defining the detected pattern structure.
- **psta / pend**: The start and end dates of the detected pattern.

## 🛠️ Usage Workflow

### 📡 Operating the Analyzer (`analyzer.py` / `analyzerall.py`)
The analyzer is your database manager. You should generally follow the menus in numerical order:

1.  **Menu 1 - Fetch**: Used for initial setup or downloading historical blocks.
    *   Input a start/end date or a "years back" value (e.g., 3.0) to build your `raw_data.csv`.
2.  **Menu 2 - Update**: Your daily maintenance tool.
    *   It checks the last date in your CSV and only fetches the missing data until today.
3.  **Menu 3 - Adjust**: **Essential for technical accuracy.**
    *   This scans for price gaps caused by stock splits or bonuses and mathematically adjusts historical prices. Without this, your SMAs and RSI will be broken. Generates `data.csv`.
4.  **Menu 4 - Analyze**: The signal generator.
    *   Enter a date range (or press Enter for the latest).
    *   Choose whether to run CPU-intensive Pattern Recognition (Chart/Candle).
    *   Outputs the final `snapshot.csv` (or `snapshot_all.csv`).

### 🔍 Screening and Filtering
Once the snapshots are generated, use the secondary tools:

1.  **Run Screener**: To get the top-ranked Intraday and Swing picks:
    ```bash
    python screen_stocks.py 29-05-26snapshot_all.csv
    ```
2.  **Analyze Sectors**: Filter candidates by institutional rotation:
    ```bash
    python sectoralanalysis.py 29-05-26snapshot_all.csv
    ```
3.  **SMA Filter**: Run `sma_filter.py` to find "Tightening" setups where multiple SMAs are converging (volatility contraction).

### 📋 `screen_stocks.py` Logic

Reads your snapshot CSV (same schema as StockAnalyzerV4 output)
and produces two ranked lists:
  1. Intraday candidates
  2. Weekly swing candidates

Filename pattern  : DD-MM-YYsnapshot.csv  (date auto-parsed for display)
Run               : python screen_stocks.py [path/to/snapshot.csv]

| Mode | Primary Hard Filters | Key Scoring Weights |
| :--- | :--- | :--- |
| **Intraday** | Stage 2, RSI 45-72, ADX > 18, RVol > 0.8 | RVol (25), logAscr (5.0), BBBW Contraction (15), EMA21 Proximity Bonus |
| **Swing** | Stage 2, wRSI 50-75, Delivery > 35%, ADX > 18 | Strong Trend (15), BB Squeeze (10), RSI2 Pullback Bonus, Tiered Delivery Scoring |

### 🟢 Excel Formatting (`formatter.py`)
The formatter is designed to turn raw CSV data into a visually intuitive heat-map of market signals. It processes snapshots and applies conditional formatting based on institutional technical consensus.

**Usage:**
1. **Manual**: `python formatter.py path/to/your_snapshot.csv`
2. **Automatic**: `python formatter.py` (It will auto-detect the latest `*snapshot.csv` in your directory).

**Key Features:**
- **Automated Logic**:
    - **Booleans**: Automatically highlights signals like `bbup` (Bollinger Breakout) or `vspk` (Volume Spike).
    - **Trend Alignment**: Color codes `tren` (Direction) and `tstr` (Strength) to help you spot strong uptrends instantly.
    - **Range Analysis**: Validates `rsi`, `wrsi`, and `Stochastics` against ideal entry/exit zones.
    - **Contrarian Highlighting**: Specifically flags `zone` (Discount/Premium) and `delt` (52W High distance) to identify mean-reversion or breakout setups.
- **Multi-Sheet Architecture**:
    - **Main Analysis**: The primary dashboard with frozen headers and auto-adjusted column widths.
    - **Chart Patterns**: Separates verbose pattern data (`psta`, `pend`, `ppnt`) to keep the main view clean.
    - **Legend**: Includes an embedded guide explaining every color rule and condition.

**Visual Standards:**
- **Light Green (#C6EFCE)**: Bullish / Signal Active.
- **Light Red (#FFC7CE)**: Bearish / Signal Inactive.
- **Dark Fills with White Text**: Highlights extreme conditions (e.g., very close to or far from 52W Highs).

## 📋 Requirements

- Python 3.12+
- `pandas`, `numpy`, `nselib`, `pandas-ta`, `scipy`, `plotly`, `streamlit`, `yfinance`, `requests`, `openpyxl`, `tqdm`

---
*Disclaimer: This tool is for educational and analytical purposes only. Trading involves significant risk.*
