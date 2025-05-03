from _backend.iracingapi.session.sessionmanager import SessionManager, checkForBadServerResponse
from _backend.iracingapi.utils.publicappexception import PublicAppException


async def searchDriverName(id: int, sessionManager: SessionManager):

    async with sessionManager.session.get('https://members-ng.iracing.com/data/member/get', params={"cust_ids": id}) as response1:
        await checkForBadServerResponse(response1)
        json = await response1.json()
        link = json["link"]

    async with sessionManager.session.get(link) as response2:
        await checkForBadServerResponse(response2)
        data = await response2.json()

    if len(data["members"]) == 0:
        raise PublicAppException(f"No user found on iRacing with id '{id}'")

    member_id = data["members"][0]["display_name"]
    return member_id

