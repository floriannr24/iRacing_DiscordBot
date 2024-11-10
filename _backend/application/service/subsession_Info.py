import requests


def requestSessionInfo(subsession, session):

    # iRacingAPI
    response = session.get('https://members-ng.iracing.com/data/results/lap_chart_data',
                           params={"subsession_id": subsession, "simsession_number": "0"})

    # check if iRacing API is up and subsessionId is valid
    if not responseIsValid(response):
        return {
            "response": response,
            "service": None
        }

    data = response.json()
    data = requests.get(data["link"]).json()

    print(data)

    return {
        "response": response,
        "service": data["session_info"]
    }
