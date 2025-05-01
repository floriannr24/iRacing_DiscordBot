import asyncio
import os

from dotenv import load_dotenv

from _api.api import getBoxplotImage
from _backend.application.session.sessionmanager import SessionManager
from _bot.bot import DiscordBot


async def runBackend():

    sessionManager = await initSessionForDev()
    await getBoxplotImage(sessionManager, params={"memberId": 817320, "selected_session": -1, "show_laptimes": True})
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

    foundConfig = load_dotenv(".env.development")

    _DISABLE_DISCORD_FRONTEND = os.environ.get("DISABLE_DISCORD_FRONTEND", False) == "True"

    if foundConfig:
        if _DISABLE_DISCORD_FRONTEND:
            asyncio.run(runBackend())
        else:
            bot = DiscordBot()
            bot.run()
    else:
        raise Exception("No development run config found")
