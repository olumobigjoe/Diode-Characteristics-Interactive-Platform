import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Automated Diode Tracer Lab Bench",
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

# --- SESSION STATE INITIALIZATION ---
if 'student_id' not in st.session_state:
    st.session_state['student_id'] = "Guest_Student"
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'quiz_submitted' not in st.session_state:
    st.session_state['quiz_submitted'] = False
if 'saved_score' not in st.session_state:
    st.session_state['saved_score'] = 0

# Base DataFrame definition initialized in session memory
if 'si_data' not in st.session_state:
    st.session_state['si_data'] = pd.DataFrame(columns=["Voltage (V)", "Current (mA)"])
if 'ge_data' not in st.session_state:
    st.session_state['ge_data'] = pd.DataFrame(columns=["Voltage (V)", "Current (mA)"])

# --- HEADER ---
st.title("🔌 Practical: Automated Forward & Reverse Bias Characteristics of Si and Ge Diodes")
st.subheader("Department of Physics/Electronics — Solid State Electronics Laboratory")
st.markdown("---")

# --- LOGIN GATEWAY ---
if not st.session_state['authenticated']:
    st.info("👋 Welcome! Please initialize the laboratory bench by entering your Matriculation Number.")
    matric_no = st.text_input("Student Matriculation Number:")
    if st.button("Initialize Lab Bench"):
        if matric_no.strip() != "":
            st.session_state['si_data'] = pd.DataFrame(columns=["Voltage (V)", "Current (mA)"])
            st.session_state['ge_data'] = pd.DataFrame(columns=["Voltage (V)", "Current (mA)"])
            st.session_state['student_id'] = matric_no.strip()
            st.session_state['authenticated'] = True
            st.session_state['quiz_submitted'] = False 
            st.session_state['saved_score'] = 0
            
            log_user_action(st.session_state['student_id'], "Session_Start", "Initialized Fresh Isolated Diode Lab Bench.")
            st.rerun()
        else:
            st.warning("Identification required to track experimental logs.")
    st.stop()

# --- SIDEBAR: BENCH CONFIGURATION & AUTOMATED DATA LOGGER ---
st.sidebar.header("🎛️ Virtual Instrument Controls")
material = st.sidebar.radio("Select Semiconductor Diode:", ["Silicon (Si)", "Germanium (Ge)"])
bias_mode = st.sidebar.radio("Select Input Bias Region:", ["Forward Bias Region", "Reverse Bias Region"])

st.sidebar.markdown("---")
st.sidebar.subheader("📥 Automated Data Logger")
st.sidebar.markdown("*Vary the applied voltage source ($0.00\\text{ V}$ to $20.00\\text{ V}$ in steps of $0.10\\text{ V}$). Current output updates automatically in mA.*")

# Adjusted configuration limits: Voltage sweeps from 0 to 20 Volts in steps of 0.1
if bias_mode == "Forward Bias Region":
    v_magnitude = st.sidebar.number_input("Voltage Magnitude (Volts):", min_value=0.00, max_value=20.00, value=0.00, step=0.10, format="%.2f", key="v_fwd")
    v_in = v_magnitude
else:
    v_magnitude = st.sidebar.number_input("Voltage Magnitude (Volts):", min_value=0.00, max_value=20.00, value=0.00, step=0.10, format="%.2f", key="v_rev")
    v_in = -v_magnitude  # Converts input magnitude to a negative reverse voltage parameter internally

# --- MATHEMATICAL SEMICONDUCTOR PHYSICS ENGINE ---
vt = 0.0259  # Thermal voltage at room temperature (~300K)

if material == "Silicon (Si)":
    is_fwd = 1e-12       # Reverse Saturation Current for Silicon (1 pA)
    eta = 1.3            # Ideality factor
    v_breakdown = -12.0  # Avalanche Breakdown Voltage
else: # Germanium (Ge)
    is_fwd = 1e-6        # Reverse Saturation Current for Germanium (1 µA)
    eta = 1.0            # Ideality factor
    v_breakdown = -6.0   # Avalanche Breakdown Voltage

# Calculate the precise current value response
if v_in >= 0:
    # Forward Bias Equation: Shockley Model (Converted directly to mA)
    i_ampere = is_fwd * (np.exp(v_in / (eta * vt)) - 1)
    i_generated_ma = i_ampere * 1000.0
else:
    # Reverse Bias Equation with Breakdown Mask modeling
    if v_in <= v_breakdown:
        multiplier = 1.0 / (1.0 - (np.abs(v_in / v_breakdown) ** 4) + 1e-6)
        multiplier = min(multiplier, 2000.0) 
        i_ampere = -is_fwd * multiplier
    else:
        i_ampere = -is_fwd * (1.0 - np.exp(v_in / vt))
        
    i_generated_ma = i_ampere * 1000.0  # Converted to mA for uniform structure alignment

# Enforce clean 2-decimal place restriction mapping
v_in = round(v_in, 2)
i_generated_ma = round(i_generated_ma, 2)

st.sidebar.markdown(f"### Generated Output Current:")
st.sidebar.info(f"**⚡ Current $I$ = {i_generated_ma:.2f} mA**")

if st.sidebar.button("Log Generated Metrics Row"):
    new_row = pd.DataFrame([{"Voltage (V)": v_in, "Current (mA)": i_generated_ma}])
    
    if material == "Silicon (Si)":
        st.session_state['si_data'] = pd.concat([st.session_state['si_data'], new_row], ignore_index=True).drop_duplicates(subset=["Voltage (V)"]).sort_values(by="Voltage (V)")
    else:
        st.session_state['ge_data'] = pd.concat([st.session_state['ge_data'], new_row], ignore_index=True).drop_duplicates(subset=["Voltage (V)"]).sort_values(by="Voltage (V)")
        
    log_user_action(st.session_state['student_id'], "Unified_Auto_Row_Added", f"{material} - {bias_mode}: V={v_in}, I={i_generated_ma} mA")
    st.toast("Calculated data row recorded!", icon="⚙️")

if st.sidebar.button("🚨 Clear Current Material Dataset"):
    if material == "Silicon (Si)":
        st.session_state['si_data'] = pd.DataFrame(columns=["Voltage (V)", "Current (mA)"])
    else:
        st.session_state['ge_data'] = pd.DataFrame(columns=["Voltage (V)", "Current (mA)"])
    st.sidebar.warning(f"Cleared all entries for {material}")
    st.rerun()

# Fetch active table parameters
active_df = st.session_state['si_data'] if material == "Silicon (Si)" else st.session_state['ge_data']

# --- MAIN SCREEN WORKSPACE ---
col_graph, col_table = st.columns([2, 1])

with col_table:
    st.subheader(f"📋 Experimental Spreadsheet Log [{st.session_state['student_id']}]")
    st.markdown(f"**Material:** `{material}`")
    
    # Format columns explicitly to display exactly 2 decimal places in the table visual layout
    formatted_df = active_df.copy()
    if not formatted_df.empty:
        formatted_df["Voltage (V)"] = formatted_df["Voltage (V)"].map("{:.2f}".format)
        formatted_df["Current (mA)"] = formatted_df["Current (mA)"].map("{:.2f}".format)
        
    st.dataframe(formatted_df, use_container_width=True, hide_index=True)
    st.caption("ℹ️ *Note: All logging metrics are automatically standardized to Milliamperes (mA) down to 2 decimal places.*")

with col_graph:
    st.subheader
