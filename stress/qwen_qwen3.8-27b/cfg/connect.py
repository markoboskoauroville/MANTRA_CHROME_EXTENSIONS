import json

with open('settings.json') as f:
    settings = json.load(f)

host = settings['host']
port = settings['port']
retries = settings['retries']

print(f"Connecting to {host}:{port} with {retries} retries")
