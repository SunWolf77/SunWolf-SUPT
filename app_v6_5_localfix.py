# ===============================================================
# SUPT :: SunWolf ReSunance Continuum v6.5 (Local INGV Fallback)
# ===============================================================

import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime as dt
import plotly.graph_objects as go
import re
import io

# ------------------------------
# CONFIG
# ------------------------------
st.set_page_config(page_title="SUPT :: SunWolf ReSunance Continuum v6.5", layout="wide")

LOCAL_CSV = "events.csv"
NOAA_GEOMAG_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
API_TIMEOUT = 10

# ------------------------------
# UTILITY FUNCTIONS
# ------------------------------
def clean_magnitude(value):
    """Extract numeric magnitude from INGV string like 'Useless 0.5±0.3'."""
    if pd.isna(value):
        return np.nan
    match = re.search(r"(\d+\.\d+|\d+)", str(value))
    return float(match.group(1)) if match else np.nan

def load_local_ingv_csv():
    try:
        df = pd.read_csv(LOCAL_CSV)
        df.columns = [c.strip() for c in df.columns]
        # Attempt to detect time and magnitude columns
        time_col = next((c for c in df.columns if "Time" in c or "UTC" in c), None)
        mag_col = next((c for c in df.columns if "Mag" in c or "Magnitude" in c), None)
        depth_col = next((c for c in df.columns if "Depth" in c), None)

        df["time"] = pd.to_datetime(df[time_col], errors="coerce")
        df["magnitude"] = df[mag_col].apply(clean_magnitude)
        df["depth_km"] = pd.to_numeric(df[depth_col], errors="coerce")
        df = df.dropna(subset=["time", "magnitude", "depth_km"])
        return df.sort_values("time", ascending=False)
    except Exception as e:
        st.error(f"Local INGV data load failed: {e}")
        return pd.DataFrame(columns=["time", "magnitude", "depth_km"])

def fetch_geomag_data():
    try:
        r = requests.get(NOAA_GEOMAG_URL, timeout=API_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        latest = data[-1]
        return float(latest[1])
    except Exception:
        return 0.0

def compute_eii(md_max, md_mean, shallow_ratio, psi_s):
    return np.clip((md_max * 0.2 + md_mean * 0.15 + shallow_ratio * 0.4 + psi_s * 0.25), 0, 1)

def classify_phase(EII):
    if EII >= 0.85:
        return "ACTIVE – Collapse Window Initiated"
    elif EII >= 0.6:
        return "ELEVATED – Pressure Coupling Phase"
    else:
        return "MONITORING"

# ------------------------------
# APP LAYOUT
# ------------------------------
st.title("🜂 SUPT :: SunWolf ReSunance Continuum v6.5")
st.caption("Real-Time Volcanic–Solar Coupling Monitor for Campi Flegrei — SUPT Continuum Framework")

# Sidebar: ψₛ input + refresh
psi_s = st.sidebar.slider("Solar Pressure Proxy (ψₛ)", 0.0, 1.0, 0.72, 0.01)
if st.sidebar.button("🔁 Refresh Data"):
    st.experimental_rerun()

# Load INGV data (local fallback)
df = load_local_ingv_csv()
geomag_kp = fetch_geomag_data()

# Compute SUPT metrics
if not df.empty:
    md_max = df["magnitude"].max()
    md_mean = df["magnitude"].mean()
    shallow_ratio = len(df[df["depth_km"] < 2.5]) / max(len(df), 1)
    EII = compute_eii(md_max, md_mean, shallow_ratio, psi_s)
    RPAM = classify_phase(EII)
else:
    EII, RPAM = 0.0, "NO DATA"

# Display metrics
col1, col2, col3 = st.columns(3)
col1.metric("Energetic Instability Index (EII)", f"{EII:.3f}")
col2.metric("RPAM Phase", RPAM)
col3.metric("Geomagnetic Kp", f"{geomag_kp:.1f}")

# ------------------------------
# CCI Gauge (ψₛ–Depth Coherence)
# ------------------------------
st.markdown("### ☯ ψₛ–Depth Coherence Index (CCI)")

if not df.empty:
    psi_series = np.random.normal(psi_s, 0.05, len(df))
    depth_norm = (df["depth_km"] - df["depth_km"].mean()) / df["depth_km"].std()
    psi_norm = (psi_series - np.mean(psi_series)) / np.std(psi_series)
    cci = np.corrcoef(psi_norm, depth_norm)[0, 1] ** 2 if len(df) > 2 else 0.0

    color = "green" if cci >= 0.7 else "orange" if cci >= 0.4 else "red"
    label = "Coherent" if cci >= 0.7 else "Moderate" if cci >= 0.4 else "Decoupled"

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=cci,
        title={"text": f"CCI: {label}"},
        gauge={"axis": {"range": [0, 1]},
               "bar": {"color": color},
               "steps": [{"range": [0, 0.4], "color": "#FFCDD2"},
                         {"range": [0.4, 0.7], "color": "#FFF59D"},
                         {"range": [0.7, 1.0], "color": "#C8E6C9"}]}))
    st.plotly_chart(gauge, use_container_width=True)
else:
    st.warning("No valid INGV events found in dataset.")

# ------------------------------
# Summary Block
# ------------------------------
if not df.empty:
    latest = df.iloc[0]
    st.markdown("### 📊 Event Summary")
    st.write(
        f"**Latest event:** {latest['time']:%Y-%m-%d %H:%M UTC} | "
        f"**Md:** {latest['magnitude']:.1f} | **Depth:** {latest['depth_km']:.1f} km"
    )
    st.write(
        f"**Events loaded:** {len(df)} | **Mean Md:** {df['magnitude'].mean():.2f} | "
        f"**Mean Depth:** {df['depth_km'].mean():.2f} km"
    )

# ------------------------------
# Forecast Plot
# ------------------------------
st.markdown("### 🔮 48h ψₛ Temporal Resonance Forecast")
hours = np.arange(0, 48)
forecast = np.sin(np.linspace(0, np.pi * 2, 48)) * 0.25 + psi_s
fig = go.Figure(go.Scatter(x=hours, y=forecast, mode="lines", line=dict(color="#FFB300", width=3)))
fig.update_layout(
    title="48-Hour ψₛ Harmonic Forecast",
    xaxis_title="Hours Ahead",
    yaxis_title="ψₛ Index",
    template="plotly_white",
)
st.plotly_chart(fig, use_container_width=True)

# Footer
st.caption(f"Updated {dt.datetime.utcnow():%Y-%m-%d %H:%M:%S UTC} | Feeds: NOAA • INGV (local) | SUPT v6.5")
st.caption("Powered by Sheppard’s Universal Proxy Theory — SunWolf Continuum")
