import requests
from _backend.application.sessionbuilder.session_builder import responseIsValid


def requestLapsMulti(subsession, session):

    # iRacingAPI
    response = session.get('https://members-ng.iracing.com/data/results/lap_chart_data',
                           params={"subsession_id": subsession, "simsession_number": "0"})

    # check if iRacing API is up and subsessionId is valid
    if not responseIsValid(response):
        return {
            "response": response,
            "data": None
        }

    data = response.json()
    data = requests.get(data["link"]).json()

    base_download_url = data["chunk_info"]["base_download_url"]
    chunk_file_names = data["chunk_info"]["chunk_file_names"]

    iRacingData = []

    for data in chunk_file_names:
        intList = requests.get(base_download_url + data).json()
        iRacingData = iRacingData + intList

    return {
        "response": response,
        "data": iRacingData
    }
