# Interactive P-N Junction Diode Characteristics & Learning Analytics Application

An interactive, web-based virtual laboratory application designed for Higher National Diploma (HND) Physics with Electronics programs. This platform serves as an interactive curve tracer and data logger for recording the forward and reverse bias characteristics of Silicon (Si) and Germanium (Ge) P-N junction diodes using voltage and current parameters.

---

## 📌 Project Overview
In tertiary physics laboratories, continuous access to specialized instrumentation like precision semiconductor curve tracers, variable DC power units, and micro-ammeters can be constrained. 

This project addresses this limitation by establishing an **Interactive Semiconductor Physics Simulator** using Python and Streamlit. The application allows students to switch between Silicon and Germanium, select bias modes (Forward or Reverse), manually input experimental values for Voltage (V) and Current (mA/µA), and map their inputs dynamically against theoretical semiconductor characteristics curves. Concurrently, an embedded **Learning Analytics Engine** captures student workspace actions, helping instructors evaluate troubleshooting behaviors and data tracking performance.

---

## 🛠️ Features

* **Dual Material Lab Bench:** Compares Silicon (Si) and Germanium (Ge) properties to visually demonstrate variance in junction barriers ($0.7\text{V}$ vs $0.3\text{V}$).
* **Biasing Mode Operations:** Offers independent operational spaces for Forward Bias and Reverse Bias analysis.
* **Dual Unit Input Instrumentation:** * Forward Bias inputs take Voltage in **Volts (V)** and Current in **Milliamperes (mA)**.
  * Reverse Bias inputs take Voltage in **Volts (V)** and Leakage Current in **Microamperes (µA)**.
* **Interactive Graphical Tracer:** Displays a dark-themed Plotly canvas that projects theoretical curves and overlays a custom cursor indicator identifying the student's logged coordinates.
* **Post-Laboratory Evaluation Form:** Integrates 5 comprehensive viva-voce diagnostic quiz questions focused on p-n junction physics.
* **Persistent Telemetry Logging:** Automatically serializes and logs authentication events, parameter values, and quiz scores into `student_analytics_log.csv`.
* **Instructor Audit Portal:** Synthesizes historical event records into frequency distribution matrices for tracking student progress.

---

## 📐 System Architecture

The software architecture relies on three cohesive modules to preserve structural separation:

```text
[Student Frontend UI Panel] <─── Session State ───> [Learning Analytics Tracker]
              │                                                    │
              ▼                                                    ▼
 [Mathematical Physics Engine]                     [Persistent Analytics CSV Database]
