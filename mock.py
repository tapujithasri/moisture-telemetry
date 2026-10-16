import streamlit as st
import pandas as pd
import time
import storage
import simulation

st.set_page_config(page_title="Telemetry Core - Custom Thresholds", layout="wide")

# Custom UI Styles
st.markdown("""
    <style>
    .telemetry-title { text-align: center; font-family: 'Courier New', monospace; font-weight: bold; color: #00FF66; }
    </style>
    <h1 class='telemetry-title'>🛰️ TELEMETRY SYSTEM CORE (MODULAR)</h1>
    """, unsafe_allow_html=True)

# 1. State Initializer
if "history" not in st.session_state:
    st.session_state.history = []
if "sim_tick" not in st.session_state:
    st.session_state.sim_tick = 0
if "watering_active" not in st.session_state:
    st.session_state.watering_active = False

# 2. Sidebar Control panel
with st.sidebar:
    st.header("🎮 System Operations")
    run_simulation = st.toggle("🔌 Activate Telemetry Stream", value=False)
    
    if st.button("🗑️ Clear Log & Reset History", type="primary"):
        storage.purge_all_data()
        st.session_state.history = []
        st.session_state.sim_tick = 0
        st.session_state.watering_active = False
        st.toast("Telemetry data completely wiped!", icon="🔥")
        st.rerun()

    st.markdown("---")
    st.header("⚙️ Threshold Controls")
    dry_threshold = st.slider("⚠️ Dry Start Threshold (%)", 5, 40, 20)
    wet_threshold = st.slider("🛑 Wet Stop Threshold (%)", 60, 95, 80)
    
    st.markdown("---")
    st.header("💾 Storage Manager")
    download_spot = st.empty()

# 3. UI Content Matrix
alert_banner = st.empty()
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📊 Current Node")
    metric_spot = st.empty()
with col2:
    st.subheader("⚡ System Diagnostics")
    status_spot = st.empty()
with col3:
    st.subheader("📈 Real-Time Stream Timeline")
    chart_spot = st.empty()

st.subheader("📋 Live Log Terminal (Last 10 Accumulated Rows)")
table_spot = st.empty()

# --- RUN ENGINE STEP ---
all_data_df = storage.init_dataframe()

if run_simulation:
    # 🔁 Core Pipeline Iteration step
    st.session_state.sim_tick += 1
    
    # Calculate values using simulation module
    live_reading = simulation.calculate_next_moisture(
        st.session_state.sim_tick, st.session_state.watering_active, st.session_state.history
    )
    
    sys_state, metric_delta, color_mode, st.session_state.watering_active = simulation.evaluate_system_state(
        live_reading, dry_threshold, wet_threshold, st.session_state.watering_active
    )
    
    # Alert banner styling updates
    if "DRY" in sys_state:
        alert_banner.error(f"🚨 STATE: [{sys_state}] - Soil below safe limit ({dry_threshold}%). Pump ON.")
    elif "WET" in sys_state:
        alert_banner.warning(f"🛑 STATE: [{sys_state}] - Soil reached ceiling boundary ({wet_threshold}%). Pump OFF.")
    else:
        alert_banner.success(f"✅ TELEMETRY LINK ACTIVE: [{sys_state}]")
        
    # Commit changes using storage module
    storage.append_telemetry_row(live_reading, sys_state, dry_threshold, wet_threshold)
    st.session_state.history = storage.update_history_buffer(st.session_state.history, live_reading)
    
    # Reload fresh local table rows
    all_data_df = storage.init_dataframe()
    
else:
    # ⏸️ Handle Engine when Idle
    alert_banner.info("⏸️ TELEMETRY SYSTEM IDLE: Flip the sidebar toggle to stream real-time data.")
    live_reading = st.session_state.history[-1]["Moisture (%)"] if st.session_state.history else 0
    sys_state = "IDLE / SUSPENDED"
    metric_delta = "🚫 PAUSED"
    color_mode = "off"

# 4. Rendering Phase
total_rows = len(all_data_df)
last_10_df = all_data_df.tail(10).iloc[::-1] if not all_data_df.empty else all_data_df
df_chart = pd.DataFrame(st.session_state.history)

metric_spot.metric(label="MOCK_SENSOR_NODE_01", value=f"{live_reading} %", delta=metric_delta, delta_color=color_mode)

status_spot.code(f"""
Telemetry Mode : MOCK_SIMULATOR
Active State   : {sys_state}
Dry Trigger Set: {dry_threshold}%
Wet Trigger Set: {wet_threshold}%
Total Database : {total_rows} rows saved
""", language="yaml")

if not df_chart.empty:
    chart_spot.line_chart(df_chart.set_index("System Time"), height=230)
else:
    chart_spot.info("No timeline data loaded.")

table_spot.dataframe(last_10_df, use_container_width=True)

# Generate Download Links
if total_rows > 0:
    csv_data = all_data_df.to_csv(index=False).encode('utf-8')
    download_spot.download_button(
        label="📥 Download Complete CSV Log",
        data=csv_data,
        file_name=f"telemetry_export_{time.strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# 🔁 Stream UI controller refresh frequency without blocking the thread
if run_simulation:
    time.sleep(1.0)
    st.rerun()
