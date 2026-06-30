import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Unified Diode Curve Tracer",
    page_icon="🔌",
    layout="wide"
)

# --- LEARNING ANALYTICS LOGGER ---
LOG_FILE = "student_analytics_log.csv"

def log_user_action(student_id, action_type, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_data = pd.DataFrame([{
        "Timestamp": timestamp,
        "Student_ID": student_id,
        "Action_Type": action_type,
        "Details": str(details)
    }])
    if not os.path.isfile(LOG_FILE):
        log_data.to_csv(LOG_FILE, index=False)
    else:
        log_data.to_csv(LOG_FILE, mode='a', header=False, index=False)

# --- SESSION STATE FOR DATA STORAGE ---
if 'student_id' not in st.session_state:
    st.session_state['student_id'] = "Guest_Student"
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Unified Data Tables holding both Forward and Reverse observations together
if 'si_data' not in st.session_state:
    st.session_state['si_data'] = pd.DataFrame(columns=["Voltage (V)", "Current Input", "Unit"])
if 'ge_data' not in st.session_state:
    st.session_state['ge_data'] = pd.DataFrame(columns=["Voltage (V)", "Current Input", "Unit"])

# --- HEADER ---
st.title("🔌 Practical: Unified Forward & Reverse Bias Characteristics of Si and Ge Diodes")
st.subheader("Department of Physics/Electronics — Solid State Electronics Laboratory")
st.markdown("---")

# --- LOGIN GATEWAY ---
if not st.session_state['authenticated']:
    st.info("👋 Welcome! Please initialize the laboratory bench by entering your Matriculation Number.")
    matric_no = st.text_input("Student Matriculation Number:")
    if st.button("Initialize Lab Bench"):
        if matric_no.strip() != "":
            st.session_state['student_id'] = matric_no.strip()
            st.session_state['authenticated'] = True
            log_user_action(st.session_state['student_id'], "Session_Start", "Initialized Unified Graph Lab Bench.")
            st.rerun()
        else:
            st.warning("Identification required to track experimental logs.")
    st.stop()

# --- SIDEBAR: BENCH CONFIGURATION & ENTRY LOG ---
st.sidebar.header("🎛️ Experimental Bench Controls")
material = st.sidebar.radio("Select Semiconductor Diode:", ["Silicon (Si)", "Germanium (Ge)"])
bias_mode = st.sidebar.radio("Select Input Bias Region:", ["Forward Bias Region", "Reverse Bias Region"])

st.sidebar.markdown("---")
st.sidebar.subheader("📥 Data Spreadsheet Logger")

# Configuration matching the requested unit and precision rules
if bias_mode == "Forward Bias Region":
    st.sidebar.markdown("**Forward Parameters:** Enter positive values.")
    v_in = st.sidebar.number_input("Voltage, V (Volts):", min_value=0.00, max_value=5.00, value=0.00, step=0.05, format="%.2f", key="v_fwd")
    c_unit = st.sidebar.selectbox("Current Unit:", ["milliampere (mA)", "microampere (µA)"], key="u_fwd")
    i_raw = st.sidebar.number_input("Measured Current Value:", min_value=0.00, max_value=500.00, value=0.00, step=0.10, format="%.2f", key="i_fwd")
else:
    st.sidebar.markdown("**Reverse Parameters:** Enter negative values for graph quadrant alignment.")
    v_in = st.sidebar.number_input("Voltage, V (Negative Volts):", min_value=-100.00, max_value=0.00, value=0.00, step=1.00, format="%.2f", key="v_rev")
    c_unit = st.sidebar.selectbox("Current Unit:", ["microampere (µA)", "milliampere (mA)"], key="u_rev")
    i_raw = st.sidebar.number_input("Measured Leakage Current (Negative Value):", min_value=-500.00, max_value=0.00, value=0.00, step=0.10, format="%.2f", key="i_rev")

if st.sidebar.button("Log Matrix Row Entry"):
    new_row = pd.DataFrame([{"Voltage (V)": round(v_in, 2), "Current Input": round(i_raw, 2), "Unit": c_unit}])
    
    if material == "Silicon (Si)":
        st.session_state['si_data'] = pd.concat([st.session_state['si_data'], new_row], ignore_index=True).drop_duplicates(subset=["Voltage (V)"]).sort_values(by="Voltage (V)")
    else:
        st.session_state['ge_data'] = pd.concat([st.session_state['ge_data'], new_row], ignore_index=True).drop_duplicates(subset=["Voltage (V)"]).sort_values(by="Voltage (V)")
        
    log_user_action(st.session_state['student_id'], "Unified_Row_Added", f"{material} - {bias_mode}: V={v_in}, I={i_raw} {c_unit}")
    st.toast("Row recorded with 2-decimal precision!", icon="📝")

if st.sidebar.button("🚨 Clear Current Material Dataset"):
    if material == "Silicon (Si)":
        st.session_state['si_data'] = pd.DataFrame(columns=["Voltage (V)", "Current Input", "Unit"])
    else:
        st.session_state['ge_data'] = pd.DataFrame(columns=["Voltage (V)", "Current Input", "Unit"])
    st.sidebar.warning(f"Cleared all entries for {material}")
    st.rerun()

# --- CONVERSION ENGINE FOR UNIFIED mA GRAPHING ---
def process_plotting_dataframe(df):
    if df.empty:
        return df.copy()
    processed = df.copy()
    graph_currents = []
    
    for _, row in processed.iterrows():
        val = row["Current Input"]
        unit = row["Unit"]
        # If input is in microamperes, scale to milliamperes down to two decimal spots
        if "microampere" in unit or "µA" in unit:
            graph_currents.append(round(val / 1000.0, 4))
        else:
            graph_currents.append(round(val, 2))
            
    processed["Current (mA)"] = graph_currents
    return processed

# Get active table metrics
active_df = st.session_state['si_data'] if material == "Silicon (Si)" else st.session_state['ge_data']
plot_df = process_plotting_dataframe(active_df)

# --- MAIN SCREEN INTERACTIVE WORKBENCH ---
col_graph, col_table = st.columns([2, 1])

with col_table:
    st.subheader("📋 Logged Data Registry")
    st.markdown(f"**Material:** `{material}` (All bias data rows)")
    st.dataframe(active_df, use_container_width=True, hide_index=True)
    st.caption("ℹ️ *Note: Microamperes (µA) are dynamically converted to fractions of Milliamperes (mA) directly on the unified tracer window.*")

with col_graph:
    st.subheader(f"📊 Continuous Curve Tracer Plot: {material}")
    st.markdown("*Shows both Forward and Reverse Bias data points scaled on the same coordinate grid.*")
    
    fig = go.Figure()
    
    if not plot_df.empty:
        # Separate forward and reverse points to give distinct color profiles on the single layout
        fwd_pts = plot_df[plot_df["Voltage (V)"] >= 0]
        rev_pts = plot_df[plot_df["Voltage (V)"] < 0]
        
        # 1. Forward Trace Plotting
        if not fwd_pts.empty:
            fig.add_trace(go.Scatter(
                x=fwd_pts["Voltage (V)"], y=fwd_pts["Current (mA)"],
                mode='markers+lines', name="Forward Bias (mA)",
                marker=dict(color='#00CC96', size=9),
                line=dict(color='#00CC96', width=2)
            ))
        # 2. Reverse Trace Plotting on the same graph axis
        if not rev_pts.empty:
            fig.add_trace(go.Scatter(
                x=rev_pts["Voltage (V)"], y=rev_pts["Current (mA)"],
                mode='markers+lines', name="Reverse Bias (Scaled to mA)",
                marker=dict(color='#FF4B4B', size=9, symbol='square'),
                line=dict(color='#FF4B4B', width=2, dash='dot')
            ))
            
        x_min = min(plot_df["Voltage (V)"].min() - 2, -5)
        x_max = max(plot_df["Voltage (V)"].max() + 0.5, 1.5)
        y_min = min(plot_df["Current (mA)"].min() - 1, -2)
        y_max = max(plot_df["Current (mA)"].max() + 5, 15)
    else:
        x_min, x_max, y_min, y_max = -10, 2, -5, 20
        st.info("💡 The graph is currently empty. Input values into the sidebar data logger to map characteristics plots.")

    fig.layout = go.Layout(
        xaxis=dict(title="Applied Bias Voltage (Volts, V)", range=[x_min, x_max], zeroline=True, zerolinecolor="white", gridcolor="rgba(128,128,128,0.2)"),
        yaxis=dict(title="Diode Current (Milliamperes, mA)", range=[y_min, y_max], zeroline=True, zerolinecolor="white", gridcolor="rgba(128,128,128,0.2)"),
        template="plotly_dark",
        height=450,
        margin=dict(l=25, r=25, t=10, b=25)
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- POST-LAB EVALUATION VIVA VOCE (5 QUESTIONS) ---
st.header("📝 Post-Laboratory Evaluation & Viva-Voce")
st.markdown("Answer these 5 critical diagnostic questions to submit your analysis of your recorded curves:")

with st.form("diode_viva_voce"):
    q1 = st.radio(
        "1. Based on your recorded Forward Bias data table, what is the approximate threshold (knee voltage) where Silicon starts conducting significantly?",
        ["0.1 V to 0.2 V", "0.3 V to 0.4 V", "0.6 V to 0.7 V"]
    )
    
    q2 = st.radio(
        "2. When your recorded voltage moves further into Reverse Bias, why does the leakage current remain exceptionally tiny before breakdown?",
        ["Because the depletion region widens, creating an immense barrier resistance that blocks majority carriers.",
         "Because the forward bias resistance cancels out all current vectors completely.",
         "Because covalent bonds break down and lock all electrons back into stable atomic orbits."]
    )
    
    q3 = st.radio(
        "3. What forms the tiny reverse leakage current measured in microamperes (µA) during your practical?",
        ["The flow of majority carriers trying to force their way across the barrier.",
         "The drift of thermally generated minority charge carriers sweeping across the junction.",
         "Static friction electricity generated along the copper wiring connections."]
    )
    
    q4 = st.radio(
        "4. Comparing your Forward Bias curves for both materials, which diode allows forward current (mA) to scale up at a lower threshold voltage?",
        ["Silicon (Si), because of its wider structural atomic bandgap.",
         "Germanium (Ge), due to its smaller forbidden bandgap energy barrier (~0.3V threshold).",
         "Both show identical conduction thresholds because material matrix attributes don't affect forward voltage."]
    )
    
    q5 = st.radio(
        "5. What structural state occurs inside the p-n junction if you sweep the reverse voltage drastically past its Peak Inverse Voltage (PIV) specification?",
        ["The internal electric field triggers carrier multiplication (avalanche breakdown), causing a sharp, massive rise in reverse current.",
         "The depletion layer completely evaporates and forces the system into an open circuit state.",
         "The diode flips polarity automatically and switches back into a forward conducting state."]
    )
    
    submitted = st.form_submit_button("Submit Lab Evaluation Answers")
    
    if submitted:
        score = 0
        if q1 == "0.6 V to 0.7 V": score += 20
        if q2 == "Because the depletion region widens, creating an immense barrier resistance that blocks majority carriers.": score += 20
        if q3 == "The drift of thermally generated minority charge carriers sweeping across the junction.": score += 20
        if q4 == "Germanium, due to its smaller forbidden bandgap energy barrier (~0.3V threshold).": score += 20
        if q5 == "The internal electric field triggers carrier multiplication (avalanche breakdown), causing a sharp, massive rise in reverse current.": score += 20
        
        st.subheader(f"🎯 Evaluation Result: {score}/100")
        if score == 100:
            st.success("Excellent! Your technical deductions match your practical curve tracings perfectly.")
        else:
            st.warning("Some answers are incorrect. Review your data points and threshold knees to re-verify your conclusions.")
            
        log_user_action(st.session_state['student_id'], "Quiz_Submission", f"Score: {score}/100")

st.markdown("---")
if st.button("Log Out / Reset Lab Bench"):
    st.session_state['authenticated'] = False
    st.rerun()