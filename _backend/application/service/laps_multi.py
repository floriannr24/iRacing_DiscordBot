import asyncio

import aiohttp
from Demos.security.sspi.socket_server import serve

from _backend.application.session.sessionmanager import SessionManager, handleServerException


async def requestLapsMulti(subsession: int, sessionManager: SessionManager):

    async with sessionManager as manager:
        async with manager.session.get('https://members-ng.iracing.com/data/results/lap_chart_data', params={"subsession_id": subsession, "simsession_number": "0"}) as response1:
            json = await response1.json()
            handleServerException(response1, json)
            link = json["link"]
            async with manager.session.get(link) as response2:
                data = await response2.json()
                handleServerException(response2, data)
                base_download_url = data["chunk_info"]["base_download_url"]
                chunk_file_names = data["chunk_info"]["chunk_file_names"]

                dataLinks = [base_download_url + chunk_name for chunk_name in chunk_file_names]
                async with manager.session as s:
                    tasks = [requestChunkData(link, s) for link in dataLinks]
                    result = await asyncio.gather(*tasks)
                    data = [item for sublist in result for item in sublist]
                    return data

async def requestChunkData(link: str, session):
    async with session.get(link) as response:
        json = await response.json()
        handleServerException(response, json)
        return json
