import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Semiconductor Junction Lab & Analytics",
    page_icon="🔬",
    layout="wide"
)

# --- DIRECTORY & FILE SETUP FOR LEARNING ANALYTICS ---
LOG_FILE = "student_analytics_log.csv"

def log_user_action(student_id, action_type, details):
    """Logs student interaction telemetry paths to a CSV for analytics tracking."""
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

# --- INITIALIZE SESSION STATE VARIABLES ---
if 'student_id' not in st.session_state:
    st.session_state['student_id'] = "Guest_Student"
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'quiz_submitted' not in st.session_state:
    st.session_state['quiz_submitted'] = False

# --- APPLICATION HEADER ---
st.title("🔬 Interactive Semiconductor Junction Physics & Analytics Platform")
st.subheader("Department of Physics/Electronics — Solid State Electronics Practical Bench")
st.markdown("---")

# --- USER AUTHENTICATION / LOGIN ---
if not st.session_state['authenticated']:
    st.info("👋 Welcome! Please enter your Student Matriculation Number to initialize the diode calibration panel.")
    matric_no = st.text_input("Enter Student Matriculation Number (e.g., HND/PHY/2026/089):")
    if st.button("Initialize Lab Bench"):
        if matric_no.strip() != "":
            st.session_state['student_id'] = matric_no.strip()
            st.session_state['authenticated'] = True
            log_user_action(st.session_state['student_id'], "Session_Start", "Initialized diode characterization bench.")
            st.rerun()
        else:
            st.warning("Please enter a valid identification number.")
    st.stop()

# --- SIDEBAR: VIRTUAL INSTRUMENTATION CONTROLS ---
st.sidebar.header("🎛️ Diode Tester Controls")
st.sidebar.markdown("*Vary parameters to evaluate Silicon vs Germanium characteristics*")

# Instrumentation Sliders
material_selection = st.sidebar.radio("1. Select Target Semiconductor", ["Silicon (Si) Diode", "Germanium (Ge) Diode"])
temp_celsius = st.sidebar.slider("2. Ambient Thermal Chamber Temp (°C)", min_value=-40, max_value=120, value=25, step=5)
doping_slider = st.sidebar.select_slider("3. Junction Doping Density (cm⁻³)", options=[1e15, 1e16, 1e17, 1e18], value=1e16)

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Logged in as:** `{st.session_state['student_id']}`")
if st.sidebar.button("Log Out / Reset Bench"):
    log_user_action(st.session_state['student_id'], "Session_End", "Logged out of bench.")
    st.session_state['authenticated'] = False
    st.session_state['quiz_submitted'] = False
    st.rerun()

if st.sidebar.button("Log Experimental Curve State"):
    details = f"Material: {material_selection}, Temp: {temp_celsius}°C, Doping: {doping_slider}"
    log_user_action(st.session_state['student_id'], "Parameter_Calibration", details)
    st.sidebar.success("Characteristics dataset logged!")

# --- CORE MATHEMATICAL SEMICONDUCTOR SIMULATION ENGINE ---
def simulate_diode_characteristics(material, temp_c, doping):
    # Fundamental Constants
    q = 1.602e-19       # Charge of electron (C)
    k = 1.381e-23       # Boltzmann constant (J/K)
    T = temp_c + 273.15 # Convert to Absolute Kelvin
    
    # Material specific definitions
    Eg = 1.12 if "Silicon" in material else 0.67  # Bandgap Energy in eV
    
    # Calculate thermal voltage
    V_thermal = (k * T) / q
    
    # Baseline reverse saturation tracking constants
    Is0 = 1e-12 if "Silicon" in material else 1e-6
    Is = Is0 * ((T / 300.15) ** 3) * np.exp(-Eg / (2 * V_thermal))
    
    # Shift saturation scales slightly relative to doping density adjustments
    Is = Is * (1e16 / doping)
    
    # Generate interactive input voltage sweeping ranges (-5V reverse to +1V forward bias)
    v_bias = np.linspace(-5.0, 1.0, 300)
    
    # Implement the standard Shockley Diode equation model
    i_diode = Is * (np.exp(v_bias / V_thermal) - 1)
    
    # Model extreme high-field reverse breakdown thresholds
    v_breakdown = -4.5 if "Silicon" in material else -3.5
    i_diode = np.where(v_bias < v_breakdown, i_diode - 0.04 * (v_breakdown - v_bias)**2, i_diode)
    
    return v_bias, i_diode, V_thermal, Is

# Compute physical datasets based on sidebar states
voltage_array, current_array, vt_val, leakage_val = simulate_diode_characteristics(material_selection, temp_celsius, doping_slider)

# --- MAIN DASHBOARD INTERACTIVE LAB LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"📊 Real-Time I-V Characteristics: {material_selection}")
    st.markdown("Hover across the curve coordinates to evaluate exact voltage and current properties.")
    
    # Formulate interactive graphical data trace structures
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=voltage_array, 
        y=current_array, 
        mode='lines', 
        name=material_selection, 
        line=dict(color='#00CC96' if "Silicon" in material_selection else '#FF4B4B', width=3)
    ))
    
    # Direct dictionary configuration bypass to ensure compliance across Python 3.14 cloud revisions
    fig.layout = go.Layout(
        xaxis=dict(title="Applied Bias Voltage (V)", range=[-5.2, 1.1], zeroline=True, zerolinecolor="gray"),
        yaxis=dict(title="Diode Current (A)", range=[-0.02, 0.06], zeroline=True, zerolinecolor="gray"),
        template="plotly_dark",
        margin=dict(l=20, r=20, t=20, b=20),
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📋 Instrumentation Panel Readouts")
    st.markdown("Theoretical variables extracted from the junction physics calculations:")
    
    st.metric(label="Calculated Thermal Voltage (V_t)", value=f"{vt_val:.4f} V")
    st.metric(label="Reverse Saturation Current (I_s)", value=f"{leakage_val:.4e} A")
    
    barrier_potential = 0.7 if "Silicon" in material_selection else 0.3
    st.markdown(f"**Junction Turn-on Threshold (Knee):** ~`{barrier_potential}V` at room temperature.")
    
    st.info("💡 **Junction Physics Analysis:** Silicon exhibits a lower reverse leakage current ($I_s$) compared to Germanium due to its wider energy bandgap. However, Germanium provides a lower forward conduction threshold.")

st.markdown("---")

# --- INTERACTIVE ASSESSMENT PORTAL ---
st.header("📝 Diagnostic Evaluation Module")
st.markdown("Answer these analytical practical questions based on your current lab observations.")

with st.form("diode_quiz"):
    ans1 = st.radio(
        "1. Why does a Germanium diode initiate forward conduction at a lower applied voltage (~0.3V) compared to Silicon (~0.7V)?",
        ["Germanium has a smaller forbidden energy bandgap (0.67 eV) than Silicon (1.12 eV).",
         "Germanium possesses a significantly higher doping profile than standard Silicon matrices.",
         "Silicon exhibits an increased thermal voltage rating under identical ambient room testing temperatures."]
    )
    
    ans2 = st.radio(
        "2. What happens to the forward bias curve profile when the temperature within the thermal chamber increases?",
        ["The curve moves to the right, requiring greater turn-on voltage bounds.",
         "The turn-on potential knee shifts to the left, indicating decreased internal barrier height.",
         "The baseline characteristics profile collapses instantly into an absolute linear vacuum trace."]
    )
    
    submitted = st.form_submit_button("Submit Experimental Evaluation Answers")
    
    if submitted:
        st.session_state['quiz_submitted'] = True
        score = 0
        
        if ans1 == "Germanium has a smaller forbidden energy bandgap (0.67 eV) than Silicon (1.12 eV).":
            score += 50
        if ans2 == "The turn-on potential knee shifts to the left, indicating decreased internal barrier height.":
            score += 50
            
        st.subheader("🎯 Test Performance Results")
        st.write(f"Your analytical grade score: **{score}/100**")
        
        if score == 100:
            st.success("Splendid work! Your answers match standard solid-state electronics engineering models.")
        else:
            st.error("Some criteria evaluations are incorrect. Tweak your parameters to compare Silicon and Germanium traits again.")
            
        log_user_action(st.session_state['student_id'], "Quiz_Submission", f"Score: {score}%. Q1: {ans1}, Q2: {ans2}")

st.markdown("---")

# --- INSTRUCTOR PORTAL IN SCRIPT ---
st.header("📊 Instructor Portal & Learning Analytics Summary")
st.markdown("*Real-time audit trails showing student interactions and learning trends.*")

if os.path.exists(LOG_FILE):
    try:
        df_logs = pd.read_csv(LOG_FILE)
        user_logs = df_logs[df_logs["Student_ID"] == st.session_state['student_id']]
        
        col_summary1, col_summary2 = st.columns(2)
        with col_summary1:
            st.subheader("Your Live Telemetry Log Profile")
            st.dataframe(user_logs, use_container_width=True)
            
        with col_summary2:
            st.subheader("Global Action Breakdown Metric")
            action_counts = df_logs["Action_Type"].value_counts().reset_index()
            action_counts.columns = ["Action", "Frequency"]
            
            fig_pie = go.Figure(data=[go.Pie(labels=action_counts["Action"], values=action_counts["Frequency"], hole=.3)])
            fig_pie.update_layout(template="plotly_dark", margin=dict(l=10, r=10, t=30, b=10), height=250)
            st.plotly_chart(fig_pie, use_container_width=True)
    except Exception as e:
        st.warning("Data repository tracking stream initializing...")
else:
    st.info("No learning analytics records have been aggregated yet. Interact with control structures above to initialize tracking pipelines.")