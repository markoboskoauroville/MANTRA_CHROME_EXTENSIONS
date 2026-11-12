import json
from pathlib import Path

def main():
    config_path = Path(__file__).with_name("settings.json")
    with config_path.open() as f:
        cfg = json.load(f)
    host = cfg["host"]
    port = cfg["port"]
    retries = cfg["retries"]
    print(f"Connecting to {host}:{port} with {retries} retries")

if __name__ == "__main__":
    main()
