class Delta:

    def __init__(self):
        pass
        # def get_Delta_Data(self, beforeDrivers, afterDrivers):
        #
        #     # get session application.data from iRacingAPI + FuzzwahAPI
        #     self.iRacing_results = ResultsMulti(self.subsession_id, self.session).requestResultsMulti()
        #     self.iRacing_lapdata = LapsMulti(self.subsession_id, self.session).requestLapsMulti()
        #
        #     carclass_id = self.gen_searchUsersCarClass("Florian Niedermeier2")  # search carclass id of user
        #     iRacingData_carclass, fuzzData_carclass = self.gen_filterByCarClass(
        #         carclass_id)  # get only application.data for corresponding carclass
        #     unique_drivers = self.gen_findUniqueDrivers(iRacingData_carclass)  # find unique drivers in said carclass
        #
        #     output = self.delta_collectInfo(iRacingData_carclass, unique_drivers)  # collect info in dictionary
        #     output = self.gen_sortDictionary(output)  # sort dictionary by "laps completed" and "finish position"
        #     output = self.delta_find_DISQ_DISC(
        #         output)  # find DISQ / DISC drivers and append them to the end of the dictionary
        #     # output_data = self.delta_filterDrivers(output_data, beforeDrivers, afterDrivers)
        #     output = self.delta_calcDelta(output)  # calculate delta time to first and add to dictionary
        #
        #     return output
        #
        # def get_Pace_Data(self, name):
        #
        #     outerDict = {}
        #
        #     for i, id in enumerate(self.subsession_id):
        #         irData = LapsMulti(id, self.session).requestLapsMulti()
        #         metaData = ResultsMulti(id, self.session).requestResultsMulti()
        #
        #         output = self.pace_collectInfo(irData, name)
        #         output = self.gen_scanForInvalidTypes(output, -1, None)
        #
        #         data = {}
        #         outerDict["race" + str(i)] = data
        #         data["laps"] = output
        #         data["metaData"] = metaData
        #
        #     return outerDict

        ####################################################################

        ####################################################################

        # def delta_calcDelta(self, lapsDict):
        #
        #     for i in range(0, len(lapsDict), 1):
        #
        #         intDelta = []
        #
        #         for s in range(0, len(lapsDict[i]["session_time"]), 1):
        #             delta = lapsDict[0]["session_time"][s] - lapsDict[i]["session_time"][s]
        #             if not delta == 0:
        #                 delta = round(delta, 2) * (-1)
        #             intDelta.append(delta)
        #         lapsDict[i]["delta"] = intDelta
        #
        #     return lapsDict
        #
        # def delta_find_DISQ_DISC(self, all_laptimes):
    #
    #     finished = []
    #     disq_disc = []
    #
    #     for lapdata in all_laptimes:
    #         if lapdata["result_status"] == "Running":
    #             finished.append(lapdata)
    #         else:
    #             continue
    #
    #     for lapdata in all_laptimes:
    #         if lapdata["result_status"] == "Disqualified" or lapdata["result_status"] == "Disconnected":
    #             disq_disc.append(lapdata)
    #         else:
    #             continue
    #
    #     return finished + disq_disc
    #
    # def delta_filterDrivers(self, data, beforeDrivers, afterDrivers):
    #     name = "Florian Niedermeier2"
    #
    #     if ((beforeDrivers or afterDrivers) == None) or ((beforeDrivers or afterDrivers) == 0):
    #         return data
    #
    #     foundIndex = 0
    #
    #     # searching current driver
    #     for x in range(0, len(data), 1):
    #         if data[x]["driver"] == name:
    #             foundIndex = x
    #
    #     # check if "beforeDrivers" and "afterDrivers" args are valid
    #     if beforeDrivers + 1 > data[foundIndex]["finish_position"] or afterDrivers > len(data) - 1:
    #         return data
    #
    #     else:
    #
    #         foundData = []
    #
    #         for i in range(1, beforeDrivers + 1):
    #             foundData.append(data[foundIndex - (beforeDrivers + 1) + i])
    #
    #         foundData.append(data[foundIndex])
    #
    #         for i in range(1, afterDrivers + 1):
    #             foundData.append(data[foundIndex + i])
    #
    #     return foundData
    #
    # def delta_collectInfo(self, laps_json, unique_drivers):
    #     lapsDict = []
    #     for driver in unique_drivers:
    #
    #         sessionTime = []
    #         delta = []
    #         laps_completed_pos = []
    #         intDict = {
    #             "driver": driver,
    #             "result_status": None,
    #             "laps_completed": None,
    #             "finish_position": None,
    #             "session_time": sessionTime,
    #             "delta": delta
    #         }
    #
    #         lapsDict.append(intDict)
    #
    #         # add "finish_position", "laps_completed" to intDict{} via requestLapsMulti()
    #         for record in laps_json:
    #             if record["display_name"] == driver:
    #                 seconds_per_lap = self.bpm_cleanAndConvertLapTimes(record["lap_time"], record["lap_number"])
    #                 sessionSeconds_per_lap = self.gen_convertTimeformatToSeconds(record["session_time"])
    #                 laps_completed_pos.append(record["lap_position"])
    #                 intDict["session_time"].append(sessionSeconds_per_lap)
    #
    #         intDict["finish_position"] = laps_completed_pos[len(laps_completed_pos) - 1]
    #         intDict["laps_completed"] = len(laps_completed_pos) - 1
    #
    #         # add "Running", "Disq" or "Disconnected" to intDict{} via FuzzwahAPI
    #         # add "carId" to intDict{} via FuzzwahAPI
    #         for result in self.iRacing_results["session_results"][2]["results"]:
    #             if driver == result["display_name"]:
    #                 intDict["result_status"] = result["reason_out"]
    #
    #     return lapsDict
    #
    # ####################################################################
    #
    # def pace_collectInfo(self, irdata, driverName):
    #
    #     intList = []
    #
    #     for lap in irdata:
    #         if lap["display_name"] == driverName:
    #             laptime = lap["lap_time"]
    #             laptime = self.gen_convertTimeformatToSeconds(laptime)
    #             intList.append(laptime)
    #
    #     return intList