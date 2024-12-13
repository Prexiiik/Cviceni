import psutil
import socket
import argparse
import time
import json
from tabulate import tabulate

def get_network_activity():
    connections = psutil.net_connections()
    activity = []

    for conn in connections:
        laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "-"
        raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "-"
        protocol = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
        activity.append({
            "Local Address": laddr,
            "Remote Address": raddr,
            "State": conn.status,
            "Protocol": protocol
        })

    return activity

def filter_activity(activity, ip=None, port=None, state=None):
    filtered = []
    for conn in activity:
        if ip and ip not in conn["Local Address"] and ip not in conn["Remote Address"]:
            continue
        if port and f":{port}" not in conn["Local Address"] and f":{port}" not in conn["Remote Address"]:
            continue
        if state and conn["State"].lower() != state.lower():
            continue
        filtered.append(conn)
    return filtered

def display_activity(activity, output_format):
    if output_format == "json":
        print(json.dumps(activity, indent=4))
    else:
        headers = ["Local Address", "Remote Address", "State", "Protocol"]
        table = [[conn["Local Address"], conn["Remote Address"], conn["State"], conn["Protocol"]] for conn in activity]
        print(tabulate(table, headers=headers, tablefmt="grid"))

def monitor_network(interval, ip=None, port=None, state=None, output_format="table"):
    previous_activity = None
    try:
        while True:
            current_activity = get_network_activity()
            if ip or port or state:
                current_activity = filter_activity(current_activity, ip=ip, port=port, state=state)

            if previous_activity != current_activity:
                print("\nUpdated Network Activity:")
                display_activity(current_activity, output_format)
                previous_activity = current_activity

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor and display network activity.")
    parser.add_argument("--ip", type=str, help="Filter by IP address.")
    parser.add_argument("--port", type=int, help="Filter by port.")
    parser.add_argument("--state", type=str, help="Filter by connection state.")
    parser.add_argument("--interval", type=int, default=5, help="Monitoring interval in seconds.")
    parser.add_argument("--format", type=str, choices=["table", "json"], default="table", help="Output format (table/json).")
    
    args = parser.parse_args()

    monitor_network(interval=args.interval, ip=args.ip, port=args.port, state=args.state, output_format=args.format)
