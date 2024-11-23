from Demos.win32ts_logoff_disconnected import session

from _api.apiDatabase import getSessionForUser, storeSessionForUser
from _backend.application.dataprocessors.dataprocessor import Dataprocessor
from _backend.application.diagrams.boxplot import BoxplotDiagram
from _backend.application.diagrams.median import MedianDiagram
from _backend.application.service.recent_races import requestSubessionId
from _backend.application.session.sessionmanager import SessionManager


async def getBoxplotData(**kwargs):

    selectedSession = kwargs.get('selectedSession', None)
    subsessionId = kwargs.get('subsessionId', None)
    userId = kwargs.get('userId', None)
    showRealName = kwargs.get('showRealName', None)
    showLaptimes = kwargs.get('showLaptimes', None)
    sessionManager: SessionManager = kwargs.get("sessionManager")

    sessionManager.newSession()

    if not subsessionId:
        subsessionId = await requestSubessionId(userId, selectedSession, sessionManager)

    dataInDatabase = loadSessionFromDatabase(userId, subsessionId)

    if dataInDatabase:
        data = dataInDatabase
        await sessionManager.session.close()
    else:
        data = await Dataprocessor().getData(userId, subsessionId, sessionManager)
        saveSessionToDatabase(userId, subsessionId, data)

    # write_file_content(boxplotData)
    # data = read_file_content()
    fileLocation = BoxplotDiagram(data, showRealName=showRealName, showLaptimes=showLaptimes).draw()
    return fileLocation

async def getDeltaData(**kwargs):
    pass

async def getMedianData(**kwargs):
    selectedSession = kwargs.get('selectedSession', None)
    subsessionId = kwargs.get('subsessionId', None)
    userId = kwargs.get('userId', None)
    showRealName = kwargs.get('showRealName', None)
    sessionManager: SessionManager = kwargs.get("sessionManager")

    sessionManager.newSession()

    if not subsessionId:
        subsessionId = await requestSubessionId(userId, selectedSession, sessionManager)

    dataInDatabase = loadSessionFromDatabase(userId, subsessionId)

    if dataInDatabase:
        data = dataInDatabase
        await sessionManager.session.close()
    else:
        data = await Dataprocessor().getData(userId, subsessionId, sessionManager)
        saveSessionToDatabase(userId, subsessionId, data)

    # boxplotData = read_file_content()
    fileLocation = MedianDiagram(data, showRealName=showRealName).draw()
    return fileLocation

def loadSessionFromDatabase(custId, sessionId):
    return getSessionForUser(custId, sessionId)

def saveSessionToDatabase(custId, sessionId, data):
    storeSessionForUser(custId, sessionId, data)

# asyncio.run(getMedianData(userId=817320, selectedSession=-1))
