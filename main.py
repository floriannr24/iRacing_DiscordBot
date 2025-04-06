from _bot.bot import DiscordBot
import os
from dotenv import load_dotenv

if __name__ == "__main__":

    # Determine .env (default to development)
    environment = os.environ.get("APP_ENV", "development")
    load_dotenv(f".env.{environment}")

    if environment == "production":
        bot = DiscordBot()
        bot.run()
    else:
        raise Exception("No production run config found")