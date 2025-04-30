import asyncio
from _api.api import getDeltaImage, getBoxplotImage, getMedianImage
from _backend.application.session.sessionmanager import SessionManager
from _backend.application.utils.publicappexception import PublicAppException
from _bot.bot import DiscordBot
import os
from dotenv import load_dotenv


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

    # Determine .env (defaults to development)
    environment = os.environ.get("APP_ENV", "development")
    load_dotenv(f".env.{environment}")

    _DISABLE_DISCORD_FRONTEND = os.environ.get("DISABLE_DISCORD_FRONTEND", False) == "True"

    if environment == "development":

        if _DISABLE_DISCORD_FRONTEND:
            asyncio.run(runBackend())
        else:
            bot = DiscordBot()
            bot.run()

    elif environment == "production":
        bot = DiscordBot()
        bot.run()
    else:
        raise Exception("No run config found")