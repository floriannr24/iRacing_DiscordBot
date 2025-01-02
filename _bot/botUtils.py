import asyncio
import traceback
from enum import Enum
import discord
from discord import app_commands
from _backend.application.utils.publicappexception import PublicAppException

class Messages(Enum):
    ERROR_NO_MEMBER_ID_FOUND = discord.Embed(title="❌ Error",
                                             description="You must register yourself first with /regsiter. The bot will remember your credentials for all subsequent commands.",
                                             color=0xFF0000)
    ERROR_NO_CREDENTIALS_PROVIDED = discord.Embed(title="❌ Error",
                                                  description="You must provide either 'iracing_id' or 'iracing_name'. Your credentials will be remembered by the bot for all following commands.",
                                                  color=0xFF0000)
    SUCCESS_CREDENTIALS_SAVED = discord.Embed(title="✅ Success", color=0x33CC33)
    ERROR_SESSION_ID = discord.Embed(title="❌ Error",
                                     description="You must provide either 'subsession_id' or 'selected_session'.",
                                     color=0xFF0000)
    ERROR_TIMEOUT = discord.Embed(title="⏱️ Timeout",
                                  description="The request timed out after 20 seconds. Please try again later.",
                                  color=0xFFA500)
    ERROR_PUBLIC = discord.Embed(title="❌ Error", color=0xFF0000)
    ERROR_INTERNAL = discord.Embed(title="❌ Error",
                                   description="Encountered an error while processing data.",
                                   color=0xFF0000)

def getValuesSelectedSession():
    return [
            app_commands.Choice(name="-1", value=-1),
            app_commands.Choice(name="-2", value=-2),
            app_commands.Choice(name="-3", value=-3),
            app_commands.Choice(name="-4", value=-4),
            app_commands.Choice(name="-5", value=-5),
            app_commands.Choice(name="-6", value=-6),
            app_commands.Choice(name="-7", value=-7),
            app_commands.Choice(name="-8", value=-8),
            app_commands.Choice(name="-9", value=-9),
            app_commands.Choice(name="-10", value=-10),
        ]

async def handleException(exception, interaction) -> None:
    if type(exception) == asyncio.TimeoutError:
        embed = Messages.ERROR_TIMEOUT
    elif type(exception) == PublicAppException:
        embed = Messages.ERROR_PUBLIC
        embed.value.description = exception.args[0]
    else: # Exception catch-all
        embed = Messages.ERROR_INTERNAL

    if type(exception) != PublicAppException:
        traceback.print_exc() # print stacktrace to console
        print(f"ERROR:\n"
            f"  type: {embed.name}\n"
            f"  user: {interaction.user} ({interaction.user.id}),\n"
            f"  data: {{command: '{interaction.data['name']}', options: '{interaction.data['options']} }}")

    await interaction.followup.send(embed=embed.value, ephemeral=True)
    return