import aiohttp
from _backend.application.session.sessionmanager import SessionManager, checkForBadServerResponse

async def requestResultsMulti(subsession: int, sessionManager: SessionManager):

    async with sessionManager.session.get('https://members-ng.iracing.com/data/results/get', params={"subsession_id": subsession, "simsession_number": "0"}) as response1:
        json = await response1.json()
        checkForBadServerResponse(response1, json)
        link = json["link"]

    async with sessionManager.session.get(link) as response2:
        data = await response2.json()
        checkForBadServerResponse(response2, data)

    return data