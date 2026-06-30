# Unified Custom Trace P-N Junction Diode Curve Tracer & Learning Analytics

An interactive, data-logging virtual laboratory application engineered for Higher National Diploma (HND) Physics with Electronics programs. This platform serves as a software-defined digital curve tracer, allowing students to input manual experimental measurements for Voltage and Current to continuously map both forward and reverse semiconductor bias coordinates within a single, unified graph framework.

---

## 📌 Project Overview
In tertiary physical science and electronics laboratories, providing continuous access to specialized instrumentation like precision semiconductor curve tracers, variable DC power units, and micro-ammeters can be constrained. 

This project addresses this limitation by establishing an **Interactive Semiconductor Physics Simulator** using Python and Streamlit. The application allows students to switch between Silicon and Germanium, select bias regions, and manually input custom experimental values for Voltage (V) and Current with strict 2-decimal precision. 

Unlike static models, this platform forces both Forward and Reverse bias traces onto the same coordinate grid for clear material comparison while an embedded **Learning Analytics Engine** dynamically captures student workspace metrics into a structured telemetry format.

---

## 🛠️ Key Functional Features

* **Unified Graph Workspace:** Eliminates divided tracking views. Both positive forward quadrant and negative reverse quadrant inputs display on a single Plotly plane.
* **Flexible Unit Configurations:** Accommodates current input selections in both **milliamperes (mA)** and **microamperes (µA)** with strict two-decimal input enforcement.
* **Automatic Scalar Harmonization:** The backend script dynamically parses microampere readings ($\mu\text{A}$) down to functional fractions of a milliampere ($\text{mA}$) to prevent trace scaling distortion on the mutual coordinate plane.
* **Dual Material Comparison:** Compares Silicon (Si) and Germanium (Ge) operational properties to visually demonstrate variance in junction barriers ($0.7\text{V}$ vs $0.3\text{V}$).
* **Post-Laboratory Evaluation Form:** Integrates 5 comprehensive viva-voce diagnostic quiz questions focused on p-n junction physics.
* **Persistent Telemetry Logging:** Automatically serializes and logs authentication events, parameter values, and quiz scores into `student_analytics_log.csv`.

---

## 📐 System Architecture

The software architecture relies on three cohesive modules to preserve structural separation:

```text
[Student Frontend UI Panel] <─── Session State ───> [Learning Analytics Tracker]
              │                                                    │
              ▼                                                    ▼
 [Mathematical Physics Engine]                     [Persistent Analytics CSV Database]
