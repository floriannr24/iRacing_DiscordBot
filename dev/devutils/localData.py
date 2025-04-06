import json
from pathlib import Path

def saveToJson(data, id, type):
    path = Path().absolute() / 'dev' / 'boxedData'
    filename = f"{str(id)}_{type}.json"
    location = str(path / filename)

    print(f"Saved /dev/boxedData/{filename}")

    with open(location, "w") as file:
        json.dump(data, file, indent=2)

def loadFromJson(id, type):
    path = Path().absolute() / 'dev' / 'boxedData'
    filename = f"{str(id)}_{type}.json"
    location = str(path / filename)

    print(f"Loaded /dev/boxedData/{filename}")

    try:
        with open(location, "r") as file:
            data = json.load(file)
    except Exception:
        raise Exception(f"No boxed data available for /dev/boxedData/{filename}")

    return data
