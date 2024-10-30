import requests
from _backend.application.sessionbuilder.session_builder import responseIsValid


def requestResultsMulti(subsession, session):
    # iRacingAPI
    response = session.get('https://members-ng.iracing.com/data/results/get',
                           params={"subsession_id": subsession, "simsession_number": "0"})

    # check if iRacing API is up and subsessionId is valid
    if not responseIsValid(response):
        return {
            "response": response,
            "data": None
        }

    iRacingData = requests.get(response.json()["link"]).json()

    intDict = {
        "series_name": iRacingData["series_name"],
        "track": iRacingData["track"],
        "weather": iRacingData["weather"],
        "session_results": iRacingData["session_results"]
    }

    iRacingData = intDict

    return {
        "response": response,
        "data": iRacingData
    }
