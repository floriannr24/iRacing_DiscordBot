import json
import os
from pathlib import Path

from _backend.application.session.sessionmanager import SessionManager, checkForBadServerResponse
from dev.devutils.localData import saveToJson, loadFromJson


async def requestResultsMulti(subsession: int, sessionManager: SessionManager):

    _BOXED = os.environ.get("BOXED", False) == "True"
    _SAVE_DATA = os.environ.get("SAVE_DATA", False) == "True"
    data = None

    if not _BOXED:
        async with sessionManager.session.get('https://members-ng.iracing.com/data/results/get', params={"subsession_id": subsession, "simsession_number": "0"}) as response1:
            await checkForBadServerResponse(response1)
            jsonFile = await response1.json(content_type=None)
            link = jsonFile["link"]

        async with sessionManager.session.get(link) as response2:
            await checkForBadServerResponse(response2)
            data = await response2.json(content_type=None)

        if _SAVE_DATA:
            saveToJson(data, subsession, "results_multi")

        return data

    else:
        data = loadFromJson(subsession, "results_multi")
        return data


