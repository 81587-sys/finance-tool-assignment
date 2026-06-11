from __future__ import annotations

from dataclasses import dataclass
from io import StringIO

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="金融工具作業",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded",
)


APP_CSS = """
<style>
    .stApp {
        background:
            radial-gradient(circle at 16% 12%, rgba(66, 69, 76, .34), transparent 32rem),
            radial-gradient(circle at 82% 10%, rgba(52, 69, 75, .24), transparent 34rem),
            radial-gradient(circle at 58% 86%, rgba(30, 44, 52, .28), transparent 36rem),
            linear-gradient(135deg, #0f1113 0%, #181a1f 47%, #0b0d10 100%);
        background-size: cover;
        background-attachment: fixed;
        color: #e8eaed;
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        opacity: .52;
        background-image:
            linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,.028) 1px, transparent 1px);
        background-size: 64px 64px;
        mask-image: radial-gradient(circle at 52% 38%, black 0%, black 46%, transparent 78%);
        animation: gridDrift 22s linear infinite;
    }

    .stApp::after {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        background:
            linear-gradient(120deg, transparent 0%, rgba(138, 180, 248, .08) 42%, transparent 56%),
            linear-gradient(250deg, transparent 0%, rgba(129, 201, 149, .055) 38%, transparent 60%);
        background-size: 220% 220%;
        mix-blend-mode: screen;
        animation: signalSweep 18s ease-in-out infinite alternate;
    }

    [data-testid="stHeader"] {
        background: rgba(17, 19, 21, .82);
        backdrop-filter: blur(12px);
    }

    [data-testid="stSidebar"] {
        background: #17191d;
        border-right: 1px solid #2c3036;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        position: relative;
        z-index: 2;
    }

    .hero {
        padding: 1.2rem 1.4rem;
        border: 1px solid #343941;
        border-left: 5px solid #8ab4f8;
        background: rgba(32, 35, 40, .92);
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 18px 48px rgba(0, 0, 0, .34);
    }

    .hero h1 {
        margin: 0 0 .4rem 0;
        color: #f1f3f4;
        font-size: 2.35rem;
    }

    .hero p {
        color: #bdc1c6;
        font-size: 1rem;
        margin: 0;
        line-height: 1.6;
    }

    .info-panel {
        border: 1px solid #343941;
        background: rgba(32, 35, 40, .9);
        border-radius: 8px;
        padding: 1rem;
        color: #e8eaed;
    }

    .info-panel h3 {
        margin-top: 0;
        color: #f1f3f4;
    }

    .info-panel li {
        margin-bottom: .35rem;
    }

    [data-testid="stMetric"] {
        background: rgba(32, 35, 40, .86);
        border: 1px solid #343941;
        border-radius: 8px;
        padding: .9rem 1rem;
        box-shadow: 0 12px 32px rgba(0, 0, 0, .22);
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        color: #f1f3f4;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: .4rem;
        border-bottom: 1px solid #343941;
    }

    .stTabs [data-baseweb="tab"] {
        background: #202328;
        border-radius: 8px 8px 0 0;
        color: #bdc1c6;
    }

    .stTabs [aria-selected="true"] {
        color: #f1f3f4;
        background: #2a2d33;
    }

    div[data-testid="stDataFrame"],
    div[data-testid="stCodeBlock"],
    div[data-testid="stAlert"] {
        border-radius: 8px;
    }

    .stSlider [data-baseweb="slider"] div {
        color: #8ab4f8;
    }

    .market-flow {
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 1;
        overflow: hidden;
        opacity: .56;
    }

    .market-flow svg {
        width: 118vw;
        height: 118vh;
        transform: translate(-6vw, -7vh);
        filter: drop-shadow(0 0 14px rgba(138, 180, 248, .14));
        animation: fieldFloat 24s ease-in-out infinite alternate;
    }

    .flow-line {
        fill: none;
        stroke-linecap: round;
        stroke-linejoin: round;
        stroke-dasharray: 24 18;
        animation: flowDash 10s linear infinite;
    }

    .flow-line.primary {
        stroke: rgba(138, 180, 248, .48);
        stroke-width: 1.35;
    }

    .flow-line.secondary {
        stroke: rgba(154, 160, 166, .22);
        stroke-width: 1;
        animation-duration: 14s;
        animation-direction: reverse;
    }

    .flow-line.accent {
        stroke: rgba(129, 201, 149, .34);
        stroke-width: 1.15;
        animation-duration: 12s;
    }

    .flow-node {
        fill: rgba(232, 234, 237, .48);
        animation: nodePulse 4.8s ease-in-out infinite;
    }

    .flow-node.accent {
        fill: rgba(129, 201, 149, .68);
        animation-delay: -1.6s;
    }

    @keyframes gridDrift {
        from { background-position: 0 0, 0 0; }
        to { background-position: 64px 64px, 64px 64px; }
    }

    @keyframes signalSweep {
        from { background-position: 0% 42%, 100% 64%; opacity: .54; }
        to { background-position: 100% 58%, 0% 40%; opacity: .86; }
    }

    @keyframes flowDash {
        from { stroke-dashoffset: 0; }
        to { stroke-dashoffset: -84; }
    }

    @keyframes fieldFloat {
        from { transform: translate(-6vw, -7vh) scale(1); }
        to { transform: translate(-4vw, -5vh) scale(1.025); }
    }

    @keyframes nodePulse {
        0%, 100% { opacity: .22; r: 2.2; }
        50% { opacity: .9; r: 3.8; }
    }

    @media (prefers-reduced-motion: reduce) {
        .stApp::before,
        .stApp::after,
        .market-flow svg,
        .flow-line,
        .flow-node {
            animation: none;
        }
    }
</style>
"""


FLOW_BACKGROUND = """
<div class="market-flow" aria-hidden="true">
    <svg viewBox="0 0 1440 900" preserveAspectRatio="none">
        <path class="flow-line secondary" d="M-40 165 C 130 112, 240 210, 390 166 S 650 84, 820 134 S 1080 246, 1488 118" />
        <path class="flow-line primary" d="M-60 310 C 96 286, 178 186, 328 226 S 552 408, 724 322 S 988 142, 1168 238 S 1336 388, 1490 300" />
        <path class="flow-line accent" d="M-80 465 C 120 514, 258 358, 438 404 S 688 604, 872 506 S 1078 342, 1238 398 S 1392 508, 1518 436" />
        <path class="flow-line secondary" d="M-60 650 C 158 592, 310 706, 466 642 S 704 474, 864 558 S 1068 770, 1246 672 S 1408 546, 1510 612" />
        <path class="flow-line primary" d="M-30 790 C 134 724, 244 812, 384 754 S 584 620, 742 674 S 968 850, 1134 780 S 1310 654, 1500 724" />
        <circle class="flow-node" cx="328" cy="226" r="3" />
        <circle class="flow-node accent" cx="724" cy="322" r="3" />
        <circle class="flow-node" cx="872" cy="506" r="3" />
        <circle class="flow-node accent" cx="1168" cy="238" r="3" />
        <circle class="flow-node" cx="1246" cy="672" r="3" />
        <circle class="flow-node accent" cx="742" cy="674" r="3" />
    </svg>
</div>
"""


@dataclass(frozen=True)
class StrategyConfig:
    initial_cash: float
    first_entry_ratio: float
    add_entry_ratio: float
    take_profit: float
    stop_loss: float
    fast_window: int
    slow_window: int


@st.cache_data
def make_demo_prices(rows: int = 260) -> pd.DataFrame:
    """Create stable demo data so the app always renders on Streamlit Cloud."""
    rng = np.random.default_rng(41471204)
    dates = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=rows)
    drift = 0.00055
    shock = rng.normal(0, 0.016, size=rows)
    close = 620 * np.exp(np.cumsum(drift + shock))
    volume = rng.integers(18_000, 82_000, size=rows) * 1000

    return pd.DataFrame(
        {
            "Date": dates,
            "Close": close.round(2),
            "Volume": volume,
        }
    )


def parse_market_csv(uploaded_file) -> pd.DataFrame:
    raw = uploaded_file.getvalue().decode("utf-8-sig")
    df = pd.read_csv(StringIO(raw))

    candidates = {
        "date": ["date", "Date", "日期", "交易日期"],
        "close": ["close", "Close", "收盤價", "收盤", "Adj Close", "adj_close"],
        "volume": ["volume", "Volume", "成交量"],
    }
    column_map: dict[str, str] = {}
    for target, names in candidates.items():
        for name in names:
            if name in df.columns:
                column_map[target] = name
                break

    if "date" not in column_map or "close" not in column_map:
        raise ValueError("CSV 至少需要日期欄位與收盤價欄位，例如 Date, Close。")

    result = pd.DataFrame(
        {
            "Date": pd.to_datetime(df[column_map["date"]], errors="coerce"),
            "Close": pd.to_numeric(df[column_map["close"]], errors="coerce"),
        }
    )
    if "volume" in column_map:
        result["Volume"] = pd.to_numeric(df[column_map["volume"]], errors="coerce")
    else:
        result["Volume"] = np.nan

    result = result.dropna(subset=["Date", "Close"]).sort_values("Date")
    if result.empty:
        raise ValueError("CSV 讀取後沒有可用價格資料。")
    return result.reset_index(drop=True)


def add_indicators(df: pd.DataFrame, fast_window: int, slow_window: int) -> pd.DataFrame:
    prices = df.copy()
    prices["FastMA"] = prices["Close"].rolling(fast_window).mean()
    prices["SlowMA"] = prices["Close"].rolling(slow_window).mean()
    prices["DailyReturn"] = prices["Close"].pct_change().fillna(0)
    prices["Drawdown"] = prices["Close"] / prices["Close"].cummax() - 1
    return prices


def run_strategy(prices: pd.DataFrame, config: StrategyConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    cash = config.initial_cash
    shares = 0.0
    avg_cost = 0.0
    entry_count = 0
    logs: list[dict[str, object]] = []
    equity_rows: list[dict[str, object]] = []

    for row in prices.itertuples(index=False):
        date = row.Date
        price = float(row.Close)
        fast_ma = getattr(row, "FastMA")
        slow_ma = getattr(row, "SlowMA")

        signal_buy = pd.notna(fast_ma) and pd.notna(slow_ma) and fast_ma > slow_ma
        signal_exit = shares > 0 and (
            price >= avg_cost * (1 + config.take_profit)
            or price <= avg_cost * (1 - config.stop_loss)
            or (pd.notna(fast_ma) and pd.notna(slow_ma) and fast_ma < slow_ma)
        )

        action = "觀望"
        reason = "條件未觸發"

        if signal_exit:
            cash += shares * price
            pnl = (price - avg_cost) * shares
            reason = "止盈" if price >= avg_cost * (1 + config.take_profit) else "止損或均線轉弱"
            logs.append(
                {
                    "日期": date.date(),
                    "動作": "賣出",
                    "價格": round(price, 2),
                    "股數": round(shares, 4),
                    "原因": reason,
                    "損益": round(pnl, 2),
                }
            )
            shares = 0.0
            avg_cost = 0.0
            entry_count = 0
            action = "賣出"

        elif signal_buy and shares == 0 and cash > 0:
            budget = cash * config.first_entry_ratio
            bought = budget / price
            cash -= budget
            shares += bought
            avg_cost = price
            entry_count = 1
            action = "首次買進"
            reason = "短均線站上長均線"
            logs.append(
                {
                    "日期": date.date(),
                    "動作": action,
                    "價格": round(price, 2),
                    "股數": round(bought, 4),
                    "原因": reason,
                    "損益": 0.0,
                }
            )

        elif signal_buy and shares > 0 and entry_count < 3 and price < avg_cost * 0.985:
            budget = cash * config.add_entry_ratio
            if budget > 0:
                bought = budget / price
                cash -= budget
                new_value = avg_cost * shares + budget
                shares += bought
                avg_cost = new_value / shares
                entry_count += 1
                action = "分批加碼"
                reason = "趨勢仍在，但價格低於成本"
                logs.append(
                    {
                        "日期": date.date(),
                        "動作": action,
                        "價格": round(price, 2),
                        "股數": round(bought, 4),
                        "原因": reason,
                        "損益": 0.0,
                    }
                )

        equity_rows.append(
            {
                "Date": date,
                "Close": price,
                "Cash": cash,
                "Shares": shares,
                "Equity": cash + shares * price,
                "Action": action,
                "Reason": reason,
            }
        )

    equity = pd.DataFrame(equity_rows)
    trades = pd.DataFrame(logs)
    return equity, trades


def make_chart(prices: pd.DataFrame, trades: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=prices["Date"],
            y=prices["Close"],
            mode="lines",
            name="收盤價",
            line=dict(color="#8ab4f8", width=2.4),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=prices["Date"],
            y=prices["FastMA"],
            mode="lines",
            name="短期均線",
            line=dict(color="#81c995", width=1.7),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=prices["Date"],
            y=prices["SlowMA"],
            mode="lines",
            name="長期均線",
            line=dict(color="#fdd663", width=1.7),
        )
    )

    if not trades.empty:
        buys = trades[trades["動作"].isin(["首次買進", "分批加碼"])]
        sells = trades[trades["動作"] == "賣出"]
        fig.add_trace(
            go.Scatter(
                x=buys["日期"],
                y=buys["價格"],
                mode="markers",
                name="買進點",
                marker=dict(color="#81c995", size=11, symbol="triangle-up"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=sells["日期"],
                y=sells["價格"],
                mode="markers",
                name="賣出點",
                marker=dict(color="#f28b82", size=11, symbol="triangle-down"),
            )
        )

    fig.update_layout(
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(32,35,40,.92)",
        font=dict(color="#e8eaed"),
        margin=dict(l=20, r=20, t=25, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(gridcolor="rgba(232,234,237,.09)"),
        yaxis=dict(gridcolor="rgba(232,234,237,.09)", title="價格"),
    )
    return fig


def format_money(value: float) -> str:
    return f"${value:,.0f}"


st.markdown(APP_CSS + FLOW_BACKGROUND, unsafe_allow_html=True)

st.markdown(
    """
    <section class="hero">
        <h1>金融工具作業：量化交易初探</h1>
        <p>
            用 Python 的清單、迴圈、判斷與條件中斷，模擬新手投資者如何用規則克服貪婪與恐懼。
            本工具支援歷史股價 CSV、均線訊號、止盈、止損、分批進場與交易紀錄視覺化。
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("策略參數")
    uploaded = st.file_uploader("上傳歷史股價 CSV", type=["csv"])
    sample_csv = make_demo_prices(120).to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "下載範例歷史股價 CSV",
        data=sample_csv,
        file_name="sample_stock_prices.csv",
        mime="text/csv",
    )
    fast_window = st.slider("短期均線天數", 3, 40, 10)
    slow_window = st.slider("長期均線天數", 10, 120, 30)
    st.caption("均線天數是每一天往前回看幾個交易日的平均值，線條會每天重新計算並連成完整趨勢。")
    initial_cash = st.number_input("初始資金", min_value=10_000, value=1_000_000, step=10_000)
    first_entry_ratio = st.slider("首次進場資金比例", 5, 100, 35) / 100
    add_entry_ratio = st.slider("分批加碼資金比例", 5, 60, 20) / 100
    take_profit = st.slider("止盈比例", 1, 40, 12) / 100
    stop_loss = st.slider("止損比例", 1, 40, 8) / 100

if slow_window <= fast_window:
    st.warning("長期均線天數需要大於短期均線天數，系統已自動調整長期均線。")
    slow_window = fast_window + 5

try:
    source_label = "內建示範股價"
    base_prices = make_demo_prices()
    if uploaded is not None:
        base_prices = parse_market_csv(uploaded)
        source_label = uploaded.name
except Exception as exc:
    st.error(f"資料讀取失敗：{exc}")
    st.stop()

prices = add_indicators(base_prices, fast_window, slow_window)
config = StrategyConfig(
    initial_cash=float(initial_cash),
    first_entry_ratio=first_entry_ratio,
    add_entry_ratio=add_entry_ratio,
    take_profit=take_profit,
    stop_loss=stop_loss,
    fast_window=fast_window,
    slow_window=slow_window,
)
equity, trades = run_strategy(prices, config)

final_equity = float(equity["Equity"].iloc[-1])
total_return = final_equity / config.initial_cash - 1
max_drawdown = float((equity["Equity"] / equity["Equity"].cummax() - 1).min())
sell_trades = trades[trades["動作"] == "賣出"] if not trades.empty else pd.DataFrame()
win_rate = 0 if sell_trades.empty else (sell_trades["損益"] > 0).mean()

metric_cols = st.columns(4)
metric_cols[0].metric("最終資產", format_money(final_equity), f"{total_return:.2%}")
metric_cols[1].metric("最大回撤", f"{max_drawdown:.2%}")
metric_cols[2].metric("完成交易數", f"{len(sell_trades)} 筆")
metric_cols[3].metric("勝率", f"{win_rate:.1%}")

st.caption(f"目前資料來源：{source_label}，共 {len(prices)} 筆交易日。")
st.plotly_chart(make_chart(prices, trades), width="stretch")
st.caption(
    f"讀圖方式：短期均線是每個交易日取最近 {fast_window} 個交易日的收盤價平均，"
    f"長期均線則取最近 {slow_window} 個交易日平均；因此不是只顯示 {fast_window} 天，"
    "而是把每天算出的平均值連起來看趨勢。"
)

tab_overview, tab_logic, tab_records, tab_data = st.tabs(
    ["成果總覽", "策略邏輯", "交易紀錄", "資料檢查"]
)

with tab_overview:
    left, right = st.columns([1.1, 1])
    with left:
        st.subheader("專題對應")
        st.markdown(
            """
            <div class="info-panel">
                <ul>
                    <li>動態數據：可使用內建示範資料，也可上傳真實歷史股價 CSV。</li>
                    <li>策略升級：加入止盈、止損與最多三次分批進場。</li>
                    <li>視覺化：圖上標示買進點、加碼點與賣出點。</li>
                    <li>風險控制：用最大回撤與停損規則呈現紀律交易。</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.subheader("目前判斷")
        last_action = equity["Action"].iloc[-1]
        last_reason = equity["Reason"].iloc[-1]
        st.info(f"最後一天狀態：{last_action}。原因：{last_reason}。")
        st.line_chart(equity.set_index("Date")["Equity"], height=220)

with tab_logic:
    st.subheader("核心流程")
    st.code(
        """
for 每一天股價 in 歷史資料:
    if 已持有股票 and 達到止盈或止損:
        賣出並中斷這一輪持倉
    elif 短期均線 > 長期均線 and 尚未持有:
        用部分資金首次買進
    elif 趨勢仍成立 and 價格低於成本 and 加碼次數未滿:
        分批加碼降低平均成本
    else:
        繼續監控
        """.strip(),
        language="python",
    )
    st.write(
        "這段邏輯對應報告中的清單、迴圈、判斷與條件中斷；投資者不再用感覺追高殺低，而是用固定規則執行。"
    )

with tab_records:
    st.subheader("交易紀錄")
    if trades.empty:
        st.warning("目前參數沒有觸發交易，可調整均線或止盈止損比例。")
    else:
        st.dataframe(trades, width="stretch", hide_index=True)
        csv = trades.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "下載交易紀錄 CSV",
            data=csv,
            file_name="trade_records.csv",
            mime="text/csv",
        )

with tab_data:
    st.subheader("股價資料")
    st.dataframe(prices.tail(80), width="stretch", hide_index=True)
    st.write("CSV 欄位可使用 Date/Close/Volume，或中文欄位：日期、收盤價、成交量。")
