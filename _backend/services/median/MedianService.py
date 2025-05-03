import math
from datetime import timedelta

from _api.api import loadSessionFromDatabase, saveSessionToDatabase
from _backend.diagrams.median import MedianDiagram
from _backend.iracingapi.apicalls.recent_races import requestSubessionId
from _backend.iracingapi.dataprocessors.dataprocessor import Dataprocessor
from _backend.services.median.MedianData import MedianData


class MedianService:

    def __init__(self):
        pass

    async def getMedianImage(self, sessionManager, params, medianOptions):
        subsessionId = params.get("subsession_id", None)
        selectedSession = params.get("selected_session", None)
        userId = params.get("memberId", None)

        if not subsessionId:
            subsessionId = await requestSubessionId(userId, selectedSession, sessionManager)

        dataInDatabase = loadSessionFromDatabase(userId, subsessionId)

        if dataInDatabase:
            data = dataInDatabase
        else:
            data = await Dataprocessor().getData(userId, subsessionId, sessionManager)
            saveSessionToDatabase(userId, subsessionId, data)

        medianData = self.prepareMedianData(data, medianOptions)

        fileLocation = MedianDiagram(medianData=medianData, medianOptions=medianOptions).draw()

        return fileLocation

    def prepareMedianData(self, data, options):
        medianData = MedianData()

        userDriverName = self.getUserDriverName(data)
        driverNames = self.getDriverNames(data)
        userDriverIndex = self.getUserDriverIndex(driverNames, userDriverName)

        xMin, xMax = self.calculateXMinMax(self.getMedianDeltaRunning(data, userDriverIndex))

        medianData.xMin = xMin
        medianData.xMax = xMax
        medianData.driverNames = self.getDriverNames(data)
        medianData.finishPositions = self.getFinishPositions(data)
        medianData.sof = self.getSof(data)
        medianData.carIds = self.getCarIds(data)
        medianData.seriesName = self.getSeriesName(data)
        medianData.trackName = self.getTrackName(data)
        medianData.sessionTime = self.getSessionTime(data)
        medianData.medianDeltaRunning = self.getMedianDeltaRunning(data, userDriverIndex)
        medianData.subsessionId = self.getSubsessionId(data)
        medianData.userDriverName = userDriverName
        medianData.driverNames = driverNames
        medianData.medianDeltas = self.getMedianDelta(data, userDriverIndex)
        medianData.isRainySession = self.getRainInfo(data)
        medianData.medians = self.getMedian(data)
        medianData.seriesId = self.getSeriesId(data)
        medianData.laps = self.getLaps(data)
        medianData.xMedians = self.getXMedians(medianData.medianDeltas)
        medianData.medianDeltas_str = self.formatMedianDeltas(data, userDriverIndex)
        medianData.medians_str = self.formatMedians(medianData.medians)
        medianData.userDriverIndex = userDriverIndex

        return medianData

    def calculateXMinMax(self, medianDelta):
        largestNegativeDelta = min(medianDelta)
        xMin = self.roundDown(largestNegativeDelta)

        if xMin >= -0.5:
            xMin = xMin - 0.5

        largestPositiveDelta = max(medianDelta)
        xMax = self.roundUp(largestPositiveDelta)

        return xMin, xMax

    def roundDown(self, delta):
        # round down to the next 0.5 step
        return math.floor(delta * 2) / 2

    def roundUp(self, delta):
        # round down to the next 0.5 step
        return math.ceil(delta * 2) / 2

    def getMedianDeltaRunning(self, data, userIndex):
        medianDeltas = [driver["median"] for driver in data["drivers"] if driver["result_status"] == "Running"]

        if userIndex > len(medianDeltas) - 1:
            userMedianVal = 0  # if userdriver has disq/disc
        else:
            userMedianVal = medianDeltas[userIndex]

        return [self.calcMedianDeltaToUserDriver(x, userMedianVal) for x in medianDeltas]

    def calcMedianDeltaToUserDriver(self, medianVal, userMedianVal):
        return round(medianVal - userMedianVal, 3)

    def getUserDriverName(self, data):
        return data["metadata"]["user_driver_name"]

    def getDriverNames(self, data):
        return [driver["name"] for driver in data["drivers"]]

    def getUserDriverIndex(self, driverNames, name):
        return driverNames.index(name)

    def getSeriesName(self, data):
        return data["metadata"]["series_name"]

    def getFinishPositions(self, data):
        return [driver["finish_position_in_class"] for driver in data["drivers"]]

    def getCarIds(self, data):
        return [driver["car_id"] for driver in data["drivers"]]

    def getSof(self, data):
        return data["metadata"]["sof"]

    def getTrackName(self, data):
        return data["metadata"]["track"]

    def getSessionTime(self, data):
        return data["metadata"]["session_time"]

    def getMedianDelta(self, data, userIndex):
        medians = [0 if driver["median"] == None else driver["median"] for driver in data["drivers"]]
        userMedianVal = medians[userIndex]
        return [self.calcMedianDeltaToUserDriver(x, userMedianVal) for x in medians]

    def getRainInfo(self, data):
        return data["metadata"]["is_rainy_session"]

    def getMedian(self, data):
        return [driver["median"] for driver in data["drivers"]]

    def getSubsessionId(self, data):
        return data["metadata"]["subsession_id"]

    def getSeriesId(self, data):
        return data["metadata"]["series_id"]

    def getLaps(self, data):
        return [driver["laps"] for driver in data["drivers"]]

    def prepareData(self, originalData, showDiscDisq):
        if showDiscDisq:
            return originalData
        else:  # always include userdriver, even if disc/disq
            user_driver_id = originalData["metadata"]["user_driver_id"]
            originalData["drivers"] = [driver for driver in originalData["drivers"] if
                                       driver["result_status"] == "Running" or driver["id"] == user_driver_id]
            return originalData

    def formatMedianDeltas(self, data, userIndex):
        medians = [driver["median"] for driver in data["drivers"]]
        userMedianVal = medians[userIndex]

        if userMedianVal == None:
            userMedianVal = 0

        deltas = [None if x == None else self.calcMedianDeltaToUserDriver(x, userMedianVal) for x in medians]
        return [self.formatDelta(x) for x in deltas]

    def formatDelta(self, delta):

        if delta == None:
            value = "N/A"
        else:
            if delta < 0:
                value = str(f"{delta:.3f}")
            elif delta > 0:
                value = str(f"+{delta:.3f}")
            else:
                value = ""

        return value

    def formatLaptime(self, medianLaptime):
        if medianLaptime:
            sec_rounded = round(medianLaptime, 3)
            td_raw = str(timedelta(seconds=sec_rounded))
            td_minutes = td_raw.split(":", 1)[1]
            td_minutes = td_minutes[1:-3]
            return td_minutes
        else:
            return "N/A"

    def formatMedians(self, medians):
        return [self.formatLaptime(x) for x in medians]

    def getTrackId(self, data):
        return data["metadata"]["track_id"]

    def getXMedians(selfs, medianDeltas):
        return [0 if x == None else x for x in medianDeltas]
