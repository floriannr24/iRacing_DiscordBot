import asyncio

from _backend.application.session.sessionmanager import SessionManager, checkForBadServerResponse
from _backend.application.utils.publicappexception import PublicAppException


async def requestSubessionId(cust_id, selectedSession, sessionManager: SessionManager):

    # getting a specific subsessionId via argument "selectedSession"
    # Argument is negative and traverses the list of recent races backwards. -1 for the latest race, -2 for the second to last race etc.

    async with sessionManager.session.get('https://members-ng.iracing.com/data/stats/member_recent_races', params={'cust_id': cust_id}) as response1:
        json = await response1.json()
        checkForBadServerResponse(response1, json)
        link = json["link"]

    async with sessionManager.session.get(link) as response2:
        data = await response2.json()
        checkForBadServerResponse(response2, data)

    index =  (-1) * selectedSession - 1

    listOfRaces = data["races"]
    if len(listOfRaces) <= index:
        raise PublicAppException(f"Not enough races found for 'member_id'={cust_id} and 'selectedSession'={selectedSession}. Number of races found: {len(listOfRaces)}")

    subsession_id = data["races"][index]["subsession_id"]
    return subsession_id