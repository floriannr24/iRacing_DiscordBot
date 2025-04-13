import asyncio
import os

from _backend.application.session.sessionmanager import SessionManager, checkForBadServerResponse
from dev.devutils.localData import saveToJson, loadFromJson


async def requestLapsMulti(subsession: int, sessionManager: SessionManager):

    _BOXED = os.environ.get("BOXED", False) == "True"
    _SAVE_DATA = os.environ.get("SAVE_DATA", False) == "True"
    data = None

    if not _BOXED:

        async with sessionManager.session.get('https://members-ng.iracing.com/data/results/lap_chart_data', params={"subsession_id": subsession, "simsession_number": "0"}) as response1:
            await checkForBadServerResponse(response1)
            jsonFile = await response1.json(content_type=None)
            link = jsonFile["link"]

        async with sessionManager.session.get(link) as response2:
            await checkForBadServerResponse(response2)
            data = await response2.json(content_type=None)
            base_download_url = data["chunk_info"]["base_download_url"]
            chunk_file_names = data["chunk_info"]["chunk_file_names"]

            dataLinks = [base_download_url + chunk_name for chunk_name in chunk_file_names]

        async with sessionManager.session as s:
            tasks = [requestChunkData(link, s) for link in dataLinks]
            result = await asyncio.gather(*tasks)
            data = [item for sublist in result for item in sublist]

        if _SAVE_DATA:
            saveToJson(data, subsession, "laps_multi")

        return data

    else:
        data = loadFromJson(subsession, "laps_multi")
        return data

async def requestChunkData(link: str, session):
    async with session.get(link) as response:
        await checkForBadServerResponse(response)
        json = await response.json(content_type=None)
        return json
