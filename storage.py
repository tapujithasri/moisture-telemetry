import os
import time
import pandas as pd

CSV_FILE = "telemetry_log.csv"

def init_dataframe():
    """Reads or sets up the historical baseline data frame safely."""
    if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=["Timestamp", "Moisture (%)", "State", "Dry_Limit_Set", "Wet_Limit_Set"])

def append_telemetry_row(live_reading, sys_state, dry_threshold, wet_threshold):
    """Commits a single row transaction to the local disk file."""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    new_data = {
        "Timestamp": timestamp, 
        "Moisture (%)": live_reading, 
        "State": sys_state,
        "Dry_Limit_Set": dry_threshold,
        "Wet_Limit_Set": wet_threshold
    }
    new_row_df = pd.DataFrame([new_data])
    if not os.path.exists(CSV_FILE):
        new_row_df.to_csv(CSV_FILE, index=False)
    else:
        new_row_df.to_csv(CSV_FILE, mode='a', header=False, index=False)

def update_history_buffer(history_list, live_reading):
    """Appends data and trims memory length to prevent lag."""
    history_list.append({"System Time": time.strftime('%H:%M:%S'), "Moisture (%)": live_reading})
    if len(history_list) > 30:
        history_list.pop(0)
    return history_list

def purge_all_data():
    """Wipes the CSV file from disk entirely."""
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
