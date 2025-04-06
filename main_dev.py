import asyncio
from http.cookiejar import CookieJar

from _api.api import getDeltaImage, getBoxplotImage
from _backend.application.session.sessionmanager import SessionManager
from _bot.bot import DiscordBot
import os
from dotenv import load_dotenv


async def runBackend():

    #boxed
    await getBoxplotImage(None, params={"memberId": 817320, "subsession_id": 73872593})
    # asyncio.run(getBoxplotImage(None, params={"memberId": 817320, "subsession_id": 73303628}))
    # asyncio.run(getDeltaImage(userId=817320, subsessionId=72801368))
    # asyncio.run(getDeltaImage(userId=817320, subsessionId=72797931))
    # asyncio.run(getDeltaImage(userId=817320, subsessionId=73019927)) #bug, userdriver 2nd
    # asyncio.run(getMedianData(userId=817320, subsessionId=72777447)) #rework
    # asyncio.run(getMedianData(userId=817320, subsessionId=72779496)) #rework

async def initSessionForDev():
    sessionManager = SessionManager()
    cookie = await sessionManager.authenticateAndGetCookie()
    sessionManager.newSession(cookie)
    return sessionManager

if __name__ == "__main__":

    # Determine .env (default to development)
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