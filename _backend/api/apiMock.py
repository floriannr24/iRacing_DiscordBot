import json
import os


def read_file_content():

    file_path = os.path.join("responseData.json")

    with open(file_path, 'r') as f:
        return json.load(f)
