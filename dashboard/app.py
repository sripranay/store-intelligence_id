import streamlit as st
import requests

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Store Intelligence Dashboard")

st.title("📊 Store Intelligence Dashboard")

store_id = st.text_input("Store ID", "STORE_001")

def get_data(endpoint):
    try:
        url = f"{API}{endpoint}"
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": str(e)}

# METRICS
st.subheader("📈 Metrics")

metrics = get_data(f"/stores/{store_id}/metrics")

if "error" in metrics:
    st.error("API not running (metrics)")
else:
    st.write(f"Visitors: {metrics.get('unique_visitors', 0)}")
    st.write(f"Entries: {metrics.get('total_entries', 0)}")
    st.write(f"Conversion Rate: {metrics.get('conversion_rate', 0)}")

# FUNNEL
st.subheader("🔻 Funnel")

funnel = get_data(f"/stores/{store_id}/funnel")

if "error" in funnel:
    st.error("API not running (funnel)")
else:
    st.json(funnel)

# ANOMALIES
st.subheader("⚠️ Anomalies")

anomalies = get_data(f"/stores/{store_id}/anomalies")

if "error" in anomalies:
    st.error("API not running (anomalies)")
else:
    st.json(anomalies)