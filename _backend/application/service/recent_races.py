from _backend.application.session.sessionmanager import SessionManager, handleServerException
from _backend.application.utils.publicappexception import PublicAppException


async def requestSubessionId(cust_id, selectedSession, sessionManager: SessionManager):

    # getting index starting from the back of the list via arg "selectedSession".
    # SelectedSession is negative (-1 for the last race, -2 for the 2nd to last race etc.)
    async with sessionManager as manager:
        async with manager.session.get('https://members-ng.iracing.com/data/stats/member_recent_races', params={'cust_id': cust_id}) as response1:
            json = await response1.json()
            handleServerException(response1, json)
            link = json["link"]
            async with manager.session.get(link) as response2:
                data = await response2.json()
                handleServerException(response2, data)

    index =  (-1) * selectedSession - 1

    listOfRaces = data["races"]
    if len(listOfRaces) <= index:
        raise PublicAppException(f"Not enough races found for 'member_id'={cust_id} and 'selectedSession'={selectedSession}. Number of races found: {len(listOfRaces)}")

    subsession_id = data["races"][index]["subsession_id"]
    return subsession_id