import json

with open("settings.json") as f:
    s = json.load(f)

print(f"Connecting to {s['host']}:{s['port']} with {s['retries']} retries")
