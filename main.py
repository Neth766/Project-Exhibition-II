from core.http_engine import HTTPEngine

url = "http://localhost:8081/vulnerabilities/sqli_blind/"

engine = HTTPEngine(url)

res = engine.get({"id": "1", "Submit": "Submit"})
print("Status:", res["status"])
print("Length:", res["length"])
