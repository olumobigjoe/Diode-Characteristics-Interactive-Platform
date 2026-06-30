import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="P-N Junction Characteristics Curve Tracer",
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

# --- SESSION STATE FOR LABORATORY DATA STORAGE ---
if 'student_id' not in st.session_state:
    st.session_state['student_id'] = "Guest_Student"
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Initialize custom data tables for the session if they don't exist
if 'si_forward' not in st.session_state:
    st.session_state['si_forward'] = pd.DataFrame(columns=["Voltage (V)", "Current (mA)"])
if 'si_reverse' not in st.session_state:
    st.session_state['si_reverse'] = pd.DataFrame(columns=["Voltage (V)", "Current (µA)"])
if 'ge_forward' not in st.session_state:
    st.session_state['ge_forward'] = pd.DataFrame(columns=["Voltage (V)", "Current (mA)"])
if 'ge_reverse' not in st.session_state:
    st.session_state['ge_reverse'] = pd.DataFrame(columns=["Voltage (V)", "Current (µA)"])

# --- HEADER ---
st.title("🔌 Practical: Recording Forward & Reverse Bias Characteristics of Si and Ge Diodes")
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
            log_user_action(st.session_state['student_id'], "Session_Start", "Initialized Custom Table Lab Bench.")
            st.rerun()
        else:
            st.warning("Identification required to track experimental logs.")
    st.stop()

# --- SIDEBAR CONFIGURATION AND MANUAL DATA ENTRY ---
st.sidebar.header("🎛️ Experimental Bench Controls")
material = st.sidebar.radio("Select Semiconductor Diode:", ["Silicon (Si)", "Germanium (Ge)"])
bias_mode = st.sidebar.radio("Select Bias Mode:", ["Forward Bias", "Reverse Bias"])

st.sidebar.markdown("---")
st.sidebar.subheader("📥 Data Logger Panel")
st.sidebar.markdown("*Take your manual physical readings and record them step-by-step into the active table below:*")

# Dynamic inputs based on selections
if bias_mode == "Forward Bias":
    v_in = st.sidebar.number_input("Input Voltage (Volts, V):", min_value=0.0, max_value=2.0, value=0.0, step=0.1, key="v_fwd")
    i_in = st.sidebar.number_input("Input Forward Current (milliamperes, mA):", min_value=0.0, max_value=150.0, value=0.0, step=1.0, key="i_fwd")
else:
    v_in = st.sidebar.number_input("Input Reverse Voltage (Negative Volts, V):", min_value=-50.0, max_value=0.0, value=0.0, step=0.5, key="v_rev")
    i_in = st.sidebar.number_input("Input Reverse Leakage Current (microamperes, µA):", min_value=-200.0, max_value=0.0, value=0.0, step=1.0, key="i_rev")

if st.sidebar.button("Add Reading to Spreadsheet Row"):
    new_row = pd.DataFrame([{"Voltage (V)": v_in, "Current (mA)" if bias_mode=="Forward Bias" else "Current (µA)": i_in}])
    
    # Target state table dynamically
    if material == "Silicon (Si)":
        if bias_mode == "Forward Bias":
            st.session_state['si_forward'] = pd.concat([st.session_state['si_forward'], new_row], ignore_index=True).drop_duplicates().sort_values(by="Voltage (V)")
        else:
            st.session_state['si_reverse'] = pd.concat([st.session_state['si_reverse'], new_row], ignore_index=True).drop_duplicates().sort_values(by="Voltage (V)", ascending=False)
    else: # Germanium
        if bias_mode == "Forward Bias":
            st.session_state['ge_forward'] = pd.concat([st.session_state['ge_forward'], new_row], ignore_index=True).drop_duplicates().sort_values(by="Voltage (V)")
        else:
            st.session_state['ge_reverse'] = pd.concat([st.session_state['ge_reverse'], new_row], ignore_index=True).drop_duplicates().sort_values(by="Voltage (V)", ascending=False)
            
    log_user_action(st.session_state['student_id'], "Row_Added", f"{material} - {bias_mode}: V={v_in}, I={i_in}")
    st.toast("Row recorded successfully!", icon="📝")

if st.sidebar.button("🚨 Clear Active Material Data"):
    if material == "Silicon (Si)":
        st.session_state['si_forward'] = pd.DataFrame(columns=["Voltage (V)", "Current (mA)"])
        st.session_state['si_reverse'] = pd.DataFrame(columns=["Voltage (V)", "Current (µA)"])
    else:
        st.session_state['ge_forward'] = pd.DataFrame(columns=["Voltage (V)", "Current (mA)"])
        st.session_state['ge_reverse'] = pd.DataFrame(columns=["Voltage (V)", "Current (µA)"])
    st.sidebar.warning(f"Cleared all entries for {material}")
    st.rerun()

# --- FETCH RELEVANT LOGGED DATA ---
if material == "Silicon (Si)":
    fwd_df = st.session_state['si_forward']
    rev_df = st.session_state['si_reverse']
else:
    fwd_df = st.session_state['ge_forward']
    rev_df = st.session_state['ge_reverse']

# --- MAIN SCREEN LAYOUT ---
col_charts, col_tables = st.columns([2, 1])

with col_tables:
    st.subheader("📋 Active Laboratory Table")
    st.markdown(f"**Current View:** `{material}` - `{bias_mode}`")
    
    if bias_mode == "Forward Bias":
        st.dataframe(fwd_df, use_container_width=True, hide_index=True)
    else:
        st.dataframe(rev_df, use_container_width=True, hide_index=True)
        st.caption("ℹ️ *Note: For graphing consistency, µA inputs are auto-converted to mA on the curve tracker.*")

with col_charts:
    st.subheader(f"📊 Live Curve Tracer Plot: {material}")
    
    fig = go.Figure()
    
    if bias_mode == "Forward Bias" and not fwd_df.empty:
        # Plot student forward characteristics
        fig.add_trace(go.Scatter(
            x=fwd_df["Voltage (V)"], 
            y=fwd_df["Current (mA)"], 
            mode='markers+lines', 
            name="Your Experimental Data (mA)",
            marker=dict(color='#00CC96', size=10, symbol='circle'),
            line=dict(color='#00CC96', width=2, dash='dash')
        ))
        x_range = [-0.1, max(fwd_df["Voltage (V)"].max(), 1.0) + 0.2]
        y_range = [-5, max(fwd_df["Current (mA)"].max(), 20.0) + 10]
        y_label = "Forward Current (mA)"
        
    elif bias_mode == "Reverse Bias" and not rev_df.empty:
        # Auto-convert µA column to mA values dynamically for plotting on the unified mA tracker axis
        current_in_ma = rev_df["Current (µA)"] / 1000.0
        
        fig.add_trace(go.Scatter(
            x=rev_df["Voltage (V)"], 
            y=current_in_ma, 
            mode='markers+lines', 
            name="Your Experimental Data (Converted to mA)",
            marker=dict(color='#FF4B4B', size=10, symbol='square'),
            line=dict(color='#FF4B4B', width=2, dash='dash')
        ))
        x_range = [min(rev_df["Voltage (V)"].min(), -10.0) - 2, 0.5]
        y_range = [min(current_in_ma.min(), -0.5) - 0.2, 0.2]
        y_label = "Reverse Leakage Current (mA)"
        
    else:
        # Fallback view placeholder if no entries are active
        x_range, y_range, y_label = [-1, 1], [-1, 1], "Current (mA)"
        st.info("💡 Laboratory notice: Spreadsheet is empty. Use the input fields on the left sidebar control panel to log your experimental dataset and view the plot tracing live.")

    fig.layout = go.Layout(
        xaxis=dict(title="Applied Bias Voltage (Volts, V)", range=x_range, zeroline=True, zerolinecolor="gray"),
        yaxis=dict(title=y_label, range=y_range, zeroline=True, zerolinecolor="gray"),
        template="plotly_dark",
        height=450,
        margin=dict(l=20, r=20, t=20, b=20)
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