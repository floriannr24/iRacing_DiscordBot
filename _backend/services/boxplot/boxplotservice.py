import copy

from _api.api import loadSessionFromDatabase, saveSessionToDatabase
from _backend.iracingapi.apicalls.recent_races import requestSubessionId
from _backend.iracingapi.dataprocessors.dataprocessor import Dataprocessor
from _backend.services.boxplot.boxplotdata import BoxplotData
from _backend.services.boxplot.boxplotdiagram import BoxplotDiagram
from _backend.services.boxplot.boxplotoptions import BoxplotOptions
from _bot.botUtils import BotParams


class BoxplotService:

    def __init__(self):
        pass

    async def getBoxplotImage(self, sessionManager, params: BotParams, boxplotOptions: BoxplotOptions):
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

        boxplotData = self.initBoxplotData(data, boxplotOptions)

        fileLocation = BoxplotDiagram(boxplotData=boxplotData, boxplotOptions=boxplotOptions).draw()

        return fileLocation

    def initBoxplotData(self, originalData, options: BoxplotOptions):

        data = self.prepareData(originalData, options.showDiscDisq)

        userDriverName = self.getUserDriverName(data)
        driverNames = self.getDriverNames(data)

        bpdata = BoxplotData()
        bpdata.driverNames = driverNames
        bpdata.finishPositions = self.getFinishPositions(data)
        bpdata.sof = self.getSof(data)
        bpdata.carIds = self.getCarIds(data)
        bpdata.seriesName = self.getSeriesName(data)
        bpdata.trackName = self.getTrackName(data)
        bpdata.sessionTime = self.getSessionTime(data)
        bpdata.subsessionId = self.getSubsessionId(data)
        bpdata.userDriverName = userDriverName
        bpdata.isRainySession = self.getRainInfo(data)
        bpdata.seriesId = self.getSeriesId(data)
        bpdata.laps = self.getLaps(data)
        bpdata.userDriverIndex = self.getUserDriverIndex(driverNames, userDriverName)
        bpdata.runningLaps = self.getRunningLaps(data)

        return bpdata

    def prepareData(self, originalData, showDiscDisq):
        data = copy.deepcopy(originalData)

        if not showDiscDisq:
            # always include userdriver, even if he disc/disq
            user_driver_id = originalData["metadata"]["user_driver_id"]
            data["drivers"] = [driver for driver in originalData["drivers"] if
                               driver["result_status"] == "Running" or driver["id"] == user_driver_id]

        return data

    def getLaps(self, data):
        return [driver["laps"] for driver in data["drivers"]]

    def getFinishPositions(self, data):
        return [driver["finish_position_in_class"] for driver in data["drivers"]]

    def getCarIds(self, data):
        return [driver["car_id"] for driver in data["drivers"]]

    def getSeriesName(self, data):
        return data["metadata"]["series_name"]

    def getUserDriverName(self, data):
        return data["metadata"]["user_driver_name"]

    def getSof(self, data):
        return data["metadata"]["sof"]

    def getTrackName(self, data):
        return data["metadata"]["track"]

    def getSessionTime(self, data):
        return data["metadata"]["session_time"]

    def getSubsessionId(self, data):
        return data["metadata"]["subsession_id"]

    def getUserDriverIndex(self, driverNames, name):
        return driverNames.index(name)

    def getSeriesId(self, data):
        return data["metadata"]["series_id"]

    def getRainInfo(self, data):
        return data["metadata"]["is_rainy_session"]

    def getRunningLaps(self, data):
        # all laps of drivers whose final status is not "Disqualified" or "Disconnected"
        return [driver["laps"] for driver in data["drivers"] if driver["result_status"] == "Running"]

    def getDriverNames(self, data):
        return [driver["name"] for driver in data["drivers"]]
