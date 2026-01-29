import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="Valuation-Pro Engine", layout="wide")

# 2. The "Bulletproof" Animated Gradient CSS
st.markdown("""
    <style>
    /* تحريك الخلفية */
    @keyframes move {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* استهداف كل الحاويات الممكنة لجبر الألوان على الظهور */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: linear-gradient(-45deg, #020617, #1e1b4b, #312e81, #0f172a) !important;
        background-size: 400% 400% !important;
        animation: move 15s ease infinite !important;
    }

    /* جعل القائمة الجانبية شفافة تماماً لرؤية الحركة خلفها */
    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background: rgba(0, 0, 0, 0) !important;
    }

    /* تنسيق كروت الـ Metrics كأنها زجاج طافي */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px);
        padding: 20px !important;
        border-radius: 15px !important;
    }

    /* إجبار النصوص على اللون الأبيض النقي */
    h1, h2, h3, h4, h5, h6, p, label, .stMetric label, .stMetric div {
        color: #ffffff !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #38bdf8 !important; /* أزرق سماوي مضيء للأرقام */
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Rest of the Logic (Keep it as it is)
# ... (باقي كود الحسابات والجداول والرسومات)

# 3. Header Section
st.title("⚖️ Valuation-Pro | Enterprise Insight Engine")
st.caption("Strategic Valuation Tool | Developed by Maher Al-Momani")
st.markdown("---")

# 4. Sidebar Inputs
st.sidebar.header("📊 Model Assumptions")
current_fcf = st.sidebar.number_input("Current Free Cash Flow ($)", value=1000000)
growth_rate = st.sidebar.slider("Forecast Growth Rate (%)", 0, 50, 10) / 100
wacc = st.sidebar.slider("WACC / Discount Rate (%)", 5, 20, 12) / 100
terminal_growth = st.sidebar.slider("Terminal Growth Rate (%)", 1, 5, 2) / 100

# 5. Financial Logic
forecast_years = [1, 2, 3, 4, 5]
future_cash_flows = [current_fcf * ((1 + growth_rate) ** y) for y in forecast_years]
present_values = [future_cash_flows[i] / ((1 + wacc) ** (i+1)) for i in range(len(forecast_years))]

last_fcf = future_cash_flows[-1]
terminal_value = (last_fcf * (1 + terminal_growth)) / (wacc - terminal_growth)
pv_terminal_value = terminal_value / ((1 + wacc) ** 5)
enterprise_value = sum(present_values) + pv_terminal_value

# 6. Metrics Display (Glowing metrics)
m1, m2, m3 = st.columns(3)
m1.metric("Enterprise Value", f"${enterprise_value:,.0f}")
m2.metric("Terminal Value", f"${terminal_value:,.0f}")
m3.metric("PV of Terminal Value", f"${pv_terminal_value:,.0f}")

st.markdown("---")

# 7. Visuals (Charts updated for Dark Theme)
left, right = st.columns([1, 1.5])

with left:
    st.write("### 📅 Projection Table")
    df = pd.DataFrame({
        "Year": [f"Year {y}" for y in forecast_years],
        "FCF ($)": future_cash_flows,
        "PV ($)": present_values
    })
    st.dataframe(df.style.format({"FCF ($)": "{:,.0f}", "PV ($)": "{:,.0f}"}), use_container_width=True)

with right:
    st.write("### 📊 Valuation Breakdown")
    labels = [f"Y{y} PV" for y in forecast_years] + ["PV of TV"]
    values = present_values + [pv_terminal_value]
    
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative"] * 6 + ["total"],
        x=labels + ["Total EV"],
        text=[f"${v/1e6:.1f}M" for v in values] + [f"${enterprise_value/1e6:.1f}M"],
        y=values + [enterprise_value],
        increasing={"marker": {"color": "#38bdf8"}}, # Glowing Blue
        totals={"marker": {"color": "#6366f1"}}  # Indigo
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(t=10, b=10, l=10, r=10)
    )
    st.plotly_chart(fig, use_container_width=True)

# 8. Sensitivity Analysis
st.markdown("---")
st.write("### 🔥 Sensitivity Analysis: WACC vs Growth")

wacc_range = [wacc + i for i in [-0.02, -0.01, 0, 0.01, 0.02]]
growth_range = [growth_rate + i for i in [0.02, 0.01, 0, -0.01, -0.02]]

sens_matrix = []
for g in growth_range:
    row = []
    for r in wacc_range:
        f_cf = [current_fcf * ((1 + g) ** y) for y in [1,2,3,4,5]]
        p_vs = [f_cf[i-1] / ((1 + r) ** i) for i in [1,2,3,4,5]]
        tv = (f_cf[-1] * (1 + terminal_growth)) / (r - terminal_growth)
        ev = sum(p_vs) + (tv / ((1 + r) ** 5))
        row.append(ev)
    sens_matrix.append(row)

fig_heat = px.imshow(
    sens_matrix,
    x=[f"{r*100:.1f}%" for r in wacc_range],
    y=[f"{g*100:.1f}%" for g in growth_range],
    color_continuous_scale="RdYlGn",
    text_auto=".2s"
)
fig_heat.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")
st.write("### 📖 Valuation Methodology")
st.latex(r"PV = \sum_{t=1}^{n} \frac{CF_t}{(1+r)^t}")
st.caption("The engine calculates intrinsic value by discounting future free cash flows back to the present using the Weighted Average Cost of Capital (WACC).")