import streamlit as st, pandas as pd, requests
from core_engine import compute_metrics

st.set_page_config(page_title="SunWolf-SUPT", layout="wide")
st.title("☀️ SunWolf-SUPT: Volcanic & Geomagnetic Dashboard")

# ===============================================================
# LOAD SEISMIC DATA — Includes Local INGV CSV Fallback
# ===============================================================
@st.cache_data(ttl=600)
def load_seismic_data():
    try:
        df = fetch_ingv_seismic_data()
        if df.empty:
            raise ValueError("Empty INGV dataset")
        st.info("Using live INGV data.")
        return df

    except Exception as e:
        st.warning(f"INGV fetch failed (auto-handled): {e}. Loading local dataset...")
        try:
            # Load local INGV events CSV
            df = pd.read_csv("events.csv")
            df.columns = df.columns.str.strip()

            # Normalize key fields for SUPT processing
            if "time" not in df.columns:
                if "Time" in df.columns:
                    df["time"] = pd.to_datetime(df["Time"], errors="coerce")
                else:
                    df["time"] = pd.to_datetime(df.iloc[:, 0], errors="coerce")

            df["magnitude"] = pd.to_numeric(df.get("MD", df.get("Magnitude", np.nan)), errors="coerce")
            df["depth_km"] = pd.to_numeric(df.get("Depth", df.get("Depth/Km", np.nan)), errors="coerce")

            # Filter last 7 days only
            df = df.dropna(subset=["time", "magnitude", "depth_km"])
            df = df[df["time"] >= (dt.datetime.utcnow() - dt.timedelta(days=7))]

            st.success(f"Loaded local INGV dataset ({len(df)} events).")
            return df

        except Exception as err:
            st.error(f"Local INGV fallback failed: {err}")
            return generate_synthetic_seismic_data()

@st.cache_data(ttl=10)
def fetch_kp():
    try:
        data = requests.get(
            "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json",
            timeout=5).json()
        return float(data[-1][1])
    except Exception:
        return 3.0

# Load data
cf_df   = fetch_ingv(40.79,40.84,14.10,14.15)
vulc_df = fetch_ingv(38.38,38.47,14.90,15.05)
kp = fetch_kp()

metrics = compute_metrics(cf_df, vulc_df, kp)

st.metric("Geomagnetic KP", kp)
st.metric("EII", metrics["EII"])
st.metric("RPAM Status", metrics["RPAM"])
st.metric("ψₛ-Scale", metrics["psi_scale"])

st.caption("Campi Flegrei and Vulcano data auto-refresh every 2 min.")
