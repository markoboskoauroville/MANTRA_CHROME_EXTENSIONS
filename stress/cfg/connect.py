import json

with open("settings.json", "r") as f:
    config = json.load(f)

print(f"Connecting to {config['host']}:{config['port']} with {config['retries']} retries")
