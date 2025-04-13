from _backend.application.session.sessionmanager import SessionManager, checkForBadServerResponse
from _backend.application.utils.publicappexception import PublicAppException


async def searchDriverId(name: str, sessionManager: SessionManager):

    async with sessionManager.session.get('https://members-ng.iracing.com/data/lookup/drivers', params={"search_term": name}) as response1:
        await checkForBadServerResponse(response1)
        json = await response1.json()
        link = json["link"]

    async with sessionManager.session.get(link) as response2:
        await checkForBadServerResponse(response2)
        data = await response2.json()

    if len(data) == 0:
        raise PublicAppException(f"No user found on iRacing with name '{name}'")

    member_id = data[0]["cust_id"]
    return member_id

