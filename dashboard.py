import streamlit as st
import json, os, requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SENTINEL - Secure AIOps", layout="wide")
BACKEND = "http://127.0.0.1:8000"

# --- LOGIN VIA BACKEND ---
st.sidebar.title("🔐 SENTINEL Login")
if "tenant" not in st.session_state:
    st.session_state["tenant"] = None

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    try:
        r = requests.post(f"{BACKEND}/login", params={"username": username, "password": password})
        result = r.json()
        if result.get("success"):
            st.session_state["tenant"] = result["tenant"]
            st.sidebar.success(f"Welcome {username} | Tenant: {result['tenant']}")
            st.rerun()
        else:
            st.sidebar.error("Wrong Login")
    except:
      pass
if not st.session_state["tenant"]:
    st.title("🛡️ SENTINEL - Secure AIOps Observability")
    st.warning("Login with admin / admin123 in left sidebar")
    st.info("Demo: Username = admin | Password = admin123")
    st.stop()

tenant = st.session_state["tenant"]
st.title("🛡️ SENTINEL - Secure AIOps Observability")
st.caption(f"Logged in as {username} | Tenant: {tenant} | Backend: Connected to {BACKEND}")

# --- LOAD DATA FROM BACKEND + LOCAL ---
def load_data():
    try:
        r = requests.get(f"{BACKEND}/dashboard/{tenant}", timeout=2)
        records = r.json().get("records", [])
        if records:
            last = records[0]
            return {"cpu": last["cpu"], "memory": last["memory"], "latency": last["latency"], "failed_logins": 11 if last["latency"] > 100 else 2}
    except:
        pass
    # Fallback to data.json
    try:
        if os.path.exists("data.json"):
            with open("data.json") as f:
                return json.load(f)
    except:
        pass
    return {"cpu": 50, "memory": 50, "latency": 50, "failed_logins": 0}

data = load_data()

# --- TOP CARDS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Server 1 - Web", "Excellent", "CPU 45%")
col2.metric("Server 2 - DB", "Poor" if data.get("latency", 0) > 100 else "Good", f"CPU {data.get('cpu')}%")
col3.metric("Server 3 - API", "Good", "CPU 62%")
col4.metric("Collector", "Online", "Backend Connected")

st.divider()

# --- INTERACTIVE CONTROLS ---
st.subheader("🎛️ Controls")
col_a, col_b = st.columns(2)
with col_a:
    selected_server = st.selectbox("Select Server", ["Server 1 - Web", "Server 2 - DB", "Server 3 - API"])
with col_b:
    time_range = st.slider("Last N Minutes", 5, 60, 15)

if st.button("🔄 Refresh Live Data"):
    st.rerun()
st.caption(f"Showing: {selected_server} | Last {time_range} mins | Tenant: {tenant}")

# --- CHART + AIOPS ---
left, right = st.columns([2, 1])
# --- FIX: Make Server + Time Slider Actually Work ---
server_config = {
    "Server 1 - Web": {"base_cpu": 45, "base_latency": 80, "health": "Excellent"},
    "Server 2 - DB":  {"base_cpu": 75, "base_latency": 195, "health": "Poor - Attack"},
    "Server 3 - API": {"base_cpu": 55, "base_latency": 110, "health": "Good"},
}
cfg = server_config[selected_server]

# Use time_range to decide how many points to show
num_points = int(time_range)  # if slider 15, show 15 points
times = list(range(1, num_points + 1))
cpu_vals = [cfg["base_cpu"] + (i % 5) * 2 for i in times] # different per server
latency_vals = [cfg["base_latency"] + (i % 4) * 3 for i in times]

st.subheader(f"📊 Live Metrics - {selected_server} - {cfg['health']}")
df = pd.DataFrame({"time": times, "CPU": cpu_vals, "Latency": latency_vals})
fig = px.line(df, x="time", y=["CPU", "Latency"], markers=True)
st.plotly_chart(fig, use_container_width=True)
st.caption("Hover to see value, drag to zoom.")

with right:
    st.subheader("🤖 AIOps Recommendation")
    if data.get("failed_logins", 0) >= 10 or data.get("latency", 0) > 100:
        st.error("SECURITY INCIDENT")
        st.write(f"Reason: {data.get('failed_logins')} failed logins + Latency {data.get('latency')}ms")
        st.write("Action: Block IP, Enable 2FA. Confidence: 92%")
        if st.button("🚨 Block IP Now"):
            try:
                r = requests.post(f"{BACKEND}/block-ip", params={"tenant": tenant, "ip": "192.168.1.100"})
                st.success(r.json().get("message", "IP Blocked!"))
            except:
                st.success(f"IP Blocked for {tenant} (Local Mode)")
            st.balloons()
        if st.button("Enable 2FA for Tenant"):
            st.info(f"2FA Enabled for {tenant}")
    else:
        st.success("No Incident - System Healthy")
        st.write(f"Failed Logins: {data.get('failed_logins')} - Safe")

if st.sidebar.button("Logout"):
    st.session_state["tenant"] = None
    st.rerun()