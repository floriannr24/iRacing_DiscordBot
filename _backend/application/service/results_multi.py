import aiohttp

from _backend.application.session.sessionmanager import SessionManager, handleServerException


async def requestResultsMulti(subsession: int, manager: SessionManager):

    async with manager.session.get('https://members-ng.iracing.com/data/results/get', params={"subsession_id": subsession, "simsession_number": "0"}) as response1:
        json = await response1.json()
        handleServerException(response1, json)
        link = json["link"]
        async with manager.session.get(link) as response2:
            data = await response2.json()
            handleServerException(response2, data)
            return data