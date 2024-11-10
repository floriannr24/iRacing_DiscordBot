import json
import os


def read_file_content():

    file_path = os.path.join("responseData.json")

    with open(file_path, 'r') as f:
        return json.load(f)


def write_file_content(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)
