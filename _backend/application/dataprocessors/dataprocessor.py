import asyncio
import statistics
from _backend.application.service.laps_multi import requestLapsMulti
from _backend.application.service.results_multi import requestResultsMulti
from _backend.application.session.sessionmanager import SessionManager
from _backend.application.utils.publicappexception import PublicAppException

class Dataprocessor:
    def __init__(self):
        self.iRacing_lapdata = None
        self.iRacing_results = None

    async def getData(self, userId, subsessionId, sessionManager: SessionManager):

        try:
            self.iRacing_results = await requestResultsMulti(subsessionId, sessionManager)
            self.iRacing_lapdata = await requestLapsMulti(subsessionId, sessionManager)
        except PublicAppException as e:
            raise PublicAppException(e.args[0])
        # better session.close behavior?
        # session.close for timeout?

        if not self.iRacing_results or not self.iRacing_lapdata:
            raise RuntimeError("'self.iRacing_results' or 'self.iRacing_lapdata' is null")

        user_carclass = self.searchUsersCarClass(userId)
        unique_drivers = self.findUniqueDriversInCarclassOfUserDriver(user_carclass)

        dictionary = {
            "metadata": {
                "subsession_id": subsessionId,
                "laps": None,
                "series_name": self.getSeriesName(),
                "series_id": self.getSeriesId(),
                "track": self.getTrackName(),
                "track_id": self.getTrackId(),
                "session_time": self.getSessionTime(),
                "sof": self.getSessionSof(),
                "user_driver_id": userId,
                "user_driver_name": self.getUserDriverName(userId),
                "is_rainy_session": self.getRainInfo()
            },
            "drivers": self.addDriverInfo(unique_drivers)
        }

        self.sortDictionary(dictionary)
        self.setPositionLabels(dictionary)

        return dictionary

    def searchUsersCarClass(self, id):

        carclassid = None

        if len(self.iRacing_results["session_results"]) <= 1:
            raise PublicAppException("Selected session is a practice session. Only race sessions are supported.")

        for results in self.iRacing_results["session_results"][2]["results"]:
            if results["cust_id"] == id:
                carclassid = results["car_class_id"]
                break
            else:
                continue

        if not carclassid:
            raise PublicAppException("Couldn't find your member_id in the given session.")

        return carclassid

    def sortDictionary(self, dictionary):

        # running drivers
        driversRunning = [driver for driver in dictionary["drivers"] if driver["result_status"] == "Running"]
        secondarySortRunning = list(sorted(driversRunning, key=lambda p: p["finish_position_in_class"]))  # secondary sort by key "finish_position"
        primarySortRunning = list(sorted(secondarySortRunning, key=lambda p: p["laps_completed"], reverse=True))  # primary sort by key "laps_completed", descending

        # disc/disq drivers
        driversDiscDisq = [driver for driver in dictionary["drivers"] if driver["result_status"] != "Running"]
        secondarySortDiscDisq = list(sorted(driversDiscDisq, key=lambda p: p["finish_position_in_class"]))  # secondary sort by key "finish_position"
        primarySortDiscDisq = list(sorted(secondarySortDiscDisq, key=lambda p: p["laps_completed"], reverse=True))  # primary sort by key "laps_completed", descending

        dictionary["drivers"] = primarySortRunning + primarySortDiscDisq

    def findUniqueDriversInCarclassOfUserDriver(self, user_carclass):
        unique_drivers = set()

        for driver in self.iRacing_results["session_results"][2]["results"]:
            if driver["car_class_id"] == user_carclass:
                unique_drivers.add((driver["cust_id"], driver["display_name"]))
        return unique_drivers

    def convertTimeformatToSeconds(self, laptime):
        if not laptime == -1:
            return laptime / 10000
        else:
            return None

    def collectInfo(self, driver):

        driver_id = driver[0]
        driver_name = driver[1]

        list_of_positions = self.list_of_positions(driver_id)
        laps = self.set_laps(driver_id)

        intDict = {
            "name": driver_name,
            "id": driver_id,
            "finish_position_in_class": self.set_finishPositionInClass(driver_id),
            "result_status": self.set_resultStatus(driver_id),
            "laps_completed": self.set_lapsCompleted(list_of_positions),
            "laps": laps,
            "car_class_name": self.set_carClass(driver_id)["name"],
            "car_id": self.set_carId(driver_id),
            "personal_best": self.set_fastestPersonalLap(driver_id),
            "fastest_lap": self.set_ifDriverSetFastestLapInSession(driver_id),
            "irating": self.set_iRating(driver_id),
            "license": None,
            "median": self.set_median(laps),
        }

        return intDict

    def list_of_positions(self, driver_id):
        laps_completed_pos = []
        for record in self.iRacing_lapdata:
            if record["cust_id"] == driver_id:
                laps_completed_pos.append(record["lap_position"])
        return laps_completed_pos

    def set_lapsCompleted(self, laps_completed_pos):
        return len(laps_completed_pos) - 1

    def set_resultStatus(self, driver_id):
        for data in self.iRacing_results["session_results"][2]["results"]:
            if driver_id == data["cust_id"]:
                return data["reason_out"]

    def set_laps(self, driver_id):

        session_time0 = 0
        laps = []

        for i, record in enumerate(self.iRacing_lapdata):

            if record["cust_id"] == driver_id:

                lap_number = record["lap_number"]
                session_time1 = record["session_time"]

                if lap_number == 0:
                    session_time0 = record["session_time"]

                if lap_number > 0:
                    lap_time = session_time1 - session_time0
                    session_time0 = session_time1
                    laps.append(self.convertTimeformatToSeconds(lap_time))

        return laps

    def set_carClass(self, driver_id):

        carClass = {}

        for data in self.iRacing_results["session_results"][2]["results"]:
            if data["cust_id"] == driver_id:
                carClass["name"] = data["car_class_name"]
                break

        return carClass

    def set_finishPositionInClass(self, driver_id):
        for data in self.iRacing_results["session_results"][2]["results"]:
            if data["cust_id"] == driver_id:
                if data["reason_out"] == "Running":
                    return data["finish_position_in_class"] + 1
                else:
                    return -1

    def addDriverInfo(self, unique_drivers):
        driverArray = [self.collectInfo(driver) for driver in unique_drivers]
        return driverArray

    def set_ifDriverSetFastestLapInSession(self, driver_id):
        return True if self.findUserWithFastestLap(driver_id) else False

    def findUserWithFastestLap(self, driver_id):
        for driverlap in self.iRacing_lapdata:
            if driverlap["cust_id"] == driver_id and driverlap["fastest_lap"]:
                return True

    def set_fastestPersonalLap(self, driver_id):
        session_time0 = 0

        for i, record in enumerate(self.iRacing_lapdata):

            if record["cust_id"] == driver_id:

                lap_number = record["lap_number"]
                session_time1 = record["session_time"]

                if lap_number == 0:
                    session_time0 = record["session_time"]

                if lap_number > 0:
                    lap_time = session_time1 - session_time0
                    session_time0 = session_time1
                    if record["incident"] == False and record["personal_best_lap"] == True:
                        return self.convertTimeformatToSeconds(lap_time)

    def getSeriesName(self):
        return self.iRacing_results["series_name"]

    def set_carId(self, driver_id):
        for data in self.iRacing_results["session_results"][0]["results"]:
            if data["cust_id"] == driver_id:
                return data["car_id"]

    def getUserDriverName(self, id):
        for driver in self.iRacing_results["session_results"][2]["results"]:
            if driver["cust_id"] == id:
                return driver["display_name"]

    def getTrackName(self):
        trackname = self.iRacing_results["track"]["track_name"]
        trackConfig = self.iRacing_results["track"]["config_name"]

        if trackConfig == "N/A":
            track = f"{trackname}"
        else:
            track = f"{trackname} ({trackConfig})"

        return track

    def getSessionSof(self):
        return self.iRacing_results["event_strength_of_field"]

    def getSessionTime(self):
        startTime = self.iRacing_results["start_time"]
        startTimeFormatted = startTime.replace('T', ' ')[:-4] + " GMT"
        return startTimeFormatted

    def set_iRating(self, driver_id):
        for data in self.iRacing_results["session_results"][0]["results"]:
            if data["cust_id"] == driver_id:
                return data["newi_rating"]

    def set_median(self, laps):
        if laps:
            return statistics.median(laps)
        else:
            return None

    def getSeriesId(self):
        return self.iRacing_results["series_id"]

    def getTrackId(self):
        return self.iRacing_results["track"]["track_id"]

    def getRainInfo(self):
        # return self.iRacing_results["session_results"][0]["weather_result"]["precip_time_pct"] > 0
        pass

    def setPositionLabels(self, dictionary):
        driversRunning = [driver for driver in dictionary["drivers"] if driver["result_status"] == "Running"]
        for i, driver in enumerate(driversRunning):
            driver["finish_position_in_class"] = i + 1

        driversDiscDisq = [driver for driver in dictionary["drivers"] if driver["result_status"] != "Running"]
        for driver in driversDiscDisq:
            if driver["result_status"] == "Disconnected":
                driver["finish_position_in_class"] = 'DISC'
            if driver["result_status"] == "Disqualified":
                driver["finish_position_in_class"] = 'DISQ'



