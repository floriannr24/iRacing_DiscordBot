import asyncio
from pathlib import Path
from _backend.application.session.sessionmanager import SessionManager

async def requestCarLogos():
    sessionManager = SessionManager()
    cookie = await sessionManager.authenticateAndGetCookie()

    sessionManager = SessionManager()
    sessionManager.newSession(cookie)

    response1 = await sessionManager.session.get('https://members-ng.iracing.com/data/car/assets')
    json = await response1.json()
    link = json["link"]

    response2 = await sessionManager.session.get(link)
    data = await response2.json()

    relativeImageUrl = "https://images-static.iracing.com/"

    for car_id in data:
        filename = data[car_id]["logo"]
        if (filename):
            await downloadAndSaveImage(relativeImageUrl + filename, car_id, "cars", sessionManager)

    await sessionManager.session.close()

async def requestSeriesLogos():

    sessionManager = SessionManager()
    cookie = await sessionManager.authenticateAndGetCookie()

    sessionManager = SessionManager()
    sessionManager.newSession(cookie)

    response1 = await sessionManager.session.get('https://members-ng.iracing.com/data/series/assets')
    json = await response1.json()
    link = json["link"]

    response2 = await sessionManager.session.get(link)
    data = await response2.json()

    relativeImageUrl = "https://images-static.iracing.com/img/logos/series/"

    for series_id in data:
        filename = data[series_id]["logo"]
        if (filename):
            await downloadAndSaveImage(relativeImageUrl + filename, series_id, "series", sessionManager)

    await sessionManager.session.close()

async def downloadAndSaveImage(url, id, type, sessionmanager):

    folderPath = Path().absolute().parent / 'resources' / 'images' / f'{type}_download'
    imagePath = f"{str(folderPath / id)}.png"

    response = await sessionmanager.session.get(url)
    image_content = await response.read()

    with open(imagePath, 'wb') as f:
        f.write(image_content)

async def requestTrackmaps():

    sessionManager = SessionManager()
    cookie = await sessionManager.authenticateAndGetCookie()

    sessionManager = SessionManager()
    sessionManager.newSession(cookie)

    response1 = await sessionManager.session.get('https://members-ng.iracing.com/data/track/assets')
    json = await response1.json()
    link = json["link"]

    response2 = await sessionManager.session.get(link)
    data = await response2.json()

    for track_id in data:
        relativeImageUrl = data[track_id]["track_map"]
        filename = "active.svg"
        if filename and relativeImageUrl:
            await downloadAndSaveSVG(relativeImageUrl + filename, track_id, "tracks", sessionManager)

    await sessionManager.session.close()

async def downloadAndSaveSVG(url, id, type, sessionmanager):
    folderPath = Path().absolute().parent / 'resources' / 'images' / f'{type}_download'
    svgPath = f"{str(folderPath / id)}.svg"

    response = await sessionmanager.session.get(url)
    image_content = await response.read()

    with open(svgPath, 'wb') as f:
        f.write(image_content)

# asyncio.run(requestSeriesLogos())
# asyncio.run(requestCarLogos())
# asyncio.run(requestTrackmaps())