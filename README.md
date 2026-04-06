# Blind SQL Injection Project (DVWA + SQLMap + Nikto)

## Project Overview
This project demonstrates how to test a deliberately vulnerable web application (DVWA) for SQL Injection vulnerabilities using:

- Custom Python scripts (`blind_sqli.py`, `dataset_analyzer.py`, `dataset_analyzer2.py`)
- `SQLMap` for automated SQL injection detection
- `Nikto` for web server and web-layer vulnerability scanning

The goal is educational: understand how blind SQL injection works, how scanners detect it, and how to interpret scan reports.

## Project Structure

```text
blindqli/
|-- blind_sqli.py
|-- main.py
|-- dataset_analyzer.py
|-- dataset_analyzer2.py
|-- core/
|   |-- http_engine.py
|   |-- diff_engine.py
|   `-- payloads.py
|-- sqlmap_output/
|   `-- localhost/
|       |-- log
|       |-- session.sqlite
|       `-- target.txt
|-- results.txt
`-- README.md
```

## High-Level Workflow

```text
[Browser / Scripts / SQLMap / Nikto]
                |
                v
      [DVWA (Apache + PHP)]
                |
                v
        [MySQL / MariaDB DB]
```

1. DVWA receives user input from query parameters.
2. Vulnerable SQL query executes in the database.
3. Tools observe changes in response body, timing, and server behavior.
4. Results are stored and analyzed.

---

## What is DVWA?
`DVWA` (Damn Vulnerable Web Application) is an intentionally insecure web app used for cybersecurity practice.

### Why DVWA is useful
- Safe environment for learning common web vulnerabilities.
- Includes multiple vulnerability categories and security levels (`low`, `medium`, `high`).
- Reproduces real attack patterns in a controlled lab.

### How DVWA simulates web vulnerabilities
- It contains insecure input handling and poor query construction.
- At low security level, input is not sanitized enough, making SQL injection possible.
- This helps students observe both exploitation and detection workflows safely.

---

## SQL Injection (SQLi) Basics
SQL Injection happens when user input is inserted into SQL queries without proper validation or parameterization.

### 1) Boolean-Based Blind SQL Injection
The application does not show DB errors directly.
Instead, we infer true/false conditions from response differences.

Example idea:

- True condition: `id=1' AND 1=1 #`
- False condition: `id=1' AND 1=2 #`

If page output changes, we know injection is working.

### 2) Time-Based Blind SQL Injection
If visible content does not change, timing can still reveal truth values.

Example idea:

- `id=1' AND SLEEP(5) #`

If response is delayed by about 5 seconds, condition likely executed in DB.

### 3) Content-Based SQL Injection
This project also demonstrates content-length/content-text comparison.

In `blind_sqli.py`, payloads are sent and response length is compared to a known "true" baseline to extract database name characters.

---

## Step-by-Step SQLMap Usage

### Step 1: Get `PHPSESSID` Cookie
You need an authenticated DVWA session.

1. Open DVWA in browser and log in.
2. Open DevTools -> Application/Storage -> Cookies.
3. Copy `PHPSESSID` value.
4. Ensure security level cookie is set to `security=low`.

Example cookie header format:

```bash
PHPSESSID=your_session_value; security=low
```

### Step 2: Run SQLMap (Required Example Command)

```bash
sqlmap -u "URL" --cookie="PHPSESSID=value; security=low" --batch --output-dir=sqlmap_output
```

Practical DVWA example:

```bash
sqlmap -u "http://localhost:8081/vulnerabilities/sqli_blind/?id=1&Submit=Submit" --cookie="PHPSESSID=YOUR_VALUE; security=low" --batch --output-dir=sqlmap_output
```

### Step 3: How SQLMap Discovers Injection Points
SQLMap typically does this internally:

1. Sends baseline request.
2. Sends crafted boolean payloads and compares response behavior.
3. Sends time-based payloads (e.g., `SLEEP`) and checks response delays.
4. Identifies DBMS fingerprints and confirms injectable parameter.

From this project logs (`sqlmap_output/localhost/log`), SQLMap found:

- Injectable parameter: `id` (GET)
- Boolean-based blind SQLi
- Time-based blind SQLi
- Backend DBMS: MySQL/MariaDB

### Step 4: How SQLMap Produces JSON Output
SQLMap CLI mainly stores output in:

- Text logs
- Session SQLite database

For JSON responses, use `sqlmapapi.py` (SQLMap REST API), which returns JSON-formatted data.

Example flow:

```bash
sqlmapapi.py -s -H 127.0.0.1 -p 8775
curl http://127.0.0.1:8775/task/new
```

Then start a scan for that task and read `/scan/<taskid>/data` (JSON response).

### Step 5: How to Interpret SQLMap Results
Focus on:

- `Parameter`: which input is injectable (`id`).
- `Type`: boolean-based blind / time-based blind.
- `Payload`: exact proof-of-concept payload used by SQLMap.
- `back-end DBMS`: tells likely DB engine.

If SQLMap reports injectable payloads and stable evidence, vulnerability is confirmed.

---

## Dedicated Nikto Section

### What is Nikto?
`Nikto` is a web server scanner that checks for:

- Dangerous files
- Insecure server configurations
- Outdated software signatures
- Missing security headers

### Why Nikto is Used
SQLMap focuses on database injection paths. Nikto focuses on server/web-layer weaknesses.
Using both provides broader security coverage.

### Key Nikto Command Flags
- `-h`: Target host (required)
- `-p`: Port
- `-ssl`: Force HTTPS
- `-o`: Output file
- `-Format`: Report format (such as `txt`, `csv`, `html`, `xml`)
- `-Tuning`: Select scan categories

### How to Run Nikto Against DVWA (Required Example Command)

```bash
nikto -h http://localhost:8081
```

Save report example:

```bash
nikto -h http://localhost:8081 -o nikto_report.txt -Format txt
```

### How to Read Nikto Scan Report
Look for:

- Server banner and version clues
- Missing headers (e.g., clickjacking/XSS protection related headers)
- Exposed files or admin paths
- Configuration findings tagged by Nikto IDs

Treat Nikto findings as investigation leads. Validate each finding manually.

---

## Why SQLMap + Nikto Together?

### SQLMap
Best for database-related injection vulnerabilities:

- Detects SQLi automatically
- Confirms blind injection techniques
- Helps enumerate database metadata when authorized

### Nikto
Best for server and web-layer scanning:

- Detects risky server configuration
- Identifies known weak endpoints/files
- Highlights missing hardening controls

Together they give a stronger web security assessment than either tool alone.

---

## What I Learned

- How web applications send input to backend databases.
- How SQL injection manipulates query logic.
- How blind SQLi can be detected through content and timing differences.
- How automated scanners test, confirm, and report vulnerabilities.
- How to interpret scanner output instead of only running commands.

---

## Project Setup Instructions

### 1) Install and Run DVWA with Docker

```bash
docker pull vulnerables/web-dvwa
docker run --rm -it -p 8081:80 --name dvwa vulnerables/web-dvwa
```

### 2) Access DVWA

- Open: `http://localhost:8081`
- Default login (commonly): `admin` / `password`
- Open DVWA setup page and create/reset database if required
- Set DVWA security level to `Low`

### 3) Run SQLMap

```bash
sqlmap -u "http://localhost:8081/vulnerabilities/sqli_blind/?id=1&Submit=Submit" --cookie="PHPSESSID=YOUR_VALUE; security=low" --batch --output-dir=sqlmap_output
```

### 4) Run Nikto

```bash
nikto -h http://localhost:8081
```

### 5) Save and View Output Files

- SQLMap output directory: `sqlmap_output/`
- SQLMap logs: `sqlmap_output/localhost/log`
- SQLMap session DB: `sqlmap_output/localhost/session.sqlite`
- Custom run logs: `results.txt`
- Nikto report (if saved): `nikto_report.txt`

---

## Future Work

- Add more tools:
  - Hydra (credential attack simulation in authorized labs)
  - Burp Suite (intercepting and manual testing)
  - Nmap (network and service discovery)
- Expand into additional web vulnerabilities:
  - XSS testing
  - CSRF testing
- Add reproducible scripts for report generation and JSON export pipeline.

---

## Important Ethical Note
Use these techniques only in authorized environments (like DVWA lab instances you own or have explicit permission to test).

Unauthorized scanning/testing is illegal and unethical.
