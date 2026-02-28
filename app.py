# ==========================================================
# Digital Transactions in India – Viksit Bharat 2047
# FINAL MULTI-PAGE STREAMLIT APP (CORRECTED)
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------
st.set_page_config(
    page_title="Viksit Bharat 2047 | Digital Transactions",
    page_icon="🇮🇳",
    layout="wide"
)

# ----------------------------------------------------------
# GLOBAL STYLE
# ----------------------------------------------------------
st.markdown("""
<style>
body { background-color: #ffffff; }
.tiranga {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(90deg,#FF9933,#FFFFFF,#138808);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.kpi {
    padding: 18px;
    border-radius: 12px;
    background: #f7f7f7;
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# HELPERS
# ----------------------------------------------------------
def format_txns(n):
    if n >= 1e9:
        return f"{n/1e9:.2f} Billion"
    elif n >= 1e6:
        return f"{n/1e6:.2f} Million"
    else:
        return f"{n:,.0f}"

# ----------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("upi_transactions_2024.csv")

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Rename amount column safely
    for c in df.columns:
        if "amount" in c:
            df = df.rename(columns={c: "amount_inr"})
            break

    state = (
        df.groupby("sender_state")
        .agg(
            UPI_Volume=("transaction_id", "count"),
            UPI_Value_INR=("amount_inr", "sum"),
            Fraud_Cases=("fraud_flag", "sum")
        )
        .reset_index()
        .rename(columns={"sender_state": "State"})
    )

    state["UPI_Value_Crore"] = state["UPI_Value_INR"] / 1e7
    state["Fraud_per_Million"] = state["Fraud_Cases"] / state["UPI_Volume"] * 1e6
    state["Share_%"] = state["UPI_Volume"] / state["UPI_Volume"].sum() * 100
    state["Avg_Value_per_Txn"] = state["UPI_Value_INR"] / state["UPI_Volume"]

    return state

state_summary = load_data()

# ----------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------
page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Overview",
        "🗺️ Spatial Analysis",
        "📊 Concentration",
        "💰 Formalisation",
        "🚨 Fraud Risk",
        "🔮 2047 Outlook",
        "🤖 AI Policy Assistant"
    ]
)

# ==========================================================
# OVERVIEW
# ==========================================================
if page == "🏠 Overview":
    st.markdown("<div class='tiranga'>Digital Transactions & Viksit Bharat 2047</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='kpi'><h3>{format_txns(state_summary['UPI_Volume'].sum())}</h3>Total Transactions</div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='kpi'><h3>₹{state_summary['UPI_Value_Crore'].sum():,.1f} Cr</h3>Total Value</div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='kpi'><h3>{state_summary['Fraud_Cases'].sum():,}</h3>Fraud Cases</div>", unsafe_allow_html=True)

# ==========================================================
# SPATIAL MAP
# ==========================================================
elif page == "🗺️ Spatial Analysis":
    metric = st.selectbox("Metric", ["UPI_Volume", "UPI_Value_Crore", "Fraud_per_Million"])
    geo = requests.get("https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/india_states.geojson").json()

    fig = px.choropleth(
        state_summary,
        geojson=geo,
        locations="State",
        featureidkey="properties.ST_NM",
        color=metric,
        color_continuous_scale="Turbo",
        hover_data=["UPI_Volume", "UPI_Value_Crore", "Fraud_per_Million"]
    )
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# CONCENTRATION
# ==========================================================
elif page == "📊 Concentration":
    top10 = state_summary.sort_values("Share_%", ascending=False).head(10)
    st.metric("Top 5 States Share", f"{top10.head(5)['Share_%'].sum():.1f}%")

    fig = px.bar(top10, x="State", y="Share_%", title="UPI Volume Concentration")
    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# FORMALISATION
# ==========================================================
elif page == "💰 Formalisation":
    fig = px.scatter(
        state_summary,
        x="UPI_Volume",
        y="Avg_Value_per_Txn",
        size="UPI_Value_Crore",
        color="Fraud_per_Million",
        hover_name="State"
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# FRAUD RISK
# ==========================================================
elif page == "🚨 Fraud Risk":
    fig = px.scatter(
        state_summary,
        x="UPI_Volume",
        y="Fraud_per_Million",
        size="UPI_Value_Crore",
        hover_name="State"
    )
    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# 2047 OUTLOOK (FIXED)
# ==========================================================
elif page == "🔮 2047 Outlook":
    st.markdown("## 🔮 2047 Digital Payments Outlook")

    growth = st.slider("Annual Growth Rate (%)", 5, 20, 12)

    BASE_YEAR = 2024
    TARGET_YEAR = 2047
    YEARS = TARGET_YEAR - BASE_YEAR

    # Scale sample data to national magnitude (transparent assumption)
    SCALE_FACTOR = 1_000_000
    base_volume = state_summary["UPI_Volume"].sum() * SCALE_FACTOR

    years_list = list(range(BASE_YEAR, TARGET_YEAR + 1))
    projection = [base_volume * ((1 + growth / 100) ** (y - BASE_YEAR)) for y in years_list]

    df_forecast = pd.DataFrame({
        "Year": years_list,
        "Projected Transactions": projection
    })

    c1, c2, c3 = st.columns(3)
    c1.metric("Base Year (2024)", format_txns(base_volume))
    c2.metric("2047 Projection", format_txns(projection[-1]))
    c3.metric("Growth Multiple", f"{projection[-1]/base_volume:.1f}×")

    fig = px.line(
        df_forecast,
        x="Year",
        y="Projected Transactions",
        markers=True,
        title="Projected Growth of Digital Transactions (2024–2047)"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.success(
        "📈 **Interpretation:** At this growth rate, India’s digital payment ecosystem "
        "expands multiple-fold by 2047, requiring parallel investments in cybersecurity, "
        "infrastructure, and inclusion."
    )

# ==========================================================
# AI POLICY ASSISTANT
# ==========================================================
elif page == "🤖 AI Policy Assistant":
    q = st.text_input("Ask a policy question:")

    if q:
        q = q.lower()
        if "fraud" in q:
            st.success("Fraud increases during rapid adoption; policy must pair growth with cyber literacy.")
        elif "2047" in q:
            st.success("Viksit Bharat 2047 requires inclusive digital infrastructure across all states.")
        elif "concentration" in q:
            st.success("High concentration shows uneven regional digital readiness.")
        else:
            st.info("Ask about fraud, growth, inclusion, or long-term digital policy.")

# ----------------------------------------------------------
# FOOTER
# ----------------------------------------------------------
st.markdown("---")
st.caption("Digital Transactions in India & Viksit Bharat 2047 | Final Multi-Page App")