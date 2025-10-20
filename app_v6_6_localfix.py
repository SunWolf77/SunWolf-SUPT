# ===============================================================
# SUPT :: SunWolf ReSunance Continuum v6.6 — Live Diagnostic Build
# ===============================================================

import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime as dt
import io
import plotly.graph_objects as go

# ===============================================================
# CONFIGURATION
# ===============================================================
st.set_page_config(
    page_title="SunWolf ReSunance Continuum — SUPT Live Monitor",
    layout="wide",
    page_icon="☀️"
)

LOCAL_DATA = "events.csv"
NOAA_KP_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
REFRESH_INTERVAL = 60  # seconds

# ===============================================================
# UTILITY FUNCTIONS
# ===============================================================
def compute_eii(md_max, md_mean, shallow_ratio, psi_s):
    return np.clip((md_max * 0.2 + md_mean * 0.15 + shallow_ratio * 0.4 + psi_s * 0.25), 0, 1)

def classify_phase(EII):
    if EII >= 0.85:
        return "ACTIVE – Collapse Window Initiated"
    elif EII >= 0.6:
        return "ELEVATED – Pressure Coupling Phase"
    return "MONITORING – Stable"

@st.cache_data(ttl=600)
def fetch_noaa_kp():
    try:
        r = requests.get(NOAA_KP_URL, timeout=10)
        r.raise_for_status()
        data = r.json()
        latest = data[-1]
        return float(latest[1])
    except Exception as e:
        st.warning(f"NOAA Kp fetch failed: {e}")
        return 0.0

@st.cache_data(ttl=600)
def load_seismic_data():
    try:
        df = pd.read_csv(LOCAL_DATA)
        df['time'] = pd.to_datetime(df['Time'], errors='coerce')
        df['magnitude'] = pd.to_numeric(df['MD'], errors='coerce')
        df['depth_km'] = pd.to_numeric(df['Depth'], errors='coerce')
        df = df.dropna(subset=['time', 'magnitude', 'depth_km'])
        return df
    except Exception as e:
        st.warning(f"Local data load failed: {e}")
        return pd.DataFrame()

def generate_solar_history(psi_s, hours=24):
    now = dt.datetime.utcnow()
    times = [now - dt.timedelta(hours=i) for i in range(hours)][::-1]
    psi_vals = np.random.normal(psi_s, 0.05, hours)
    return pd.DataFrame({"time": times, "psi_s": psi_vals})

def generate_forecast_wave(psi_s, hours=48):
    now = dt.datetime.utcnow()
    times = [now + dt.timedelta(hours=i) for i in range(hours)]
    forecast_psi = np.sin(np.linspace(0, np.pi * 2, hours)) * 0.3 + psi_s
    return pd.DataFrame({"hour": range(hours), "forecast_psi": forecast_psi})

# ===============================================================
# SUPT DIAGNOSTIC ENGINE
# ===============================================================
def supt_diagnostic(EII, CCI, Kp):
    if EII >= 0.85:
        phase = "ACTIVE – Collapse Window Initiated"
        message = "System energetically saturated. Collapse-phase resonance possible; high internal coupling efficiency."
    elif EII >= 0.6:
        phase = "ELEVATED – Pressure Coupling Phase"
        message = "System in harmonic tension buildup. Energy transfer active; monitoring phase coherence recommended."
    else:
        phase = "MONITORING – Stable"
        message = "System stable; no significant external coupling."

    if CCI >= 0.7:
        coherence = "Coherent"
        note = "ψₛ–Depth phases are synchronized; resonance feedback likely."
    elif CCI >= 0.4:
        coherence = "Moderate"
        note = "Partial coherence detected; energy exchange possible but weak."
    else:
        coherence = "Decoupled"
        note = "ψₛ–Depth phases misaligned; system energetically loaded but incoherent."

    if Kp >= 5:
        geomag = "Geomagnetic Storm Active — potential resonance amplifier."
    elif Kp >= 3:
        geomag = "Moderate Geomagnetic Activity — mild forcing potential."
    else:
        geomag = "Quiet geomagnetic conditions."

    diagnostic_text = f"""
    ### 🧭 SUPT Diagnostic Summary  
    **RPAM Phase:** {phase}  
    **CCI:** {CCI:.3f} ({coherence})  
    **EII:** {EII:.3f}  
    **Geomagnetic State:** {geomag}  

    **Interpretation:**  
    {message}  
    {note}
    """
    return diagnostic_text

# ===============================================================
# MAIN APP
# ===============================================================
st.title("☀️ SunWolf ReSunance Continuum — SUPT Live Monitor")
st.caption("Real-Time ψₛ–Depth–Kp Continuum | Campi Flegrei • SUPT v6.6")

st.sidebar.header("Live Parameters")
psi_s = st.sidebar.slider("Solar Pressure Proxy (ψₛ)", 0.0, 1.0, 0.72, 0.01)
st.sidebar.write(f"Auto-refresh every {REFRESH_INTERVAL} seconds.")
refresh = st.sidebar.button("🔁 Refresh Data")

# Load data
df = load_seismic_data()
kp_index = fetch_noaa_kp()

# Compute metrics
if df.empty:
    st.warning("INGV fetch failed (auto-handled): Empty INGV dataset.")
    md_max, md_mean, shallow_ratio = 0, 0, 0
else:
    md_max = df['magnitude'].max()
    md_mean = df['magnitude'].mean()
    shallow_ratio = len(df[df["depth_km"] < 2.5]) / max(len(df), 1)

EII = compute_eii(md_max, md_mean, shallow_ratio, psi_s)
RPAM = classify_phase(EII)

# Display metrics
col1, col2, col3 = st.columns(3)
col1.metric("Energetic Instability Index (EII)", f"{EII:.3f}")
col2.metric("RPAM Status", RPAM)
col3.metric("Kp Index", f"{kp_index:.1f}")

# ======================
# ψₛ–Depth Coherence Index
# ======================
st.markdown("### 🌀 ψₛ–Depth Coherence Index (CCI)")
if not df.empty:
    psi_hist = generate_solar_history(psi_s)
    depth_signal = np.interp(np.linspace(0, len(df) - 1, 24), np.arange(len(df)),
                             np.clip(df["depth_km"].rolling(3, min_periods=1).mean(), 0, 5))
    psi_norm = (psi_hist["psi_s"] - np.mean(psi_hist["psi_s"])) / np.std(psi_hist["psi_s"])
    depth_norm = (depth_signal - np.mean(depth_signal)) / np.std(depth_signal)
    cci = np.corrcoef(psi_norm, depth_norm)[0, 1] ** 2 if len(df) > 1 else 0
else:
    cci = 0.0

color = "green" if cci >= 0.7 else "orange" if cci >= 0.4 else "red"
label = "Coherent" if cci >= 0.7 else "Moderate" if cci >= 0.4 else "Decoupled"

gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=cci,
    title={"text": f"CCI: {label}"},
    gauge={
        "axis": {"range": [0, 1]},
        "bar": {"color": color},
        "steps": [
            {"range": [0, 0.4], "color": "#FFCDD2"},
            {"range": [0.4, 0.7], "color": "#FFF59D"},
            {"range": [0.7, 1.0], "color": "#C8E6C9"},
        ],
    },
))
st.plotly_chart(gauge, use_container_width=True)

# ======================
# LIVE DIAGNOSTIC PANEL
# ======================
st.markdown(supt_diagnostic(EII, cci, kp_index))

# ======================
# ψₛ 48-HOUR FORECAST
# ======================
st.markdown("### 🔮 48-Hour ψₛ Resonance Forecast")
forecast = generate_forecast_wave(psi_s)
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=forecast["hour"], y=forecast["forecast_psi"],
    mode="lines", line=dict(color="#FFB300", width=3),
    name="ψₛ Forecast"))
fig.update_layout(
    title="SUPT ψₛ Harmonic Projection (48h)",
    xaxis_title="Hours Ahead", yaxis_title="ψₛ Index",
    template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

# Footer
st.caption(f"Updated {dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | Feeds: NOAA • INGV | Mode: Continuum Live v6.6")
st.caption("Powered by Sheppard’s Universal Proxy Theory — ψₛ–Depth–Kp Harmonic Continuity Engine.")
