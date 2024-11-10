
from _backend.application.sessionbuilder.sessionmanager import SessionManager


async def requestSubessionId(cust_id, selectedSession):

    # getting index starting from the back of the list via arg "selectedSession".
    # SelectedSession is negative (-1 for the last race, -2 for the 2nd to last race etc.)
    async with SessionManager() as manager:
        async with manager.session.get('https://members-ng.iracing.com/data/stats/member_recent_races', params={'cust_id': cust_id}) as response:
            json = await response.json()
            link = json["link"]
            async with manager.session.get(link) as response1:
                data = await response1.json()

    if not data:
        raise Exception("No data found for member_id")

    # todo: move to discord bot
    if -11 < selectedSession < 0:
        index =  (-1) * selectedSession - 1
    else:
        raise Exception("Index not between -1 and 11")

    listOfRaces = data["races"]
    if len(listOfRaces) <= index:
        raise Exception(f"Not enough races found for selectedSession={selectedSession}. Number of races found: {len(listOfRaces)}")

    subsession_id = data["races"][index]["subsession_id"]
    return subsession_id