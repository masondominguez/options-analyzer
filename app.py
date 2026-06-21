from datetime import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import norm
import streamlit as st
import yfinance as yf

from content.models import (
    black_scholes, 
    binomial_tree_american
)
from content.styles import APP_STYLE
from content.tooltips import (
    CALL_POSITION_HELP,
    GREEKS_CHEAT_SHEET, 
    IV_SURFACE,
    OPTION_CHAIN, 
    PAYOUT_DIAGRAM, 
    PRICING_MODELS,
    PROBABILITIES_EXPLAINED
)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_risk_free_rate():
    """Fetches the 13-week Treasury Bill rate (^IRX) to use as the risk-free rate."""
    try:
        irx = yf.Ticker("^IRX")
        # The price of ^IRX is the actual yield percentage (e.g., 5.25)
        latest_rate = irx.history(period="1d")['Close'].iloc[-1]
        return float(latest_rate)
    except Exception:
        # Fallback to 5.0% if the fetch fails
        return 5.0

@st.cache_data(ttl=300, show_spinner=False)
def fetch_iv_surface(ticker_symbol, spot_price, surface_type):
    """Fetch IV across all expirations and return a pivoted DataFrame."""
    ticker = yf.Ticker(ticker_symbol)
    expirations = ticker.options
    today = datetime.today()

    rows = []
    for exp in expirations:
        expiry_date = datetime.strptime(exp, "%Y-%m-%d")
        dte = (expiry_date - today).days
        if dte <= 0:
            continue
        T = dte / 365.0
        try:
            chain = ticker.option_chain(exp)
            df = chain.calls if surface_type == "Call" else chain.puts
            df = df[
                (df['impliedVolatility'] > 0.01) &
                (df['impliedVolatility'] < 5.0) &
                (df['volume'] > 0) &
                (df['strike'] >= spot_price * 0.7) &
                (df['strike'] <= spot_price * 1.3)
            ].copy()
            df['dte'] = dte
            df['moneyness'] = (df['strike'] / spot_price - 1) * 100
            rows.append(df[['strike', 'moneyness', 'dte', 'impliedVolatility']])
        except Exception:
            continue

    if not rows:
        return None

    all_data = pd.concat(rows, ignore_index=True)
    return all_data

# --- USER INTERFACE ---

st.set_page_config(page_title="Options Analyzer", layout="wide")

st.markdown(APP_STYLE, unsafe_allow_html=True)

st.title("Options Analyzer")

# --- PARAMETERS — single collapsible block, visible on all screen sizes ---
with st.expander("⚙️ Parameters", expanded=True):
    row1a, row1b = st.columns([1, 1])
    with row1a:
        ticker_symbol = st.text_input("Ticker Symbol", value="AMD").upper()
    with row1b:
        live_rf_rate = fetch_risk_free_rate()
        risk_free_input = st.number_input(
            "Risk-Free Rate (%)",
            value=live_rf_rate,
            step=0.1,
            help="Defaults to the live 13-week U.S. Treasury Bill yield (^IRX)."
        )

    risk_free_rate = risk_free_input / 100

    if ticker_symbol:
        ticker = yf.Ticker(ticker_symbol)
        try:
            spot_price = ticker.history(period="1d")['Close'].iloc[-1]
            st.success(f"**{ticker_symbol}** spot price: **${spot_price:.2f}**")
        except Exception:
            st.error("Invalid ticker symbol — please try again.")
            st.stop()

        expirations = ticker.options
        if not expirations:
            st.error("No options data found for this ticker.")
            st.stop()

        st.divider()
        row2a, row2b = st.columns([1, 1])
        with row2a:
            selected_expiry = st.selectbox("Expiration Date", expirations)
        with row2b:
            option_type = st.radio("Option Type", ["Call", "Put"], horizontal=True).lower()

        opt_chain = ticker.option_chain(selected_expiry)
        calls = opt_chain.calls
        puts  = opt_chain.puts

        available_strikes = calls['strike'].tolist() if option_type == 'call' else puts['strike'].tolist()

        if 'target_strike' not in st.session_state:
            st.session_state.target_strike = None

        if st.session_state.target_strike in available_strikes:
            default_index = available_strikes.index(st.session_state.target_strike)
        else:
            atm_strike = min(available_strikes, key=lambda x: abs(x - spot_price))
            default_index = available_strikes.index(atm_strike)

        selected_strike = st.selectbox("Strike Price", available_strikes, index=default_index)
        st.session_state.target_strike = selected_strike

# ── Analysis (outside the expander — always visible) ─────────────────────────

# Calculate Time to Expiration (T)
expiry_date = datetime.strptime(selected_expiry, "%Y-%m-%d")
T = (expiry_date - datetime.today()).days / 365.0
if T <= 0:
    T = 0.001

tab1, tab2, tab3 = st.tabs(["📊 Strike Analysis", "📋 Option Chain", "🌐 IV Surface"])

with tab2:
    st.subheader(f"Option Chain — {ticker_symbol} · {selected_expiry}")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Calls**")
        st.dataframe(calls[['strike', 'lastPrice', 'bid', 'ask', 'impliedVolatility', 'volume']], height=300)
    with col2:
        st.markdown("**Puts**")
        st.dataframe(puts[['strike', 'lastPrice', 'bid', 'ask', 'impliedVolatility', 'volume']], height=300)
    with st.expander("📖 How to Read the Option Chain", expanded=False):
        st.markdown(OPTION_CHAIN)

with tab1:
    st.subheader(f"Strike Analysis — {ticker_symbol} {option_type.upper()} ${selected_strike:.0f} · {selected_expiry}")

    df = calls if option_type == "call" else puts
    opt_data = df[df['strike'] == selected_strike].iloc[0]
    iv = opt_data['impliedVolatility']

    dividend_yield = ticker.info.get('dividendYield', 0) or 0.0
    # yfinance has changed scale/units across versions — verify against a known
    # dividend payer (e.g. KO ~3%) before trusting this. If it prints as 3.0
    # instead of 0.03, divide by 100 here.

    st.write(dividend_yield)

    bs_price, delta, gamma, theta, vega, prob_itm = black_scholes(
        spot_price, selected_strike, T, risk_free_rate, iv, option_type, q=dividend_yield)
    bt_price = binomial_tree_american(
        spot_price, selected_strike, T, risk_free_rate, iv, steps=100, option_type=option_type, q=dividend_yield)
    
    with st.container(border=True):
        st.markdown(f"### Theoretical Pricing (IV: {iv*100:.2f}%, DTE: {int(T*365)})")
        mid_price = (opt_data['bid'] + opt_data['ask']) / 2 if opt_data['ask'] > 0 else opt_data['lastPrice']
        m1, m2, m3 = st.columns(3)
        m1.metric("Market Mid Price", f"${mid_price:.2f}")
        m2.metric("European (Black-Scholes)", f"${bs_price:.2f}")
        m3.metric("American (Binomial Tree)", f"${bt_price:.2f}")
        with st.expander("📖 Pricing Models & Probabilities Explained", expanded=False):
            st.markdown(PRICING_MODELS)
    
    with st.container(border=True):
        st.markdown("### Probability at Expiration")
        st.caption(
            "Derived from Black-Scholes (N(d₂) for calls, N(−d₂) for puts). "
            "This is the **risk-neutral, market-implied** probability — not a real-world forecast. "
            "It reflects what the current option price implies about the chance of expiring ITM."
        )
        p1, p2, p3 = st.columns(3)
        p1.metric("Prob. ITM", f"{prob_itm*100:.1f}%",
                  help="Probability the option expires in-the-money based on current IV.")
        p2.metric("Prob. OTM", f"{(1 - prob_itm)*100:.1f}%",
                  help="Probability the option expires worthless.")
        breakeven = (selected_strike + bs_price) if option_type == "call" else (selected_strike - bs_price)
        p3.metric("Breakeven at Expiry", f"${breakeven:.2f}",
                  help="Underlying price at which the buyer neither profits nor loses.")
        with st.expander("📖 Probabilities Explained", expanded=False):
            st.markdown(PROBABILITIES_EXPLAINED)
    
    with st.container(border=True):
        st.markdown("### Greeks (Black-Scholes Base)")
        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Delta", f"{delta:.4f}", help="$ change in option price per $1 move in underlying.")
        g2.metric("Gamma", f"{gamma:.4f}", help="Rate of change of Delta per $1 move.")
        g3.metric("Theta (Daily)", f"{theta:.4f}", help="$ lost per day due to time decay.")
        g4.metric("Vega", f"{vega:.4f}", help="$ change per 1% move in implied volatility.")
        with st.expander("📖 The Greeks Cheat Sheet", expanded=False):
            st.markdown(GREEKS_CHEAT_SHEET)
    
    with st.container(border=True):
        st.markdown("### Payout Diagram at Expiration")
    
        if option_type == 'call':
            position_options = ["Buyer (Long)", "Seller – Naked Call", "Seller – Covered Call"]
            position_help = (CALL_POSITION_HELP)
        else:
            position_options = ["Buyer (Long)", "Seller – Naked Put", "Seller – Cash-Secured Put"]
            position_help = (
                "**Buyer**: pays premium upfront, profits when stock falls below strike, "
                "max loss = premium paid.  \n"
                "**Naked Put**: collects premium, max loss approaches strike − premium if stock "
                "goes to zero — not truly unlimited, but very large without a hedge.  \n"
                "**Cash-Secured Put**: hold enough cash to buy the stock if assigned; "
                "max loss = strike − premium (stock goes to zero)."
            )
    
        position = st.radio(
            "Position",
            position_options,
            key=f"position_toggle_{option_type}",
            help=position_help,
        )
    
        price_range = np.linspace(spot_price * 0.7, spot_price * 1.3, 200)
        premium_paid     = opt_data['ask'] if opt_data['ask']  > 0 else opt_data['lastPrice']
        premium_received = opt_data['bid'] if opt_data['bid']  > 0 else opt_data['lastPrice']
        SHARES = 100
    
        if position == "Buyer (Long)":
            intrinsic        = (np.maximum(0, price_range - selected_strike) if option_type == 'call'
                                else np.maximum(0, selected_strike - price_range))
            payout_per_share = intrinsic - premium_paid
            line_color       = '#2196F3'
            chart_breakeven  = (selected_strike + premium_paid if option_type == 'call'
                                else selected_strike - premium_paid)
            max_profit_str   = ("unlimited" if option_type == 'call'
                                else f"${(selected_strike - premium_paid) * SHARES:,.2f}")
            max_loss_str     = f"${premium_paid * SHARES:,.2f}"
    
        elif position in ("Seller – Naked Call", "Seller – Naked Put"):
            payout_per_share = np.where(
                price_range > selected_strike if option_type == 'call' else price_range < selected_strike,
                (selected_strike - price_range if option_type == 'call' else price_range - selected_strike),
                0
            ) + premium_received
            line_color       = '#FF5722'
            chart_breakeven  = (selected_strike + premium_received if option_type == 'call'
                                else selected_strike - premium_received)
            max_profit_str   = f"${premium_received * SHARES:,.2f}"
            max_loss_str     = ("unlimited" if option_type == 'call'
                                else f"${(selected_strike - premium_received) * SHARES:,.2f}")
    
        elif position == "Seller – Covered Call":
            stock_leg        = price_range - spot_price
            short_call_leg   = np.where(price_range > selected_strike,
                                        selected_strike - price_range, 0) + premium_received
            payout_per_share = stock_leg + short_call_leg
            line_color       = '#4CAF50'
            chart_breakeven  = spot_price - premium_received
            max_profit_str   = f"${(selected_strike - spot_price + premium_received) * SHARES:,.2f}"
            max_loss_str     = f"${(spot_price - premium_received) * SHARES:,.2f}"
    
        else:  # Cash-Secured Put
            payout_per_share = np.where(price_range < selected_strike,
                                        price_range - selected_strike, 0) + premium_received
            line_color       = '#4CAF50'
            chart_breakeven  = selected_strike - premium_received
            max_profit_str   = f"${premium_received * SHARES:,.2f}"
            max_loss_str     = f"${(selected_strike - premium_received) * SHARES:,.2f}"
    
        payout = payout_per_share * SHARES
    
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=price_range, y=np.maximum(payout, 0),
            fill='tozeroy', fillcolor='rgba(76,175,80,0.35)',
            mode='none', showlegend=False, hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=price_range, y=np.minimum(payout, 0),
            fill='tozeroy', fillcolor='rgba(244,67,54,0.35)',
            mode='none', showlegend=False, hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=price_range, y=payout,
            mode='lines', name='P&L',
            line=dict(color=line_color, width=2.5),
            hovertemplate="Underlying: $%{x:.2f}<br>P&L: $%{y:,.2f}<extra></extra>"
        ))
        fig.add_vline(x=selected_strike, line_dash="solid", line_color="#9C27B0", line_width=1.5,
                      annotation_text=f"Strike ${selected_strike:.0f}",
                      annotation_font_color="#9C27B0")
        fig.add_vline(x=spot_price, line_dash="dash", line_color="#555555",
                      annotation_text=f"Spot ${spot_price:.2f}",
                      annotation_font_color="#555555")
        fig.add_vline(x=chart_breakeven, line_dash="dot", line_color=line_color,
                      annotation_text=f"Breakeven ${chart_breakeven:.2f}",
                      annotation_font_color=line_color)
        fig.add_hline(y=0, line_color="#cccccc", line_width=1)
        fig.update_layout(
            xaxis_title="Underlying Price at Expiration",
            yaxis_title="Profit / Loss ($ per contract, 100 shares)",
            template="plotly_white",
            annotations=[
                dict(x=0.01, y=0.97, xref="paper", yref="paper", showarrow=False,
                     text=f"Max Profit: {max_profit_str}",
                     font=dict(color="green", size=12), align="left"),
                dict(x=0.01, y=0.90, xref="paper", yref="paper", showarrow=False,
                     text=f"Max Loss: {max_loss_str}",
                     font=dict(color="red", size=12), align="left"),
            ]
        )
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("📖 How to Read the P&L Chart", expanded=False):
            st.markdown(PAYOUT_DIAGRAM)

with tab3:
    st.subheader("Implied Volatility Surface")
    st.caption("Fetches IV across all available expirations. May take a few seconds to load.")

    iv_ctrl1, iv_ctrl2 = st.columns(2)
    with iv_ctrl1:
        surface_type = st.radio("Surface Type", ["Call", "Put"], key="surface_type", horizontal=True)
    with iv_ctrl2:
        x_axis = st.radio("X-Axis", ["Strike Price", "Moneyness (%)"], key="x_axis", horizontal=True)

    with st.spinner(f"Loading IV surface for {ticker_symbol}..."):
        iv_data = fetch_iv_surface(ticker_symbol, spot_price, surface_type)

    if iv_data is None or iv_data.empty:
        st.warning("Not enough data to build an IV surface for this ticker.")
    else:
        x_col   = 'strike' if x_axis == "Strike Price" else 'moneyness'
        x_label = "Strike Price ($)" if x_axis == "Strike Price" else "Moneyness (%)"

        pivot = iv_data.pivot_table(
            values='impliedVolatility',
            index='dte',
            columns=x_col,
            aggfunc='mean'
        ).sort_index()

        z = pivot.values * 100
        x = pivot.columns.values
        y = pivot.index.values

        surf_fig = go.Figure(data=[go.Surface(
            z=z, x=x, y=y,
            colorscale='RdYlGn_r',
            colorbar=dict(title="IV (%)"),
            hovertemplate=(
                x_label.split(" ")[0] + ": %{x:.1f}<br>"
                "DTE: %{y}d<br>"
                "IV: %{z:.1f}%<extra></extra>"
            )
        )])
        surf_fig.update_layout(
            scene=dict(
                xaxis_title=x_label,
                yaxis_title="Days to Expiration",
                zaxis_title="Implied Volatility (%)",
                camera=dict(eye=dict(x=1.6, y=-1.6, z=0.8)),
                xaxis=dict(backgroundcolor="rgb(245,245,245)"),
                yaxis=dict(backgroundcolor="rgb(240,240,240)"),
                zaxis=dict(backgroundcolor="rgb(235,235,235)"),
            ),
            margin=dict(l=0, r=0, t=30, b=0),
            height=520,
            template="plotly_white",
        )
        st.plotly_chart(surf_fig, use_container_width=True)
        st.caption(
            f"Showing {iv_data['dte'].nunique()} expirations · "
            f"{iv_data[x_col].nunique()} strike points · "
            f"Strikes filtered to ±30% of spot · Cached for 5 min"
        )
        # --- NEW EDUCATIONAL TOOLTIP EXPANDER ---
        with st.expander("📖 How to Interpret the IV Surface", expanded=False):
            st.markdown(IV_SURFACE)
