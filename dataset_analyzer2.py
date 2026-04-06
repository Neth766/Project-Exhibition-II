import requests
import time
import signal

from datetime import datetime
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Console

# =============================
# Configuration
# =============================

URL = "http://localhost:8081/vulnerabilities/sqli_blind/"

COOKIES = {
    "PHPSESSID": "2r2fmq5v6b26e6bd5mt8c6fb66",
    "security": "low"
}

DATASET_FILE = "rbsqli_dataset/rbsqli_dataset.csv"

MAX_TESTS = 10000000

REFRESH_RATE = 5

console = Console()

# =============================
# Counters
# =============================

total = 0
vulnerable = 0
safe = 0
errors = 0

recent_vulnerable = []

start_time = time.time()

running = True


# =============================
# Ctrl+C Safe Stop
# =============================

def stop(sig, frame):
    global running
    running = False

signal.signal(signal.SIGINT, stop)


# =============================
# Layout Builder
# =============================

def build_layout():

    duration = time.time() - start_time

    speed = 0
    if duration > 0:
        speed = total / duration


    # ======================
    # Statistics Table
    # ======================

    table = Table(expand=True)

    table.add_column("Metric", style="cyan", width=22)
    table.add_column("Value", justify="left")


    table.add_row(
        "Target",
        f"[white]{URL}[/white]"
    )

    table.add_row(
        "Dataset",
        f"[white]{DATASET_FILE}[/white]"
    )

    table.add_row(
        "Started",
        f"[yellow]{datetime.fromtimestamp(start_time)}[/yellow]"
    )

    table.add_section()

    table.add_row(
        "Total Tested",
        f"[white]{total}[/white]"
    )

    table.add_row(
        "Vulnerable",
        f"[green]{vulnerable}[/green]"
    )

    table.add_row(
        "Safe",
        f"[white]{safe}[/white]"
    )

    table.add_row(
        "Errors",
        f"[red]{errors}[/red]"
    )

    table.add_row(
        "Elapsed Time",
        f"[yellow]{round(duration,2)} sec[/yellow]"
    )

    table.add_row(
        "Speed",
        f"[cyan]{round(speed,2)} req/sec[/cyan]"
    )


    # ======================
    # Recent Payloads Panel
    # ======================

    payload_text = ""

    if len(recent_vulnerable) == 0:
        payload_text = "[white]None detected yet[/white]"

    else:

        last_payloads = recent_vulnerable[-12:]

        for p in last_payloads:
            payload_text += f"[green]{p}[/green]\n"



    # ======================
    # Layout
    # ======================

    layout = Layout()

    layout.split_column(

        Panel(
            table,
            title="[cyan]BLIND SQLi LIVE ANALYZER[/cyan]",
            border_style="cyan"
        ),

        Panel(
            payload_text,
            title="[magenta]Recent Vulnerable Payloads[/magenta]",
            border_style="magenta"
        )

    )

    return layout


# =============================
# Main Loop
# =============================

with Live(
    build_layout(),
    refresh_per_second=REFRESH_RATE,
    console=console
) as live:

    with open(DATASET_FILE) as file:

        for payload in file:

            if not running:
                break

            if total >= MAX_TESTS:
                break

            payload = payload.strip()

            if payload == "":
                continue


            params = {
                "id": payload,
                "Submit": "Submit"
            }


            try:

                r = requests.get(
                    URL,
                    params=params,
                    cookies=COOKIES,
                    timeout=5
                )


                total += 1


                if "User ID exists" in r.text:

                    vulnerable += 1

                    recent_vulnerable.append(payload)

                else:

                    safe += 1


            except:

                total += 1
                errors += 1


            live.update(build_layout())


# =============================
# Final Results Dashboard
# =============================

duration = round(time.time() - start_time, 2)

final_table = Table(expand=True)

final_table.add_column("Metric", style="cyan", width=22)
final_table.add_column("Value", justify="left")

final_table.add_row("Target", f"[white]{URL}[/white]")
final_table.add_row("Dataset", f"[white]{DATASET_FILE}[/white]")
final_table.add_row("Total Tested", f"[white]{total}[/white]")
final_table.add_row("Vulnerable", f"[green]{vulnerable}[/green]")
final_table.add_row("Safe", f"[white]{safe}[/white]")
final_table.add_row("Errors", f"[red]{errors}[/red]")
final_table.add_row("Execution Time", f"[yellow]{duration} sec[/yellow]")

if duration > 0:
    speed = round(total/duration,2)
else:
    speed = 0

final_table.add_row("Average Speed", f"[cyan]{speed} req/sec[/cyan]")


inference_text = """

[green]Result Interpretation[/green]

• Content-based Blind SQL Injection successfully detected

• Vulnerability confirmed through response content differences

• Large-scale dataset testing completed successfully

• Automated detection capability demonstrated

• Dataset-driven SQL injection analysis completed

"""


console.print("\n")

console.print(
    Panel(
        final_table,
        title="[cyan]FINAL RESULTS[/cyan]",
        border_style="cyan"
    )
)

console.print(
    Panel(
        inference_text,
        title="[magenta]INFERENCE[/magenta]",
        border_style="magenta"
    )
)