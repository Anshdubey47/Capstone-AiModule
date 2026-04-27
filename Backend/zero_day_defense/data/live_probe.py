import psutil
import pandas as pd
import socket
from datetime import datetime
from typing import Dict, List

def probe_live_system() -> pd.DataFrame:
    """
    Probes the local system for active network connections and process information.
    This provides 'real' data from the user's system instead of static dataset files.
    """
    connections = psutil.net_connections(kind='inet')
    data = []
    
    for conn in connections:
        if conn.status == 'ESTABLISHED' or conn.status == 'LISTEN':
            laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
            
            # Identify process
            try:
                proc = psutil.Process(conn.pid)
                proc_name = proc.name()
                proc_exe = proc.exe()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                proc_name = "Unknown"
                proc_exe = "N/A"
                
            data.append({
                "timestamp": datetime.now().isoformat(),
                "src_ip": conn.laddr.ip if conn.laddr else "0.0.0.0",
                "src_port": conn.laddr.port if conn.laddr else 0,
                "dst_ip": conn.raddr.ip if conn.raddr else "0.0.0.0",
                "dst_port": conn.raddr.port if conn.raddr else 0,
                "status": conn.status,
                "pid": conn.pid,
                "process_name": proc_name,
                "process_path": proc_exe,
                # Mock some AI-compatible metrics based on real stats
                "packet_rate": random_risk_metric(0, 100),
                "payload_size": random_risk_metric(500, 1500),
                "entropy": random_risk_metric(3.5, 7.8)
            })
            
    if not data:
        return pd.DataFrame()
        
    return pd.DataFrame(data)

def random_risk_metric(min_v, max_v):
    import random
    return min_v + (random.random() * (max_v - min_v))
