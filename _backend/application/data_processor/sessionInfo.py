import statistics
from _backend.application.data.results_multi import requestResultsMulti
from _backend.application.data.subsession_Info import requestSessionInfo
from _backend.application.sessionbuilder.session_builder import responseIsValid


class SessionInfo:

    def __init__(self, session):
        self.subsession_id = None
        self.session = session
        self.iRacing_results = None
        self.iRacing_subsessionInfo = None

    def get_SessionInfo_Data(self, subsession_id):

        self.subsession_id = subsession_id
        cust_id = 817320

        response1 = requestResultsMulti(self.subsession_id, self.session)
        response2 = requestSessionInfo(self.subsession_id, self.session)

        if not responseIsValid(response1["response"]):
            return response1

        self.iRacing_results = response1["data"]
        self.iRacing_subsessionInfo = response2["data"]

        exportDict = {
            "session_start_time": self.get_session_start_time(),
            "series_name": self.get_series_name(),
            "start_position": self.get_start_position(cust_id),
            "finish_position": self.get_finish_position(cust_id),
            "winner_name": self.get_winner_name(),
            "sof": self.get_sof(),
            "subsession_id": self.subsession_id,
            "track_name": self.get_track_name()
        }

        return {
            "response": response1["response"],
            "data": exportDict
        }

    def get_finish_position(self, cust_id):
        for data in self.iRacing_results["session_results"][2]["results"]:
            if data["cust_id"] == cust_id:
                if data['reason_out'] == 'Running':
                    return data["finish_position"] + 1
                if data['reason_out'] == "Disconnected":
                    return 'DISC'
                if data['reason_out'] == "Disqualified":
                    return 'DISQ'

    def get_start_position(self, cust_id):
        for data in self.iRacing_results["session_results"][2]["results"]:
            if data["cust_id"] == cust_id:
                return data["starting_position"] + 1

    def get_session_start_time(self):
        return self.iRacing_subsessionInfo["start_time"]

    def get_series_name(self):
        return self.iRacing_results["series_name"]

    def get_track_name(self):
        return self.iRacing_results["track"]["track_name"]

    def get_winner_name(self):
        for data in self.iRacing_results["session_results"][2]["results"]:
            if data["finish_position"] == 0:
                return data["display_name"]

    def get_sof(self):

        sof_list = []

        for data in self.iRacing_results["session_results"][2]["results"]:
            sof_list.append(data["oldi_rating"])

        sof = statistics.mean(sof_list)
        sof = round(sof, 0)

        return sof
