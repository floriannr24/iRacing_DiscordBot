import asyncio
import os

from dotenv import load_dotenv

from _backend.iracingapi.session.sessionmanager import SessionManager
from _backend.services.median.medianoptions import MedianOptions
from _backend.services.median.medianservice import MedianService
from _bot.bot import DiscordBot
from _bot.botUtils import BotParams


async def runBackend():

    sessionManager = await initSessionForDev()
    await MedianService().getMedianImage(sessionManager,
                                         BotParams(817320, -1, None),
                                         MedianOptions(None, False, False))
    # await getMedianImage(None, params={"memberId": 817346, "subsession_id": 50967190, "max_seconds": 10})
    # await getMedianImage(None, params={"memberId": 817346, "subsession_id": 50826694})

    # for x in range(817330, 817350):
    #     for i in range (1,6):
    #         sessionManager = await initSessionForDev()
    #         time.sleep(3)
    #         try:
    #             print(x, -i)
    #             await getBoxplotImage(sessionManager, params={"memberId": x, "selected_session": -i})
    #         except PublicAppException as e:
    #             time.sleep(2)
    #             break
    #         finally:
    #             if sessionManager.session and not sessionManager.session.closed:
    #                 await sessionManager.session.close()

async def initSessionForDev():
    sessionManager = SessionManager()
    cookie = await sessionManager.authenticateAndGetCookie()
    sessionManager.newSession(cookie)
    return sessionManager

if __name__ == "__main__":

    configFound = load_dotenv(".env.development")

    _DISABLE_DISCORD_FRONTEND = os.environ.get("DISABLE_DISCORD_FRONTEND", False) == "True"

    if configFound:
        if _DISABLE_DISCORD_FRONTEND:
            asyncio.run(runBackend())
        else:
            bot = DiscordBot()
            bot.run()
    else:
        raise Exception("No development run config found")
