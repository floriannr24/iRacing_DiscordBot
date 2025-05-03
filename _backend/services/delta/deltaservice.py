import copy
import math

import numpy as np

from _api.api import loadSessionFromDatabase, saveSessionToDatabase
from _backend.iracingapi.apicalls.recent_races import requestSubessionId
from _backend.iracingapi.dataprocessors.dataprocessor import Dataprocessor
from _backend.iracingapi.session.sessionmanager import SessionManager
from _backend.services.delta.deltadata import DeltaData
from _backend.services.delta.deltadiagram import DeltaDiagram
from _backend.services.delta.deltaoptions import ReferenceMode, SelectionMode, DeltaOptions
from _bot.botUtils import BotParams


class DeltaService:

    async def getDeltaImage(self, sessionManager: SessionManager, params: BotParams, deltaOptions: DeltaOptions):
        subsessionId = params.subsessionId
        selectedSession = params.selectedSession
        memberId = params.memberId

        if not subsessionId:
            subsessionId = await requestSubessionId(memberId, selectedSession, sessionManager)

        dataInDatabase = loadSessionFromDatabase(memberId, subsessionId)

        if dataInDatabase:
            data = dataInDatabase
        else:
            data = await Dataprocessor().getData(memberId, subsessionId, sessionManager)
            saveSessionToDatabase(memberId, subsessionId, data)

        deltaData = self.initDeltaData(data, deltaOptions)

        fileLocation = DeltaDiagram(deltaData=deltaData, deltaOptions=deltaOptions).draw()

        return fileLocation

    def initDeltaData(self, originalData, options: DeltaOptions):

        data = self.prepareData(originalData, options)

        userDriverName = self.getUserDriverName(data)
        driverNames = self.getDriverNames(data)
        yMin, yMax = self.calculateyMinYMax(data)

        deltadata = DeltaData()
        deltadata.drivers = self.getDrivers(data)
        deltadata.numberOfLaps = self.getNumberOfLaps(data)
        deltadata.driverNames = driverNames
        deltadata.userDriverIndex = self.getUserDriverIndex(driverNames, userDriverName)
        deltadata.yMin = yMin
        deltadata.yMax = yMax
        deltadata.sof = self.getSof(data)
        deltadata.trackName = self.getTrackName(data)
        deltadata.seriesName = self.getSeriesName(data)
        deltadata.sessionTime = self.getSessionTime(data)
        deltadata.subsessionId = self.getSubsessionId(data)
        deltadata.isRainySession = self.getRainInfo(data)

        return deltadata

    def prepareData(self, originalData, options):

        data = copy.deepcopy(originalData)
        referenceMode = options.referenceMode
        selectionMode = options.selectionMode
        showDiscDisq = options.showDiscDisq

        if not showDiscDisq:
            data["drivers"] = [driver for driver in data["drivers"] if driver["result_status"] == "Running"]

        drivers = data["drivers"]
        userDriverName = self.getUserDriverName(data)
        driverIndex = [driver["name"] for driver in drivers].index(userDriverName)

        if referenceMode == ReferenceMode.WINNER:
            targetLaps = drivers[0]["laps"]
            if not selectionMode == SelectionMode.ALL:
                drivers = [drivers[0]] + self.getDriverSubset(drivers, driverIndex, selectionMode.value)  # always show winner-driver
        elif referenceMode == ReferenceMode.ME:
            targetLaps = drivers[driverIndex]["laps"]
            if not selectionMode == SelectionMode.ALL:
                drivers = self.getDriverSubset(drivers, driverIndex, selectionMode.value)
        else:
            targetLaps = drivers[0]["laps"]
            drivers = drivers

        for driver in drivers:
            delta = np.cumsum(np.array(driver["laps"]) - np.array(targetLaps[:len(driver["laps"])]))
            delta = np.pad(delta, (0, len(targetLaps) - len(driver["laps"])), mode='constant', constant_values=None)
            delta = np.ndarray.tolist(delta)
            driver["deltaToTarget"] = delta

        for driver in drivers:
            deltaToTarget = driver["deltaToTarget"]
            startPos = driver["start_position_in_class"]
            deltaToTarget.insert(0, (startPos - 1) * 0.5)

        return data

    def getDriverSubset(self, drivers, userDriverIndex, numberOfDrivers):
        indexToShow = (numberOfDrivers - 1) / 2

        if userDriverIndex >= 3:
            min = int(userDriverIndex - indexToShow)
        else:
            min = 1

        max = int(userDriverIndex + indexToShow)
        subset = drivers[min:max + 1]
        return subset

    def getRainInfo(self, data):
        return data["metadata"]["is_rainy_session"]

    def getUserDriverName(self, data):
        return data["metadata"]["user_driver_name"]

    def getSof(self, data):
        return data["metadata"]["sof"]

    def getTrackName(self, data):
        return data["metadata"]["track"]

    def getSessionTime(self, data):
        return data["metadata"]["session_time"]

    def getSeriesName(self, data):
        return data["metadata"]["series_name"]

    def getSubsessionId(self, data):
        return data["metadata"]["subsession_id"]

    def getNumberOfLaps(self, data):
        return len(data["drivers"][0]["laps"])

    def getDriverNames(self, data):
        return [driver["name"] for driver in data["drivers"]]

    def getUserDriverIndex(self, driverNames, name):
        return driverNames.index(name)

    def calculateyMinYMax(self, data):

        drivers = self.getDrivers(data)
        numberOFLaps = self.getNumberOfLaps(data)

        deltasAllLaps = np.array([driver["deltaToTarget"] for driver in drivers]).flatten()
        deltasAllLaps = deltasAllLaps[~np.isnan(deltasAllLaps)]

        largestNegativeDelta = min(deltasAllLaps)
        yMin = self.roundDown(largestNegativeDelta)

        deltasLastLap = np.array(
            [driver["deltaToTarget"][numberOFLaps - 1] for driver in drivers])
        deltasLastLap = deltasLastLap[~np.isnan(deltasLastLap)]

        yMax = np.quantile(deltasAllLaps, 0.9)
        # yMax = self.roundUp(topXPercent)

        return int(yMin), int(yMax)

    def roundDown(self, delta):
        # round down to the next 0.5 step and subtract 5
        return math.floor(delta * 2) / 2 - 1

    def getDrivers(self, data):
        return data["drivers"]
