import streamlit as st, pandas as pd, requests
from core_engine import compute_metrics

st.set_page_config(page_title="SunWolf-SUPT", layout="wide")
st.title("☀️ SunWolf-SUPT: Volcanic & Geomagnetic Dashboard")

@st.cache_data(ttl=120)
def fetch_ingv(latmin,latmax,lonmin,lonmax):
    try:
        url = (f"https://webservices.ingv.it/fdsnws/event/1/query?"
               f"starttime=2025-10-01&endtime=now&latmin={latmin}&latmax={latmax}"
               f"&lonmin={lonmin}&lonmax={lonmax}&format=text")
        df = pd.read_csv(url, sep="|", comment="#")
        df.columns = [c.strip().lower() for c in df.columns]
        return df[["time","latitude","longitude","depth","mag"]].rename(columns={"mag":"md"})
    except Exception:
        return pd.read_csv("data/events_CF.csv")

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
