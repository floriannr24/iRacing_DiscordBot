import statistics
import numpy as np
from _backend.application.data.laps_multi import requestLapsMulti
from _backend.application.data.results_multi import requestResultsMulti
from _backend.application.sessionbuilder.session_builder import responseIsValid

class Boxplot:
    def __init__(self, session):
        self.subsession_id = None
        self.session = session
        self.iRacing_lapdata = None
        self.iRacing_results = None

    def get_Boxplot_Data(self, subsession_id):

        self.subsession_id = subsession_id

        # get session application.data from iRacingAPI
        response1 = requestLapsMulti(self.subsession_id, self.session)
        response2 = requestResultsMulti(self.subsession_id, self.session)

        # abort action if response is not 200
        if not responseIsValid(response1["response"]):
            return response1

        self.iRacing_lapdata = response1["data"]
        self.iRacing_results = response2["data"]

        unique_drivers = self.findUniqueDrivers(self.iRacing_lapdata)

        dictionary = {
            "metadata": {
                "subsession_id": self.subsession_id,
                "laps": None,
                "timeframe": [],
                "median": None,
                "carclasses": self.findCarclasses(self.iRacing_results)
            },
            "drivers": self.addDriverInfo(unique_drivers)
        }

        dictionary = self.caclulateTimeframe(dictionary)
        dictionary = self.calculateMedian(dictionary)
        dictionary = self.sortDictionary(dictionary)
        dictionary = self.removePositionsForDiscDisq(dictionary)
        dictionary = self.numberOfLapsInEvent(dictionary)

        return {
            "response": response1["response"],
            "data": dictionary
        }

    def searchUsersCarClass(self, id):

        carclassid = None

        for results in self.iRacing_results["session_results"][2]["results"]:
            if results["cust_id"] == id:
                carclassid = results["car_class_id"]
                break
            else:
                continue
        return carclassid

    def sortDictionary(self, dictionary):
        secondarySort = list(sorted(dictionary["drivers"],
                                    key=lambda p: p["finish_position"]))  # secondary sort by key "finish_position"

        primarySort = list(sorted(secondarySort, key=lambda p: p["laps_completed"],
                                  reverse=True))  # primary sort by key "laps_completed", descending

        dictionary["drivers"] = primarySort

        return dictionary

    def filterByCarClass(self, carclass_id):
        iRacing_results = []
        iRacing_lapdata = []

        for results in self.iRacing_results["session_results"][2]["results"]:
            if results["car_class_id"] == carclass_id:
                iRacing_results.append(results["cust_id"])

        for driver in iRacing_results:
            for lapdata in self.iRacing_lapdata:
                if driver == lapdata["cust_id"]:
                    iRacing_lapdata.append(lapdata)

        return iRacing_lapdata

    def findUniqueDrivers(self, iRacing_lapdata_carclass):
        unique_drivers = set()
        for item in iRacing_lapdata_carclass:
            unique_drivers.add((item["cust_id"], item["display_name"]))
        return unique_drivers

    def convertTimeformatToSeconds(self, laptime):
        if not laptime == -1:
            return laptime / 10000
        else:
            return None

    def scanForInvalidTypes(self, laptimes, arg1, arg2):
        return [laptime for laptime in laptimes if laptime != arg1 if laptime != arg2]

    def collectInfo(self, driver):

        driver_id = driver[0]
        driver_name = driver[1]

        list_of_positions = self.list_of_positions(driver_id)

        intDict = {
            "name": driver_name,
            "id": driver_id,
            "finish_position": self.set_finishPosition(list_of_positions),
            "finish_position_in_class": self.set_finishPositionInClass(driver_id),
            "result_status": self.set_resultStatus(driver_id),
            "laps_completed": self.set_lapsCompleted(list_of_positions),
            "laps": self.set_laps(driver_id),
            "incidents": self.set_incidents(driver_id),
            "car_class_id": self.set_carClass(driver_id)["id"],
            "car_class_name": self.set_carClass(driver_id)["name"],
            "personal_best": self.set_fastestPersonalLap(driver_id),
            "fastest_lap": self.set_ifDriverSetFastestLapInSession(driver_id)
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

    def set_finishPosition(self, laps_completed_pos):
        return laps_completed_pos[self.set_lapsCompleted(laps_completed_pos)]

    def set_resultStatus(self, driver_id):
        for data in self.iRacing_results["session_results"][2]["results"]:
            if driver_id == data["cust_id"]:
                return data["reason_out"]

    def extractLaptimes(self, all_laptimes, raceCompleted):

        numberOfDrivers = len(all_laptimes)
        drivers_raw = []

        if raceCompleted:
            laps = []
            for lapdata in all_laptimes:
                if lapdata["result_status"] == "Running":
                    laps.append(lapdata["laps"])
                    drivers_raw.append(lapdata["driver"])
                else:
                    continue
            return laps
        else:
            laps = []
            for lapdata in all_laptimes:
                if lapdata["result_status"] == "Disqualified" or lapdata["result_status"] == "Disconnected":
                    laps.append(lapdata["laps"])
                    drivers_raw.append(lapdata["driver"])
                else:
                    continue

            # fill up indices, so DISQ and DISC drivers are put to the last places in the diagram
            indicesToFillUp = numberOfDrivers - len(laps)
            for i in range(indicesToFillUp):
                laps.insert(0, "")
            return laps

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

    def deleteInvalidLaptimes(self, output):
        output["laps"] = [value for value in output["laps"] if value != -1 if value is not None]
        return output

    def caclulateBoxplotData(self, output):

        output["bpdata"] = {
            "median": None,
            "mean": None,
            "Q1": None,
            "Q3": None,
            "whisker_top": None,
            "whisker_bottom": None,
            "fliers_top": None,
            "fliers_bottom": None,
            "laps_rndFactors": None
        }

        if output["laps"]:
            output["bpdata"]["median"] = statistics.median(output["laps"])
            output["bpdata"]["mean"] = statistics.mean(output["laps"])
            output["bpdata"]["Q1"] = Q1 = np.quantile(output["laps"], 0.25)
            output["bpdata"]["Q3"] = Q3 = np.quantile(output["laps"], 0.75)
            output["bpdata"]["whisker_top"] = whisker_top = self.calc_whiskerTop(Q1, Q3, output["laps"])
            output["bpdata"]["whisker_bottom"] = whisker_bottom = self.calc_whiskerBottom(Q1, Q3, output["laps"])
            output["bpdata"]["fliers_top"] = fliers_top = self.calc_fliersTop(whisker_top, output["laps"])
            output["bpdata"]["fliers_bottom"] = fliers_bottom = self.calc_fliersBottom(whisker_bottom, output["laps"])
            output["bpdata"]["laps_rndFactors"] = self.calc_lapsRndmFactors(fliers_top, fliers_bottom, output["laps"])

        return output

    def caclulateTimeframe(self, dictionary):

        tempMax = []
        tempMin = []

        for driver in dictionary["drivers"]:
            if driver["laps"]:
                tempMax.append(max(driver["laps"]))
                tempMin.append(min(driver["laps"]))

        slowestLap = max(tempMax)
        fastestLap = min(tempMin)

        dictionary["metadata"]["timeframe"] = [fastestLap, slowestLap]

        return dictionary

    def calc_fliersTop(self, whisker_top, laps):

        laps = sorted(laps)

        if whisker_top:
            candidates = [item for item in laps if item > whisker_top]
            return candidates
        else:
            return []

    def calc_fliersBottom(self, whisker_bottom, laps):

        laps = sorted(laps, reverse=True)

        if whisker_bottom:
            candidates = [item for item in laps if item < whisker_bottom]
            return candidates
        else:
            return []

    def calc_whiskerTop(self, Q1, Q3, laps):

        IQR15 = (Q3 - Q1) * 1.5
        whiskerTop = Q3 + IQR15

        laps = sorted(laps)

        candidates = [item for item in laps if item < whiskerTop if item > Q3]

        if not candidates:
            return Q3
        else:
            return max(candidates)

    def calc_whiskerBottom(self, Q1, Q3, laps):

        IQR15 = (Q3 - Q1) * 1.5
        whiskerBottom = Q1 - IQR15

        laps = sorted(laps, reverse=True)

        candidates = [item for item in laps if item > whiskerBottom if item < Q1]

        if not candidates:
            return Q1
        else:
            return min(candidates)

    def calculateMedian(self, dictionary):

        laps = []

        for driver in dictionary["drivers"]:

            for lap in driver["laps"]:
                laps.append(lap)

        dictionary["metadata"]["median"] = statistics.median(laps)

        return dictionary

    def calc_lapsRndmFactors(self, fliers_top, fliers_bottom, laps):

        randoms = np.random.normal(0, 1, len(laps)).tolist()
        excludedIndex = [i for i, x in enumerate(laps) if x in fliers_top or x in fliers_bottom]

        for i in excludedIndex:
            randoms[i] = 0

        return randoms

    def removePositionsForDiscDisq(self, dictionary):

        for driver in dictionary["drivers"]:
            if driver["result_status"] == "Disconnected":
                driver["finish_position"] = 'DISC'
                driver["finish_position_in_class"] = 'DISC'
            if driver["result_status"] == "Disqualified":
                driver["finish_position"] = 'DISQ'
                driver["finish_position_in_class"] = 'DISQ'

        return dictionary

    def set_carClass(self, driver_id):

        carClass = {}

        for data in self.iRacing_results["session_results"][2]["results"]:
            if data["cust_id"] == driver_id:
                carClass["id"] = data["car_class_id"]
                carClass["name"] = data["car_class_name"]
                break

        return carClass

    def set_finishPositionInClass(self, driver_id):
        for data in self.iRacing_results["session_results"][2]["results"]:
            if data["cust_id"] == driver_id:
                return data["finish_position_in_class"] + 1

    def findCarclasses(self, iRacing_results):
        unique_cc = set()
        for item in iRacing_results["session_results"][2]["results"]:
            unique_cc.add(item["car_class_id"])
        unique_cc_list = list(unique_cc)
        unique_cc_list.sort()

        return unique_cc_list

    def addDriverInfo(self, unique_drivers):

        driverArray = []

        for driver in unique_drivers:
            output = self.collectInfo(driver)
            # output = self.deleteInvalidLaptimes(output)
            output = self.caclulateBoxplotData(output)
            driverArray.append(output)

        return driverArray

    def set_personalBestLap(self, driver_id):
        pass

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

    def findFastestLap(self, driver_id):
        pass

    def set_incidents(self, driver_id):
        laps = []
        for i, record in enumerate(self.iRacing_lapdata):
            if record["cust_id"] == driver_id:
                laps.append(
                    {"lap": record["lap_number"] - 1, "incidents": record["incident"], "events": record["lap_events"]})
        return laps

    def numberOfLapsInEvent(self, dict):
        # depends on class

        dict["metadata"]["laps"] = {}
        carclasses = dict["metadata"]["carclasses"]

        for cclass in carclasses:
            cclass_laps = self.lapsOfCarclass(cclass, dict)
            dict["metadata"]["laps"][str(cclass)] = cclass_laps

        return dict

    def lapsOfCarclass(self, cclass, dict):
        for driver in dict["drivers"]:
            if driver["car_class_id"] == cclass and driver["finish_position_in_class"] == 1:
                return len(driver["laps"])
