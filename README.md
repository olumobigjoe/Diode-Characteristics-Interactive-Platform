# Interactive Semiconductor Physics Simulation & Learning Analytics Application

An interactive, web-based virtual laboratory application designed for Higher National Diploma (HND) Physics with Electronics programs. This platform serves as a software-defined digital curve tracer to model and compare the operational I-V characteristics of Silicon (Si) and Germanium (Ge) P-N junction diodes while actively tracking student learning metrics.

---

## 📌 Project Overview
In many engineering and technical laboratories, providing students with constant access to precision source measurement units (SMUs), variable DC power supplies, thermal chambers, and semiconductor curve tracers can be limited due to equipment costs and fragility. 

This project solves this bottleneck by implementing a mathematically rigorous **Semiconductor Physics Engine** using Python and Streamlit. The application computes the non-linear electronic behaviors of Silicon and Germanium p-n junctions under varying forward/reverse bias voltages, ambient temperatures, and doping profiles using the Shockley ideal diode equation. Concurrently, an embedded **Learning Analytics Engine** dynamically logs student interaction telemetry data, mapping how systematically students calibrate variables and perform on integrated diagnostic evaluations.

---

## 🛠️ Features

* **Silicon vs. Germanium Comparative Engine:** Simulates and plots both target materials dynamically to visually demonstrate differences in forbidden energy bandgaps ($1.12\text{ eV}$ vs $0.67\text{ eV}$).
* **Variable Bias Voltage Sweeping:** Provides continuous sweeps from $-5.0\text{V}$ (reverse bias testing) up to $+1.0\text{V}$ (forward bias execution).
* **Thermal Chamber Simulator:** Models temperature scaling (from $-40^\circ\text{C}$ to $+120^\circ\text{C}$) to demonstrate thermal leakage variance, shifts in thermal voltage ($V_t$), and runaway states.
* **Avalanche Breakdown Modeling:** Incorporates high-field mathematical masks to accurately show reverse breakdown voltage degradation thresholds.
* **Interactive Data Canvas:** Utilizes responsive Plotly dark-themed graphs to allow precise coordinate tracking when cursor hover paths are engaged.
* **Persistent Telemetry Logging:** Automatically serializes and appends student parameter tunings, session lifecycles, and evaluation scores into a structured `student_analytics_log.csv`.
* **Instructor Audit Dashboard:** Synthesizes aggregated interaction logs to show active frequency distributions and troubleshoot learning workflows.

---

## 📐 System Architecture

The application is structured into three unified tiers to maintain a clean separation of concerns:

```text
[Student Frontend UI Panel] <─── Session State ───> [Learning Analytics Tracker]
              │                                                    │
              ▼                                                    ▼
 [Mathematical Physics Engine]                     [Persistent Analytics CSV Database]
