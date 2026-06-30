import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Automated Diode Loop Lab Bench",
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
        log_data.to_csv(log_data, index=False)
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

# Base Dataframe logs initialized in clean session memory slots
if 'si_data' not in st.session_state:
    st.session_state['si_data'] = pd.DataFrame(columns=["Applied Voltage (V)", "Circuit Current (mA)"])
if 'ge_data' not in st.session_state:
    st.session_state['ge_data'] = pd.DataFrame(columns=["Applied Voltage (V)", "Circuit Current (mA)"])

# --- HEADER ---
st.title("🔌 Practical: Automated Current Generation in Si and Ge Diode Loop Circuits")
st.subheader("Department of Physics/Electronics — Solid State Electronics Laboratory")
st.markdown("---")

# --- LOGIN GATEWAY ---
if not st.session_state['authenticated']:
    st.info("👋 Welcome! Please initialize the laboratory bench by entering your Matriculation Number.")
    matric_no = st.text_input("Student Matriculation Number:")
    if st.button("Initialize Lab Bench"):
        if matric_no.strip() != "":
            st.session_state['si_data'] = pd.DataFrame(columns=["Applied Voltage (V)", "Circuit Current (mA)"])
            st.session_state['ge_data'] = pd.DataFrame(columns=["Applied Voltage (V)", "Circuit Current (mA)"])
            st.session_state['student_id'] = matric_no.strip()
            st.session_state['authenticated'] = True
            st.session_state['quiz_submitted'] = False 
            st.session_state['saved_score'] = 0
            
            log_user_action(st.session_state['student_id'], "Session_Start", "Initialized Fresh App Loop Lab Bench.")
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
st.sidebar.markdown("*Vary the applied voltage ($0.00\\text{ V}$ to $20.00\\text{ V}$ in steps of $0.10\\text{ V}$). Current output updates automatically in mA.*")

# Strict constraints applied: Voltage bounds set exactly between 0.00 and 20.00 with 0.10 steps
v_magnitude = st.sidebar.number_input(
    "Input Voltage Magnitude (Volts):", 
    min_value=0.00, 
    max_value=20.00, 
    value=0.00, 
    step=0.10, 
    format="%.2f"
)

# Internally mirror polarity based on forward/reverse selection state
v_in = v_magnitude if bias_mode == "Forward Bias Region" else -v_magnitude

# --- LOOP CIRCUIT MATHEMATICAL PHYSICS ENGINE (KVL SOLVER) ---
# Parameters based exactly on user specifications
R_series = 500.0  # 500 Ohms limiting resistor
vt = 0.0259       # Thermal voltage at room temperature

if material == "Silicon (Si)":
    is_sat = 1e-12       # 1 pA
    eta = 1.3
    v_breakdown = -12.0
else: # Germanium (Ge)
    is_sat = 1e-6        # 1 µA
    eta = 1.0
    v_breakdown = -6.0

def solve_circuit_current(v_source, r_limit, is_sat, eta, vt, v_bd):
    """Numerically determines the exact loop current using a Newton-Raphson framework."""
    if v_source >= 0:
        # Forward bias loop tracking solution
        if v_source < 0.2: 
            return (is_sat * (np.exp(v_source / (eta * vt)) - 1)) * 1000.0
        
        # Iterative solver initialization for non-linear exponential intersection
        v_diode = 0.6 if material == "Silicon (Si)" else 0.25
        for _ in range(15):
            f = v_source - v_diode - (is_sat * (np.exp(v_diode / (eta * vt)) - 1) * r_limit)
            df = -1.0 - ((is_sat / (eta * vt)) * np.exp(v_diode / (eta * vt)) * r_limit)
            v_diode_next = v_diode - f / df
            if abs(v_diode_next - v_diode) < 1e-5:
                v_diode = v_diode_next
                break
            v_diode = v_diode_next
        i_loop_ma = (v_source - v_diode) / r_limit * 1000.0
        return max(i_loop_ma, 0.0)
    else:
        # Reverse bias loop state containing breakdown thresholds
        if v_source <= v_bd:
            # Avalanche region multiplier modeling
            multiplier = 1.0 / (1.0 - (np.abs(v_source / v_bd) ** 4) + 1e-6)
            multiplier = min(multiplier, 2000.0)
            return (-is_sat * multiplier) * 1000.0
        else:
            return (-is_sat * (1.0 - np.exp(v_source / vt))) * 1000.0

# Execute automatic simulation calculations
i_generated_ma = solve_circuit_current(v_in, R_series, is_sat, eta, vt, v_breakdown)

# Format to strict 2 decimal precision scales
v_in = round(v_in, 2)
i_generated_ma = round(i_generated_ma, 2)

st.sidebar.markdown(f"### Generated Output Current:")
st.sidebar.info(f"**⚡ Loop Current $I$ = {i_generated_ma:.2f} mA**")

if st.sidebar.button("Log Generated Metrics Row"):
    new_row = pd.DataFrame([{"Applied Voltage (V)": v_in, "Circuit Current (mA)": i_generated_ma}])
    
    if material == "Silicon (Si)":
        st.session_state['si_data'] = pd.concat([st.session_state['si_data'], new_row], ignore_index=True).drop_duplicates(subset=["Applied Voltage (V)"]).sort_values(by="Applied Voltage (V)")
    else:
        st.session_state['ge_data'] = pd.concat([st.session_state['ge_data'], new_row], ignore_index=True).drop_duplicates(subset=["Applied Voltage (V)"]).sort_values(by="Applied Voltage (V)")
        
    log_user_action(st.session_state['student_id'], "Loop_Auto_Row_Added", f"{material} - {bias_mode}: V={v_in}, I={i_generated_ma} mA")
    st.toast("Automated measurement logged!", icon="⚙️")

if st.sidebar.button("🚨 Clear Current Material Dataset"):
    if material == "Silicon (Si)":
        st.session_state['si_data'] = pd.DataFrame(columns=["Applied Voltage (V)", "Circuit Current (mA)"])
    else:
        st.session_state['ge_data'] = pd.DataFrame(columns=["Applied Voltage (V)", "Circuit Current (mA)"])
    st.sidebar.warning(f"Cleared all entries for {material}")
    st.rerun()

# Fetch active table parameters
active_df = st.session_state['si_data'] if material == "Silicon (Si)" else st.session_state['ge_data']

# --- MAIN SCREEN WORKSPACE ---
col_graph, col_table = st.columns([2, 1])

with col_table:
    st.subheader(f"📋 Experimental Spreadsheet Log [{st.session_state['student_id']}]")
    st.markdown(f"**Active Material View:** `{material}`")
    
    # Format visible data tables strictly to 2 decimal places
    formatted_df = active_df.copy()
    if not formatted_df.empty:
        formatted_df["Applied Voltage (V)"] = formatted_df["Applied Voltage (V)"].map("{:.2f}".format)
        formatted_df["Circuit Current (mA)"] = formatted_df["Circuit Current (mA)"].map("{:.2f}".format)
        
    st.dataframe(formatted_df, use_container_width=True, hide_index=True)
    st.caption("ℹ️ *Physics Note: Values represent automated loops solved under a 500 Ω resistor matrix burden.*")

with col_graph:
    st.subheader(f"📊 Continuous Unified Curve Tracer: {material}")
    
    fig = go.Figure()
    
    if not active_df.empty:
        fwd_pts = active_df[active_df["Applied Voltage (V)"] >= 0]
        rev_pts = active_df[active_df["Applied Voltage (V)"] < 0]
        
        if not fwd_pts.empty:
            fig.add_trace(go.Scatter(
                x=fwd_pts["Applied Voltage (V)"], y=fwd_pts["Circuit Current (mA)"],
                mode='markers+lines', name="Forward Bias (mA)",
                marker=dict(color='#00CC96', size=9),
                line=dict(color='#00CC96', width=2)
            ))
        if not rev_pts.empty:
            fig.add_trace(go.Scatter(
                x=rev_pts["Applied Voltage (V)"], y=rev_pts["Circuit Current (mA)"],
                mode='markers+lines', name="Reverse Bias (mA)",
                marker=dict(color='#FF4B4B', size=9, symbol='square'),
                line=dict(color='#FF4B4B', width=2, dash='dot')
            ))
            
        x_min = min(active_df["Applied Voltage (V)"].min() - 2, -22)
        x_max = max(active_df["Applied Voltage (V)"].max() + 2, 22)
        y_min = min(active_df["Circuit Current (mA)"].min() - 5, -15)
        y_max = max(active_df["Circuit Current (mA)"].max() + 5, 45)
    else:
        x_min, x_max, y_min, y_max = -22, 22, -15, 45
        st.info("💡 Coordinate canvas clear. Adjust the sidebar inputs and select 'Log Generated Metrics Row' to construct live curves.")

    fig.layout = go.Layout(
        xaxis=dict(title="Applied Loop Voltage (Volts, V)", range=[x_min, x_max], zeroline=True, zerolinecolor="white", gridcolor="rgba(128,128,128,0.2)"),
        yaxis=dict(title="Circuit Current (Milliamperes, mA)", range=[y_min, y_max], zeroline=True, zerolinecolor="white", gridcolor="rgba(128,128,128,0.2)"),
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
            "3. What forms the tiny reverse leakage current measured during your practical?",
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
            if q4 == "Germanium (Ge), due to its smaller forbidden bandgap energy barrier (~0.3V threshold).": score += 20
            if q5 == "The internal electric field triggers carrier multiplication (avalanche breakdown), causing a sharp, massive rise in reverse current.": score += 20
            
            st.session_state['quiz_submitted'] = True
            st.session_state['saved_score'] = score
            
            log_user_action(st.session_state['student_id'], "Diode_Quiz_Locked_Submission", f"Score: {score}/100")
            st.rerun()

st.markdown("---")
if st.button("Log Out / Reset Lab Bench"):
    st.session_state['authenticated'] = False
    st.session_state['quiz_submitted'] = False
    st.session_state['saved_score'] = 0
    st.session_state['si_data'] = pd.DataFrame(columns=["Applied Voltage (V)", "Circuit Current (mA)"])
    st.session_state['ge_data'] = pd.DataFrame(columns=["Applied Voltage (V)", "Circuit Current (mA)"])
    st.rerun()
