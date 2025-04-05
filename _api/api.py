from _api.apiDatabase import apiDatabase
from _backend.application.dataprocessors.dataprocessor import Dataprocessor
from _backend.application.diagrams.boxplot import BoxplotDiagram
from _backend.application.diagrams.delta import DeltaDiagram
from _backend.application.diagrams.laptime import LaptimeDiagram
from _backend.application.diagrams.median import MedianDiagram
from _backend.application.service.driverid_search import searchDriverId
from _backend.application.service.drivername_search import searchDriverName
from _backend.application.service.recent_races import requestSubessionId
from _backend.application.session.sessionmanager import SessionManager

async def findAndSaveIdForName(sessionManager: SessionManager, member_name: str, discord_id: int):
    member_id = await searchDriverId(member_name, sessionManager)
    member_id_database = apiDatabase().getMemberIdForDiscordId(discord_id)

    if member_id_database is None:
        apiDatabase().storeNewMemberId(member_id, discord_id)
    else:
        apiDatabase().updateMemberId(member_id, discord_id)

    return member_id

async def findNameAndSaveIdForId(sessionManager: SessionManager, member_id: int, discord_id: int):
    member_name = await searchDriverName(member_id, sessionManager)
    member_id_database = apiDatabase().getMemberIdForDiscordId(discord_id)

    if member_id_database is None:
        apiDatabase().storeNewMemberId(member_id, discord_id)
    else:
        apiDatabase().updateMemberId(member_id, discord_id)

    return member_name

async def getBoxplotImage(sessionManager, params):
    subsessionId = params.get("subsession_id", None)
    selectedSession = params.get("selected_session", None)
    userId = params.get("memberId", None)

    if not subsessionId:
        subsessionId = await requestSubessionId(userId, selectedSession, sessionManager)

    dataInDatabase = loadSessionFromDatabase(userId, subsessionId)

    if dataInDatabase:
        data = dataInDatabase
        await sessionManager.session.close()
    else:
        data = await Dataprocessor().getData(userId, subsessionId, sessionManager)
        saveSessionToDatabase(userId, subsessionId, data)

    fileLocation = BoxplotDiagram(data, params).draw()

    return fileLocation

async def getMedianImage(sessionManager, params):
    subsessionId = params.get("subsession_id", None)
    selectedSession = params.get("selected_session", None)
    userId = params.get("memberId", None)

    if not subsessionId:
        subsessionId = await requestSubessionId(userId, selectedSession, sessionManager)

    dataInDatabase = loadSessionFromDatabase(userId, subsessionId)

    if dataInDatabase:
        data = dataInDatabase
        await sessionManager.session.close()
    else:
        data = await Dataprocessor().getData(userId, subsessionId, sessionManager)
        saveSessionToDatabase(userId, subsessionId, data)

    fileLocation = MedianDiagram(data, params).draw()

    return fileLocation

async def getDeltaImage(cookieJar, params):
    subsessionId = params.get("subsession_id", None)
    selectedSession = params.get("selected_session", None)
    userId = params.get("memberId", None)

    sessionManager = SessionManager()
    sessionManager.newSession(cookieJar)

    if not subsessionId:
        subsessionId = await requestSubessionId(userId, selectedSession, sessionManager)

    dataInDatabase = loadSessionFromDatabase(userId, subsessionId)

    if dataInDatabase:
        data = dataInDatabase
        await sessionManager.session.close()
    else:
        data = await Dataprocessor().getData(userId, subsessionId, sessionManager)
        saveSessionToDatabase(userId, subsessionId, data)

    fileLocation = DeltaDiagram(data, params).draw()
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
    return apiDatabase().getSessionDataForUser(custId, sessionId)

def saveSessionToDatabase(custId, sessionId, data):
    apiDatabase().storeSessionDataForUser(custId, sessionId, data)