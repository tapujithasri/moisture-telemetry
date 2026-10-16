import math

def calculate_next_moisture(tick, watering_active, current_history):
    """Computes the next wave value using sine/cosine physics."""
    # Find last moisture reading or use baseline defaults
    last_moisture = current_history[-1]["Moisture (%)"] if current_history else (35 if watering_active else 60)
    
    if watering_active:
        return min(100, last_moisture + int(math.sin(tick) * 5) + 12)
    else:
        return max(0, last_moisture - int(math.cos(tick) * 2) - 3)

def evaluate_system_state(live_reading, dry_threshold, wet_threshold, watering_active):
    """State matrix processing engine."""
    if live_reading <= dry_threshold:
        return "CRITICAL: DRY START", f"- BELOW {dry_threshold}%", "inverse", True
    elif live_reading >= wet_threshold:
        return "CRITICAL: WET STOP", f"+ ABOVE {wet_threshold}%", "normal", False
    else:
        sys_state = "PUMP ACTIVE" if watering_active else "NOMINAL OPERATION"
        metric_delta = "🌊 INCREASING" if watering_active else "🍂 DECREASING"
        return sys_state, metric_delta, "off", watering_active
