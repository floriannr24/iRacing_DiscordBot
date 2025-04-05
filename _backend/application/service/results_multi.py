import os
import aiohttp
from _backend.application.session.sessionmanager import SessionManager, checkForBadServerResponse

async def requestResultsMulti(subsession: int, sessionManager: SessionManager):

    _BOXED = os.environ.get("BOXED", False) == "True"

    if not _BOXED:
        async with sessionManager.session.get('https://members-ng.iracing.com/data/results/get', params={"subsession_id": subsession, "simsession_number": "0"}) as response1:
            json = await response1.json(content_type=None)
            checkForBadServerResponse(response1, json)
            link = json["link"]

        async with sessionManager.session.get(link) as response2:
            data = await response2.json(content_type=None)
            checkForBadServerResponse(response2, data)

    else:
        return None

    return data