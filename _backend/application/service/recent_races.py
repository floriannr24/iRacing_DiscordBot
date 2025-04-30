import os

from _backend.application.session.sessionmanager import SessionManager, checkForBadServerResponse
from _backend.application.utils.publicappexception import PublicAppException
from dev.devutils.localData import saveToJson, loadFromJson


async def requestSubessionId(cust_id, selectedSession, sessionManager: SessionManager):

    # getting a specific subsessionId via argument "selectedSession"
    # Argument is negative and traverses the list of recent races backwards. -1 for the latest race, -2 for the one before that etc.

    _BOXED = os.environ.get("BOXED", False) == "True"
    _SAVE_DATA = os.environ.get("SAVE_DATA", False) == "True"

    if not _BOXED:
        async with sessionManager.session.get('https://members-ng.iracing.com/data/stats/member_recent_races', params={'cust_id': cust_id}) as response1:
            await checkForBadServerResponse(response1)
            jsonFile = await response1.json()
            link = jsonFile["link"]

        async with sessionManager.session.get(link) as response2:
            await checkForBadServerResponse(response2)
            data = await response2.json()

        if _SAVE_DATA:
            saveToJson(data, cust_id, "member_recent_races")
    else:
        data = loadFromJson(cust_id, "member_recent_races")

    index =  (-1) * selectedSession - 1

    listOfRaces = data["races"]
    if len(listOfRaces) <= index:
        raise PublicAppException(f"Not enough races found for 'member_id'={cust_id} and 'selectedSession'={selectedSession}. Number of races found: {len(listOfRaces)}")

    subsession_id = data["races"][index]["subsession_id"]
    return subsession_id

