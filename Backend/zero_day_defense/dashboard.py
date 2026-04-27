import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from zero_day_defense.pipeline import run_pipeline
from zero_day_defense.settings import load_config

# Page Config
st.set_page_config(
    page_title="ZDD | Zero-Day Defense Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background: radial-gradient(circle at top left, #0f172a, #020617);
        color: #f8fafc;
    }

    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        color: #3b82f6;
    }

    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        border: none;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }

    .threat-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(51, 65, 85, 0.5);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }

    .threat-tag {
        background: rgba(239, 44, 44, 0.2);
        color: #f87171;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .normal-tag {
        background: rgba(34, 197, 94, 0.2);
        color: #4ade80;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# App Data Loading
def load_data():
    cfg = load_config(config_path=None, dataset_root="dataset")
    out_path = Path("artifacts/run_output.json")
    if out_path.exists():
        data = json.loads(out_path.read_text())
        return data.get("decisions", [])
    return []

def trigger_run():
    cfg = load_config(config_path=None, dataset_root="dataset")
    with st.spinner("Analyzing network traffic with Agentic AI..."):
        run_pipeline(cfg, dry_run=True, max_events=50)
    st.balloons()
    st.success("Analysis Complete!")

# Header
col1, col2 = st.columns([3, 1])
# We add some spacing for better layout
st.write("") 

with col1:
    st.title("🛡️ Zero-Day Defense System")
    st.markdown("_Multi-Layered Agentic AI Network Protection_")
with col2:
    if st.button("🚀 Run Live Analysis"):
        trigger_run()

decisions = load_data()

if not decisions:
    st.warning("No data found. Please run the live analysis to generate results.")
else:
    df = pd.DataFrame(decisions)
    
    # Summary Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Events", len(df))
    with m2:
        threats = df[df['threat'] == True]
        st.metric("Threats Detected", len(threats), delta=f"{len(threats)/len(df)*100:.1f}%" if len(df)>0 else "0%", delta_color="inverse")
    with m3:
        avg_conf = df['confidence'].mean()
        st.metric("Avg. Confidence", f"{avg_conf:.2%}")
    with m4:
        st.metric("System Health", "Optimal", delta="Active")

    st.divider()

    # Visualizations
    v1, v2 = st.columns([2, 1])
    
    with v1:
        st.subheader("⚡ Score Distribution Across Layers")
        # Flatten scores for plotting
        score_data = []
        for i, row in df.iterrows():
            for layer, score in row['scores'].items():
                score_data.append({"Event": i, "Layer": layer, "Score": score})
        
        score_df = pd.DataFrame(score_data)
        fig = px.line(score_df, x="Event", y="Score", color="Layer", 
                     template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(gridcolor='#334155'),
            xaxis=dict(gridcolor='#334155')
        )
        st.plotly_chart(fig, use_container_width=True)

    with v2:
        st.subheader("🎯 Threat Probability")
        hist_fig = px.histogram(df, x="confidence", nbins=10, 
                               template="plotly_dark", color_discrete_sequence=['#3b82f6'])
        hist_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(hist_fig, use_container_width=True)

    # Detailed Table
    st.subheader("🔍 Real-Time Event Audit")
    
    # Formatting for display
    display_df = df.copy()
    display_df['Status'] = display_df['threat'].apply(lambda x: "🚨 BLOCK" if x else "✅ ALLOW")
    display_df['Perception'] = display_df['scores'].apply(lambda x: f"{x['perception']:.3f}")
    display_df['Forecasting'] = display_df['scores'].apply(lambda x: f"{x['forecasting']:.3f}")
    display_df['LSTM'] = display_df['scores'].apply(lambda x: f"{x['lstm']:.3f}")
    
    cols_to_show = ['Status', 'src_ip', 'dst_ip', 'dst_port', 'confidence', 'Perception', 'Forecasting', 'LSTM', 'rationale']
    
    st.dataframe(
        display_df[cols_to_show],
        column_config={
            "confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=1, format="%.2f"),
            "Status": st.column_config.TextColumn("Verdict"),
            "rationale": st.column_config.TextColumn("Agent Rationale", width="large")
        },
        use_container_width=True,
        hide_index=True
    )

    # Mitigation Details
    if not threats.empty:
        with st.expander("🛡️ View Suggested Mitigation Actions"):
            for _, t in threats.iterrows():
                for action in t['actions_executed']:
                    st.info(f"**Target IP:** {action['ip']} | **Action:** Block Traffic | **Command:** `{action['command']}`")

st.markdown("---")
st.caption("Zero-Day Defense Prototype | Built with Agentic AI & Multi-Layer Anomaly Detection")
