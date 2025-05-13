from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich import box
import threading
import time
from datetime import datetime, timedelta
import pymongo
import os
import requests
from collections import defaultdict

# Shared alerts list
shared_alerts = []

def get_attacker_ip():
    try:
        return requests.get("https://api.ipify.org").text
    except:
        return "Unknown IP"

def monitor_changes():
    db = pymongo.MongoClient(os.environ['ENV_DB'])
    change_stream = db.watch([{
        '$match': {
            'operationType': 'update',
            'updateDescription.updatedFields.last_accessed': {'$exists': True}
        }
    }])

    while True:
        for change in change_stream:
            alert = {
                "time": datetime.now(),
                "ip": get_attacker_ip(),
                "collection": change["ns"]["coll"],
                "doc_id": str(change["documentKey"]["_id"]),
                "last_accessed": str(change["updateDescription"]["updatedFields"]["last_accessed"])
            }
            shared_alerts.append(alert)

def generate_activity_graph():
    # Get scans from the last hour
    one_hour_ago = datetime.now() - timedelta(hours=1)
    recent_scans = [alert for alert in shared_alerts if alert["time"] > one_hour_ago]
    
    if not recent_scans:
        return Text("No scan activity in the last hour", style="italic dim")
    
    # Group by 5-minute intervals
    time_buckets = defaultdict(int)
    for scan in recent_scans:
        # Round to nearest 5 minutes
        bucket = scan["time"].replace(minute=scan["time"].minute // 5 * 5, second=0, microsecond=0)
        time_buckets[bucket] += 1
    
    # Create a simple text-based bar chart
    max_count = max(time_buckets.values()) if time_buckets else 1
    graph = Text()
    
    for bucket in sorted(time_buckets.keys()):
        count = time_buckets[bucket]
        bar_length = int(count / max_count * 20)
        graph.append(f"{bucket.strftime('%H:%M')} ", style="cyan")
        graph.append("█" * bar_length, style="red")
        graph.append(f" {count} scans\n")
    
    return graph

def generate_table():
    table = Table(title="🚨 LIVE DATABASE SCANS", border_style="bold red", box=box.SQUARE)
    table.add_column("Timestamp", style="cyan", no_wrap=True)
    table.add_column("IP", style="magenta", no_wrap=True)
    table.add_column("Collection", style="green", no_wrap=True)
    table.add_column("Document ID", style="yellow", no_wrap=True)
    table.add_column("Last Accessed", style="blue", no_wrap=True)
    
    if not shared_alerts:
        # Add a placeholder row when empty
        table.add_row(
            "-", "-", "-", "Waiting for updates...", "-"
        )
    else:
        for alert in shared_alerts[-10:]:  # Show last 10 alerts
            table.add_row(
                alert["time"].strftime("%H:%M:%S"),
                alert["ip"],
                alert["collection"],
                alert["doc_id"][:15] + ("..." if len(alert["doc_id"]) > 15 else ""),
                alert["last_accessed"]
            )
    return table

def generate_layout():
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=12)
    )
    layout["header"].update(
        Panel("🔍 MongoDB Atlas Scan Monitor", style="bold blue")
    )
    layout["main"].update(
        Panel(generate_table(), border_style="red")
    )
    layout["footer"].update(
        Panel(generate_activity_graph(), title="📊 Scan Activity (Last Hour)", border_style="yellow")
    )
    return layout

# Start monitoring thread
threading.Thread(target=monitor_changes, daemon=True).start()

# Display table
console = Console()
with Live(generate_layout(), refresh_per_second=4, screen=True, vertical_overflow="visible") as live:
    while True:
        time.sleep(0.5)
        live.update(generate_layout())
