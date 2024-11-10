import aiohttp

from _backend.application.sessionbuilder.sessionmanager import SessionManager


async def requestResultsMulti(subsession: int, manager: SessionManager):
    # iRacingAPI
    async with manager.session.get('https://members-ng.iracing.com/data/results/get', params={"subsession_id": subsession, "simsession_number": "0"}) as response1:
        json = await response1.json()
        link = json["link"]
        async with manager.session.get(link) as response2:
            data = await response2.json()
            return data