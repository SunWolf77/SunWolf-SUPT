# 🜂 SunWolf_ReSunance_Continuum v6.5  
### Sheppard’s Universal Proxy Theory (SUPT) :: Real-Time Solar–Volcanic Coupling Monitor  

A real-time **Streamlit dashboard** for monitoring solar-volcanic resonance at **Campi Flegrei**, Italy.  
Built on *Sheppard’s Universal Proxy Theory (SUPT)*, it models dynamic energy coupling between solar wind pressure (ψₛ), geomagnetic activity (Kp), and shallow subsurface stress dynamics using live and local data streams.

---

## ⚡️ Overview

The **SunWolf ReSunance Continuum** dashboard visualizes harmonic coherence and instability in volcanic systems via SUPT metrics:

- **EII (Energetic Instability Index)** — weighted measure of system imbalance.
- **RPAM (Reactive Pressure Alignment Mode)** — current instability phase.
- **CCI (Coupling Coherence Index)** — correlation between ψₛ (solar proxy) and local seismic depth oscillations.
- **ψₛ Forecast** — harmonic projection of energy resonance for the next 48 hours.

Built for both **scientific visualization** and **educational outreach**, it integrates live NOAA data and local INGV seismic feeds.

---

## 🛰 Live Demo  
🔗 **Streamlit Cloud:**  
[https://sunwolfresunancecontinuumgit-xeytsacffy8rhz8ovahqme.streamlit.app](https://sunwolfresunancecontinuumgit-xeytsacffy8rhz8ovahqme.streamlit.app)

*(If unavailable, clone locally using instructions below.)*

---

## 🧠 Features

| Category | Description |
|-----------|-------------|
| 🌋 **Volcanic Inputs** | Local INGV data (`events.csv`) cleaned automatically — reads *Time, Magnitude, Depth (km)* |
| ☀️ **Solar Inputs** | ψₛ (solar pressure proxy), wind speed, and NOAA Kp index |
| 🧮 **Metrics** | EII (instability), RPAM (phase), and CCI (coherence gauge) |
| 📈 **Visuals** | Plotly-based harmonic ψₛ forecast (48-hour) and dynamic coherence gauge |
| 🔁 **Manual Refresh** | Sidebar “🔁 Refresh Data” reloads NOAA + INGV sources |
| 🧩 **Offline Resilience** | Falls back to `events.csv` or synthetic data if APIs fail |

---

## 🧪 Metric Formulas

### Energetic Instability Index (EII)
\[
EII = (Md_{max} × 0.2) + (Md_{mean} × 0.15) + (Shallow_{ratio} × 0.4) + (ψ_s × 0.25)
\]

### RPAM Classification
| Range | Phase | Meaning |
|--------|--------|----------|
| EII ≥ 0.85 | **ACTIVE** | Collapse window initiated |
| 0.60–0.84 | **ELEVATED** | Pressure coupling phase |
| < 0.60 | **MONITORING** | Stable system |

### Coupling Coherence Index (CCI)
\[
CCI = corr^2(ψ_s, Depth_{norm})
\]
Measures ψₛ–depth alignment; color-coded gauge (red → orange → green).

---

## ⚙️ Installation (Local)

### 1. Clone this repository
```bash
git clone https://github.com/<your-username>/SunWolf_ReSunance_Continuum.git
cd SunWolf_ReSunance_Continuum
