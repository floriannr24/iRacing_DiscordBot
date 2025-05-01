import os

from dotenv import load_dotenv

from _bot.bot import DiscordBot

if __name__ == "__main__":

    # Determine .env (defaults to development)
    environment = os.environ.get("APP_ENV", "development")
    load_dotenv(f".env.{environment}")

    if environment == "production":

        for key, value in os.environ.items():
            print(f"{key}={value}")

        bot = DiscordBot()
        bot.run()

    else:
        raise Exception("No production run config found")