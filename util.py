from pathlib import Path
import json
def load_json(filename):
    path = Path(__file__).parent / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)