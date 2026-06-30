import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="P-N Junction Characteristics Lab",
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

# --- HEADER ---
st.title("🔌 Practical: Forward & Reverse Bias Characteristics of Si and Ge Diodes")
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
            log_user_action(st.session_state['student_id'], "Session_Start", "Initialized Diode Practical Bench.")
            st.rerun()
        else:
            st.warning("Identification required to track experimental logs.")
    st.stop()

# --- SIDEBAR CONFIGURATION CONTROLS ---
st.sidebar.header("🎛️ Experimental Parameters")
material = st.sidebar.radio("Select Semiconductor Material:", ["Silicon (Si)", "Germanium (Ge)"])
bias_mode = st.sidebar.radio("Select Bias Mode:", ["Forward Bias", "Reverse Bias"])

st.sidebar.markdown("---")
# Manual Table Data Input Fields
st.sidebar.subheader("📥 Record Manual Readings")
if bias_mode == "Forward Bias":
    v_input = st.sidebar.number_input("Input Voltage (Volts):", min_value=0.0, max_value=1.5, value=0.0, step=0.1)
    i_input = st.sidebar.number_input("Input Current (milliampere, mA):", min_value=0.0, max_value=100.0, value=0.0, step=1.0)
else:
    v_input = st.sidebar.number_input("Input Voltage (Volts):", min_value=-50.0, max_value=0.0, value=0.0, step=5.0)
    i_input = st.sidebar.number_input("Input Leakage Current (microampere, µA):", min_value=-100.0, max_value=0.0, value=0.0, step=1.0)

if st.sidebar.button("Log Reading into Data Table"):
    log_details = f"Material: {material}, Mode: {bias_mode}, V: {v_input}V, I: {i_input}"
    log_user_action(st.session_state['student_id'], "Manual_Data_Entry", log_details)
    st.sidebar.success("Reading saved to laboratory session log.")

# --- CORE MATH ENGINE FOR CHARACTERISTIC PLOTS ---
def generate_diode_curve(mat_type):
    # Generates theoretical curve array for baseline comparison
    v_fwd = np.linspace(0.0, 1.2, 150)
    v_rev = np.linspace(-15.0, 0.0, 150)
    
    if mat_type == "Silicon (Si)":
        is_fwd = 1e-12
        vt = 0.026
        i_fwd = is_fwd * (np.exp(v_fwd / (1 * vt)) - 1) * 1000 # Convert to mA
        i_rev = -0.01 * np.ones_like(v_rev) # small leakage in mA
    else: # Germanium
        is_fwd = 1e-6
        vt = 0.026
        i_fwd = is_fwd * (np.exp(v_fwd / (1 * vt)) - 1) * 1000 # Convert to mA
        i_rev = -0.1 * np.ones_like(v_rev) # slightly higher leakage
        
    return v_fwd, i_fwd, v_rev, i_rev

v_fwd, i_fwd, v_rev, i_rev = generate_diode_curve(material)

# --- PRESENTATION INTERFACE LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📊 Characteristic Curve Tracer Plot ({material})")
    
    fig = go.Figure()
    if bias_mode == "Forward Bias":
        fig.add_trace(go.Scatter(x=v_fwd, y=i_fwd, mode='lines', name="Forward Bias Curve", line=dict(color='#00CC96', width=3)))
        # Current data point highlight
        fig.add_trace(go.Scatter(x=[v_input], y=[i_input], mode='markers', name="Your Reading", marker=dict(color='yellow', size=12, symbol='circle')))
        x_range = [-0.1, 1.3]
        y_range = [-5, max(i_fwd)+10]
        y_title = "Forward Current (mA)"
    else:
        fig.add_trace(go.Scatter(x=v_rev, y=i_rev, mode='lines', name="Reverse Bias Curve", line=dict(color='#FF4B4B', width=3)))
        # Convert microamps to milli for plot sync if working in reverse mode
        fig.add_trace(go.Scatter(x=[v_input], y=[i_input / 1000 if bias_mode=="Reverse Bias" else i_input], mode='markers', name="Your Reading", marker=dict(color='yellow', size=12)))
        x_range = [-16.0, 0.5]
        y_range = [-1.5, 0.5]
        y_title = "Reverse Current (mA)"

    fig.layout = go.Layout(
        xaxis=dict(title="Applied Voltage (Volts, V)", range=x_range, zeroline=True, zerolinecolor="gray"),
        yaxis=dict(title=y_title, range=y_range, zeroline=True, zerolinecolor="gray"),
        template="plotly_dark",
        height=450,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📋 Experimental Instrument Readouts")
    barrier = 0.7 if material == "Silicon (Si)" else 0.3
    st.markdown(f"**Selected Material:** `{material}`")
    st.markdown(f"**Theoretical Barrier Potential ($V_B$):** `~{barrier} V`")
    st.markdown(f"**Current Input Voltage:** `{v_input} V`")
    st.markdown(f"**Current Input Current:** `{i_input} mA/µA`")
    st.info("💡 Observe how the slope changes dynamically. In Forward Bias, current remains near zero until the applied voltage overcomes the built-in barrier voltage threshold.")

st.markdown("---")

# --- EXPERIMENTAL EVALUATION QUIZ (5 QUESTIONS) ---
st.header("📝 Post-Laboratory Viva-Voce Evaluation")
st.markdown("Answer these 5 critical questions based on your practical observations of semiconductor junction mechanics:")

with st.form("lab_quiz"):
    q1 = st.radio(
        "1. What is the approximate potential barrier voltage required to initiate significant forward conduction in a Silicon diode at room temperature?",
        ["0.1 V to 0.2 V", "0.3 V to 0.4 V", "0.6 V to 0.7 V"]
    )
    
    q2 = st.radio(
        "2. How does the width of the depletion region respond when a P-N junction is placed under Reverse Bias conditions?",
        ["The depletion region widens, increasing the internal barrier potential resistance.",
         "The depletion region narrows, allowing majority charge carriers to tunnel across easily.",
         "The depletion region width remains strictly unchanged, maintaining fixed atomic symmetry."]
    )
    
    q3 = st.radio(
        "3. What physical mechanism is primarily responsible for the tiny leakage current observed during extreme reverse bias below breakdown?",
        ["Majority carrier drift across the metal contacts.",
         "Thermally generated minority charge carrier movement across the depletion region.",
         "Mechanical friction along the covalent bond crystal grid lines."]
    )
    
    q4 = st.radio(
        "4. Which diode material displays a lower turn-on knee voltage threshold, and why?",
        ["Silicon, because it has a wider forbidden band gap structural matrix.",
         "Germanium, because it possesses a smaller forbidden bandgap energy barrier (0.67 eV).",
         "Both exhibit completely identical turn-on properties because thermal voltage dominates."]
    )
    
    q5 = st.radio(
        "5. What happens if the reverse bias voltage is continuously increased past the manufacturer's specified Peak Inverse Voltage (PIV) rating?",
        ["The diode enters the avalanche or zener breakdown region, resulting in a sudden, sharp rise in reverse current.",
         "The diode current drops to absolute zero permanently due to covalent hardening.",
         "The diode instantly transforms into an ideal vacuum-state inductor circuit."]
    )
    
    submitted = st.form_submit_button("Submit Lab Answers for Grading")
    
    if submitted:
        score = 0
        if q1 == "0.6 V to 0.7 V": score += 20
        if q2 == "The depletion region widens, increasing the internal barrier potential resistance.": score += 20
        if q3 == "Thermally generated minority charge carrier movement across the depletion region.": score += 20
        if q4 == "Germanium, because it possesses a smaller forbidden bandgap energy barrier (0.67 eV).": score += 20
        if q5 == "The diode enters the avalanche or zener breakdown region, resulting in a sudden, sharp rise in reverse current.": score += 20
        
        st.subheader(f"🎯 Your Score: {score}/100")
        if score == 100:
            st.success("Perfect score! You have successfully mastered diode operational characteristics.")
        else:
            st.warning("Review your readings and check the knee thresholds on the Plotly tracer to find your mistakes.")
        
        log_user_action(st.session_state['student_id'], "Quiz_Submission", f"Score: {score}/100")

st.markdown("---")
# --- PORTAL FOOTER ---
if st.button("Log Out / Reset Lab Bench"):
    st.session_state['authenticated'] = False
    st.rerun()