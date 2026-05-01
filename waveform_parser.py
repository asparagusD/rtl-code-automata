import os
import json
from pyDigitalWaveTools.vcd.parser import VcdParser
from rich.console import Console

console = Console()

def extract_signals_recursive(scope, prefix=""):
    """
    Recursively extract signals from a pyDigitalWaveTools VcdParser scope.
    """
    signals = {}
    if not hasattr(scope, 'children'):
        return signals
        
    for name, child in scope.children.items():
        if hasattr(child, 'children') and getattr(child, 'children'):
            new_prefix = f"{prefix}{name}."
            signals.update(extract_signals_recursive(child, new_prefix))
        else:
            signals[f"{prefix}{name}"] = child
    return signals

def parse_vcd_and_detect_anomalies(vcd_path):
    """
    Parses a VCD file and generates a structured summary with basic anomaly detection.
    """
    if not os.path.exists(vcd_path):
        return {"error": f"File not found: {vcd_path}"}
        
    try:
        parser = VcdParser()
        with open(vcd_path, "r") as f:
            parser.parse(f)
        
        raw_signals = extract_signals_recursive(parser.scope)
        summary = {"signals": {}}
        
        # Determine average clock period
        max_toggles = 0
        clock_signal_name = None
        for name, sig in raw_signals.items():
            if getattr(sig, 'data', None):
                if len(sig.data) > max_toggles:
                    max_toggles = len(sig.data)
                    clock_signal_name = name
                    
        clock_period = 10.0
        if max_toggles < 10:
            console.print("[bold yellow]⚠ Warning: No signal toggled more than 10 times. Assuming default 10ns clock period for glitch detection.[/bold yellow]")
        else:
            # Calculate median time delta between transitions for the most frequent signal
            sig_data = raw_signals[clock_signal_name].data
            deltas = []
            for i in range(1, len(sig_data)):
                deltas.append(sig_data[i][0] - sig_data[i-1][0])
            deltas.sort()
            median_delta = deltas[len(deltas) // 2]
            clock_period = float(median_delta * 2)

        for name, sig in raw_signals.items():
            transitions = []
            anomalies = []
            
            is_reset = any(r in name.lower() for r in ['rst', 'reset'])
            width = getattr(sig, 'width', 1)
            
            if not getattr(sig, 'data', None):
                continue
                
            has_active_reset = False
            last_time = None
            
            x_at_t0 = False
            resolved_time = None
            mid_sim_x = []
            
            for time, val in sig.data:
                val_str = str(val)
                if val_str.startswith('b'):
                    val_str = val_str[1:]
                
                transitions.append({"time": time, "value": val_str})
                
                is_xz = 'x' in val_str.lower() or 'z' in val_str.lower()
                
                if is_xz:
                    if time == 0:
                        x_at_t0 = True
                    else:
                        mid_sim_x.append(time)
                else:
                    if x_at_t0 and resolved_time is None:
                        resolved_time = time
                        
                # Anomaly 3: Glitches (faster than half clock period)
                if last_time is not None:
                    delta = time - last_time
                    if delta > 0 and delta < (clock_period / 4.0):
                        anomalies.append(f"Glitch detected at t={time} (delta={delta})")
                
                last_time = time
                
                if is_reset and val_str in ['1', '0']:
                    has_active_reset = True
                    
            if x_at_t0:
                if resolved_time is not None and resolved_time <= 3 * clock_period:
                    anomalies.append("INFO: X at t=0 is expected initial state for reg — resolves correctly after reset")
                else:
                    anomalies.append("CRITICAL: X/Z state at t=0 never resolves or resolves too late")
                    
            for t in mid_sim_x:
                anomalies.append(f"CRITICAL: X/Z state at t={t}")
                    
            # Anomaly 2: Stuck signals
            if len(transitions) <= 1:
                anomalies.append("Signal appears stuck (no transitions)")
                
            # Anomaly 4: Reset never asserted
            if is_reset and not has_active_reset:
                anomalies.append("Reset signal never transitioned")
                
            if width == 1 and transitions and len(transitions[0]['value']) > 1:
                width = len(transitions[0]['value'])
                
            summary["signals"][name] = {
                "name": name,
                "width": width,
                "transition_count": len(transitions),
                "anomalies": anomalies,
                "_raw_transitions": transitions 
            }
            
        return summary
    except Exception as e:
        return {"error": f"Failed to parse VCD: {str(e)}"}

def get_waveform_summary(vcd_path: str) -> str:
    """
    Returns a high-level summary of the VCD file including identified anomalies.
    """
    parsed = parse_vcd_and_detect_anomalies(vcd_path)
    if "error" in parsed:
        return parsed["error"]
        
    output = [f"Waveform Summary for {vcd_path}:"]
    for sig_name, data in parsed.get("signals", {}).items():
        anoms = ", ".join(data["anomalies"]) if data["anomalies"] else "None"
        output.append(f"- {sig_name} (width: {data['width']}): {data['transition_count']} transitions. Anomalies: {anoms}")
        
    return "\n".join(output)

def get_signal_transitions(vcd_path: str, signal_name: str) -> str:
    """
    Returns the detailed transition history for a specific signal.
    """
    parsed = parse_vcd_and_detect_anomalies(vcd_path)
    if "error" in parsed:
        return parsed["error"]
        
    signals = parsed.get("signals", {})
    if signal_name not in signals:
        matches = [s for s in signals.keys() if signal_name in s]
        if len(matches) == 1:
            signal_name = matches[0]
        elif len(matches) > 1:
            return f"Error: Multiple signals match '{signal_name}': {', '.join(matches)}"
        else:
            return f"Error: Signal '{signal_name}' not found."
            
    data = signals[signal_name]
    output = [f"Transitions for {signal_name}:"]
    for t in data["_raw_transitions"]:
        output.append(f"  t={t['time']}: {t['value']}")
        
    return "\n".join(output)
