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
    st.session_state['si_data'] = pd.DataFrame(columns=["Voltage (V)", "Generated Current", "Unit"])
if 'ge_data' not in st.session_state:
    st.session_state['ge_data'] = pd.DataFrame(columns=["Voltage (V)", "Generated Current", "Unit"])

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
            # FRESH WORKING SLATE ASSIGNMENT: Wipe previous student entries on successful login
            st.session_state['si_data'] = pd.DataFrame(columns=["Voltage (V)", "Generated Current", "Unit"])
            st.session_state['ge_data'] = pd.DataFrame(columns=["Voltage (V)", "Generated Current", "Unit"])
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
st.sidebar.markdown("*Input your applied voltage parameter. The physics simulation engine will automatically generate the corresponding current response.*")

# Step 1: Handle student input parameters
if bias_mode == "Forward Bias Region":
    v_in = st.sidebar.number_input("Voltage, V (Positive Volts):", min_value=0.00, max_value=2.00, value=0.00, step=0.05, format="%.2f", key="v_fwd")
    c_unit = "milliampere (mA)"
else:
    v_in = st.sidebar.number_input("Voltage, V (Negative Volts):", min_value=-20.00, max_value=0.00, value=0.00, step=0.50, format="%.2f", key="v_rev")
    c_unit = "microampere (µA)"

# --- MATHEMATICAL SEMICONDUCTOR PHYSICS ENGINE ---
# Fundamental Constants
vt = 0.0259  # Thermal voltage at room temperature (~300K)

if material == "Silicon (Si)":
    is_fwd = 1e-12       # Reverse Saturation Current for Silicon (1 pA)
    eta = 1.3            # Ideality factor
    v_breakdown = -12.0  # Avalanche Breakdown Voltage
else: # Germanium (Ge)
    is_fwd = 1e-6        # Reverse Saturation Current for Germanium (1 µA)
    eta = 1.0            # Ideality factor
    v_breakdown = -6.0   # Avalanche Breakdown Voltage

# Circuit Operation Calculations
if v_in >= 0:
    # Forward Bias Equation: Ideal Shockley Model
    i_ampere = is_fwd * (np.exp(v_in / (eta * vt)) - 1)
    i_generated = round(i_ampere * 1000.0, 2)  # Output scale strictly structured in mA
    c_unit = "milliampere (mA)"
else:
    # Reverse Bias Equation with Breakdown Mask modeling
    if v_in <= v_breakdown:
        # High field avalanche carrier multiplication simulation
        multiplier = 1.0 / (1.0 - (np.abs(v_in / v_breakdown) ** 4) + 1e-6)
        # Keep inside bounds of thermal survival safety limits
        multiplier = min(multiplier, 2000.0) 
        i_ampere = -is_fwd * multiplier
    else:
        # Saturation Leakage current status
        i_ampere = -is_fwd * (1.0 - np.exp(v_in / vt))
        
    i_generated = round(i_ampere * 1e6, 2)     # Output scale formatted in µA
    c_unit = "microampere (µA)"

st.sidebar.markdown(f"### Generated Output Current:")
st.sidebar.info(f"**⚡ Current $I$ = {i_generated:.2f} {c_unit.split(' ')[0]}**")

if st.sidebar.button("Log Generated Metrics Row"):
    new_row = pd.DataFrame([{"Voltage (V)": round(v_in, 2), "Generated Current": i_generated, "Unit": c_unit}])
    
    if material == "Silicon (Si)":
        st.session_state['si_data'] = pd.concat([st.session_state['si_data'], new_row], ignore_index=True).drop_duplicates(subset=["Voltage (V)"]).sort_values(by="Voltage (V)")
    else:
        st.session_state['ge_data'] = pd.concat([st.session_state['ge_data'], new_row], ignore_index=True).drop_duplicates(subset=["Voltage (V)"]).sort_values(by="Voltage (V)")
        
    log_user_action(st.session_state['student_id'], "Unified_Auto_Row_Added", f"{material} - {bias_mode}: V={v_in}, I={i_generated} {c_unit}")
    st.toast("Calculated data row recorded!", icon="⚙️")

if st.sidebar.button("🚨 Clear Current Material Dataset"):
    if material == "Silicon (Si)":
        st.session_state['si_data'] = pd.DataFrame(columns=["Voltage (V)", "Generated Current", "Unit"])
    else:
        st.session_state['ge_data'] = pd.DataFrame(columns=["Voltage (V)", "Generated Current", "Unit"])
    st.sidebar.warning(f"Cleared all entries for {material}")
    st.rerun()

# --- SCALAR HARMONIZATION ENGINE FOR UNIFIED mA GRAPHING ---
def process_plotting_dataframe(df):
    if df.empty:
        return df.copy()
    processed = df.copy()
    graph_currents = []
    
    for _, row in processed.iterrows():
        val = row["Generated Current"]
        unit = row["Unit"]
        # If generated value is in microamperes, scale down to milliamperes for unified axis mapping
        if "microampere" in unit or "µA" in unit:
            graph_currents.append(round(val / 1000.0, 4))
        else:
            graph_currents.append(round(val, 2))
            
    processed["Current (mA)"] = graph_currents
    return processed

# Fetch active table parameters
active_df = st.session_state['si_data'] if material == "Silicon (Si)" else st.session_state['ge_data']
plot_df = process_plotting_dataframe(active_df)

# --- MAIN SCREEN WORKSPACE ---
col_graph, col_table = st.columns([2, 1])

with col_table:
    st.subheader(f"📋 Experimental Spreadsheet Log [{st.session_state['student_id']}]")
    st.markdown(f"**Material:** `{material}`")
    st.dataframe(active_df, use_container_width=True, hide_index=True)
    st.caption("ℹ️ *Note: Microamperes (µA) from reverse bias tracking are dynamically converted to fractions of Milliamperes (mA) on the unified graphing canvas.*")

with col_graph:
    st.subheader(f"📊 Continuous Curve Tracer Plot: {material}")
    st.markdown("*Both Forward and Reverse Bias generated vectors are mapped continuously on the same coordinate framework.*")
    
    fig = go.Figure()
    
    if not plot_df.empty:
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
        # 2. Reverse Trace Plotting on the identical axis framework
        if not rev_pts.empty:
            fig.add_trace(go.Scatter(
                x=rev_pts["Voltage (V)"], y=rev_pts["Current (mA)"],
                mode='markers+lines', name="Reverse Bias (Scaled to mA)",
                marker=dict(color='#FF4B4B', size=9, symbol='square'),
                line=dict(color='#FF4B4B', width=2, dash='dot')
            ))
            
        x_min = min(plot_df["Voltage (V)"].min() - 2, -15)
        x_max = max(plot_df["Voltage (V)"].max() + 0.5, 1.5)
        y_min = min(plot_df["Current (mA)"].min() - 1, -5)
        y_max = max(plot_df["Current (mA)"].max() + 5, 25)
    else:
        x_min, x_max, y_min, y_max = -15, 2, -5, 25
        st.info("💡 The graph is currently empty. Input applied voltage parameters via the sidebar to generate operational curves.")

    fig.layout = go.Layout(
        xaxis=dict(title="Applied Voltage (Volts, V)", range=[x_min, x_max], zeroline=True, zerolinecolor="white", gridcolor="rgba(128,128,128,0.2)"),
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

if st.session_state['quiz_submitted']:
    st.error(f"🔒 Submission Closed. You have already completed this laboratory evaluation test.")
    st.metric("Your Locked Grade Score", f"{st.session_state['saved_score']}/100")
else:
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
        
        submitted = st.form_submit_button("Submit Final Answers (Single Attempt Only)")
        
        if submitted:
            score = 0
            if q1 == "0.6 V to 0.7 V": score += 20
            if q2 == "Because the depletion region widens, creating an immense barrier resistance that blocks majority carriers.": score += 20
            if q3 == "The drift of thermally generated minority charge carriers sweeping across the junction.": score += 20
            if q4 == "Germanium, due to its smaller forbidden bandgap energy barrier (~0.3V threshold).": score += 20
            if q5 == "The internal electric field triggers carrier multiplication (avalanche breakdown), causing a sharp, massive rise in reverse current.": score += 20
            
            # Commit state metrics to permanent session closure flags
            st.session_state['quiz_submitted'] = True
            st.session_state['saved_score'] = score
            
            log_user_action(st.session_state['student_id'], "Diode_Quiz_Locked_Submission", f"Score: {score}/100")
            st.rerun()

st.markdown("---")
if st.button("Log Out / Reset Lab Bench"):
    st.session_state['authenticated'] = False
    st.session_state['quiz_submitted'] = False
    st.session_state['saved_score'] = 0
    st.session_state['si_data'] = pd.DataFrame(columns=["Voltage (V)", "Generated Current", "Unit"])
    st.session_state['ge_data'] = pd.DataFrame(columns=["Voltage (V)", "Generated Current", "Unit"])
    st.rerun()
