
import requests

from _backend.application.sessionbuilder.session_builder import responseIsValid


class RecentRaces:

    def __init__(self, session):
        self.session = session

    def get_RecentRaces(self, cust_id):

        response = self.requestRecentRaces(cust_id)

        if not responseIsValid(response["response"]):
            return response

        exportDict = []

        for element in response["data"]:
            intdict = {
                "session_start_time": element["session_start_time"],
                "series_name": element["series_name"],
                "start_position": element["start_position"],
                "finish_position": element["finish_position"],
                "winner_name": element["winner_name"],
                "sof": element["strength_of_field"],
                "subsession_id": element["subsession_id"],
                "track_name": element["track"]["track_name"]
            }

            exportDict.append(intdict)

        return {
            "response": response["response"],
            "data": exportDict
        }

    def requestRecentRaces(self, cust_id):

        # iRacingAPI
        response = self.session.get('https://members-ng.iracing.com/data/stats/member_recent_races',
                                params={'cust_id': cust_id})

        if not responseIsValid(response):
            return {
                "response": response,
                "data": None
            }

        data = requests.get(response.json()["link"]).json()

        return {
            "response": response,
            "data": data["races"]
        }

    # def get_finish_position(self, subsession_id, cust_id):
    #
    #     iRacing_results = ResultsMulti().requestResultsMulti(subsession_id, self.session)
    #
    #     for data in iRacing_results["session_results"][2]["results"]:
    #         if data["cust_id"] == cust_id:
    #             if data['reason_out'] == 'Running':
    #                 return data["finish_position"] + 1
    #             if data['reason_out'] == "Disconnected":
    #                 return 'DISC'
    #             if data['reason_out'] == "Disqualified":
    #                 return 'DISQ'
