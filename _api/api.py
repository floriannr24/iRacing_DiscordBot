import asyncio

from _api.apiDatabase import getSessionForUser, storeSessionForUser
from _backend.application.dataprocessors.dataprocessor import Dataprocessor
from _backend.application.diagrams.boxplot import BoxplotDiagram
from _backend.application.diagrams.delta import DeltaDiagram
from _backend.application.diagrams.laptime import LaptimeDiagram
from _backend.application.diagrams.median import MedianDiagram
from _backend.application.service.recent_races import requestSubessionId
from _backend.application.session.sessionmanager import SessionManager


async def getBoxplotImage(**kwargs):

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

async def getMedianImage(**kwargs):
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

    fileLocation = MedianDiagram(data, showRealName=showRealName).draw()
    return fileLocation

async def getDeltaImage(**kwargs):
    selectedSession = kwargs.get('selectedSession', None)
    subsessionId = kwargs.get('subsessionId', None)
    userId = kwargs.get('userId', None)
    showRealName = kwargs.get('showRealName', None)
    sessionManager: SessionManager = kwargs.get("sessionManager")

    # sessionManager.newSession()

    if not subsessionId:
        subsessionId = await requestSubessionId(userId, selectedSession, sessionManager)

    dataInDatabase = loadSessionFromDatabase(userId, subsessionId)

    if dataInDatabase:
        data = dataInDatabase
        # await sessionManager.session.close()
    else:
        data = await Dataprocessor().getData(userId, subsessionId, sessionManager)
        saveSessionToDatabase(userId, subsessionId, data)

    fileLocation = DeltaDiagram(data, showRealName=showRealName).draw()
    return fileLocation

async def getLaptimeImage(**kwargs):
    selectedSession = kwargs.get('selectedSession', None)
    subsessionId = kwargs.get('subsessionId', None)
    userId = kwargs.get('userId', None)
    showRealName = kwargs.get('showRealName', None)
    sessionManager: SessionManager = kwargs.get("sessionManager")

    # sessionManager.newSession()

    if not subsessionId:
        subsessionId = await requestSubessionId(userId, selectedSession, sessionManager)

    dataInDatabase = loadSessionFromDatabase(userId, subsessionId)

    if dataInDatabase:
        data = dataInDatabase
        # await sessionManager.session.close()
    else:
        data = await Dataprocessor().getData(userId, subsessionId, sessionManager)
        saveSessionToDatabase(userId, subsessionId, data)

    fileLocation = LaptimeDiagram(data, showRealName=showRealName).draw()
    return fileLocation

def loadSessionFromDatabase(custId, sessionId):
    return getSessionForUser(custId, sessionId)

def saveSessionToDatabase(custId, sessionId, data):
    storeSessionForUser(custId, sessionId, data)

asyncio.run(getDeltaImage(userId=817320, subsessionId=73095230))
# asyncio.run(getDeltaImage(userId=817320, subsessionId=72801368))
# asyncio.run(getDeltaImage(userId=817320, subsessionId=72797931))
# asyncio.run(getDeltaImage(userId=817320, subsessionId=73019927)) #bug, userdriver 2nd
# asyncio.run(getMedianData(userId=817320, subsessionId=72777447)) #rework
# asyncio.run(getMedianData(userId=817320, subsessionId=72779496)) #rework