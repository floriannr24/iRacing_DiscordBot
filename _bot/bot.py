import asyncio
import os
import time
import discord
from discord import app_commands
from discord.ext import commands, tasks
import discord.app_commands
from _api.api import getMedianImage, getBoxplotImage, getDeltaImage, findNameAndSaveIdForId, findAndSaveIdForName
from _api.apiDatabase import apiDatabase
from _backend.application.diagrams.delta import ReferenceMode, SelectionMode
from _backend.application.session.sessionmanager import SessionManager
from _bot import botUtils
from _bot.botUtils import start_timer, end_timer, closeSession


class DiscordBot():
    def __init__(self):
        self.token = os.environ.get("TOKEN")
        self.channel_id = int(os.environ.get("CHANNEL_ID")) if os.environ.get("CHANNEL_ID") else None
        self.bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())
        self.apiDatabase = apiDatabase()
        self.cookieJar = None

        # register event handlers
        self.bot.event(self.setup_hook)
        self.bot.event(self.on_ready)

        # register commands
        self.register_commands()

    async def setup_hook(self):
        self.authenticate.start()

    async def on_ready(self):
        channel = self.bot.get_channel(self.channel_id)
        await channel.send("Bot has successfully started!")

        try:
            synced_commands = await self.bot.tree.sync()
            print(f"Synced {len(synced_commands)} commands")
        except Exception as e:
            print("Error while syncing application commands", e)

    @tasks.loop(minutes=60)
    async def authenticate(self):
        sessionManager = SessionManager()
        self.cookieJar = await sessionManager.authenticateAndGetCookie()

    def register_commands(self):
        self.cmdRegister()
        self.cmdDelete()
        self.cmdBoxplot()
        self.cmdMedian()
        # self.cmdDelta()

    def run(self):
        self.bot.run(self.token)

    def cmdRegister(self):
        @self.bot.tree.command(name="register", description="Enter your 'iracing_name' OR your 'iracing_id' to use the bot.")
        @app_commands.describe(
            iracing_name="Your iRacing name.",
            iracing_id="Your iRacing member id."
        )
        async def register(interaction: discord.Interaction,
                           iracing_name: str | None,
                           iracing_id: int | None):

            sessionManager = SessionManager()
            sessionManager.newSession(self.cookieJar)
            discordId = interaction.user.id

            try:

                start_time = await start_timer()

                if iracing_id is None and iracing_name is None:
                    await interaction.response.send_message(embed=botUtils.Messages.ERROR_NO_CREDENTIALS_PROVIDED.value, ephemeral=True)
                    return

                if iracing_id:
                    iracing_name = await asyncio.wait_for(findNameAndSaveIdForId(sessionManager, iracing_id, discordId), 20)

                if iracing_id is None and iracing_name:
                    iracing_id = await asyncio.wait_for(findAndSaveIdForName(sessionManager, iracing_name, discordId), 20)

                embed = botUtils.Messages.SUCCESS_CREDENTIALS_SAVED.value
                embed.description = f"Successfully saved user '{iracing_name}' with id '{iracing_id}'. You can now use the bot."
                await interaction.response.send_message(embed=embed, ephemeral=True)

                await end_timer(start_time)

                return

            except Exception as e:
                await botUtils.handleException(e, interaction)
            finally:
                await closeSession(sessionManager)

    def cmdDelete(self):
        @self.bot.tree.command(name="delete", description="Delete your user from the bot.")
        async def register(interaction: discord.Interaction):

            sessionManager = SessionManager()
            sessionManager.newSession(self.cookieJar)
            discordId = interaction.user.id

            try:

                start_time = await start_timer()

                memberIdDatabase = self.apiDatabase.getMemberIdForDiscordId(discordId)

                if memberIdDatabase is None :
                    await interaction.response.send_message(embed=botUtils.Messages.ERROR_NOT_YET_REGISTERED.value, ephemeral=True)
                    return

                apiDatabase().deleteMember(discordId)

                await interaction.response.send_message(embed=botUtils.Messages.SUCCESS_CREDENTIALS_DELETED.value, ephemeral=True)

                await end_timer(start_time)

                return

            except Exception as e:
                await botUtils.handleException(e, interaction)
            finally:
                await closeSession(sessionManager)

    def cmdBoxplot(self):
        @self.bot.tree.command(name="boxplot", description="Creates a boxplot out of a past iRacing session.")
        @app_commands.describe(
            subsession_id="Id of the subsession to be analyzed.",
            selected_session="One of your last ten races. '-1' for your latest race, '-2' for the race before that etc.",
            show_real_name="Display your real name in the diagram. Switched off by default",
            show_laptimes="Display laptimes. Switched off by default.",
            show_discdisq="Display disconnected/disqualified drivers. Switched off by default."
        )
        @app_commands.choices(selected_session=botUtils.getValuesSelectedSession())
        async def boxplot(interaction: discord.Interaction, subsession_id: int | None, selected_session: int | None,
                          show_real_name: bool | None,
                          show_laptimes: bool | None,
                          show_discdisq: bool | None):

            sessionManager = SessionManager()
            sessionManager.newSession(self.cookieJar)

            try:

                start_time = await start_timer()

                discordId = interaction.user.id
                memberIdDatabase = self.apiDatabase.getMemberIdForDiscordId(discordId)

                if not memberIdDatabase:
                    await interaction.response.send_message(embed=botUtils.Messages.ERROR_NO_MEMBER_ID_FOUND.value, ephemeral=True)
                    return

                # check if at least one of subsession_id or selected_session is set
                if subsession_id is None and selected_session is None:
                    await interaction.response.send_message(embed=botUtils.Messages.ERROR_SESSION_ID.value, ephemeral=True)
                    return

                # image response
                await interaction.response.defer()

                params = {"memberId": memberIdDatabase, "selected_session": selected_session, "subsession_id": subsession_id, "show_real_name": show_real_name, "show_laptimes": show_laptimes, "show_discdisq": show_discdisq}
                imagefileLocation = await asyncio.wait_for(getBoxplotImage(sessionManager, params), 20)

                file = discord.File(imagefileLocation)
                await interaction.followup.send(file=file)

                await end_timer(start_time)

                return

            except Exception as e:
                await botUtils.handleException(e, interaction)
            finally:
                await closeSession(sessionManager)


    def cmdMedian(self):
        @self.bot.tree.command(name="median", description="Compares your personal median to other drivers' median.")
        @app_commands.describe(
            subsession_id="Id of the subsession to be analyzed.",
            selected_session="One of your last ten races. '-1' for your latest race, '-2' for the race before that etc.",
            show_real_name="Display your real name in the diagram. Switched off by default",
            show_discdisq="Display disconnected/disqualified drivers. Switched off by default.",
            max_seconds="Limit the diagram to only show data up to x seconds. Useful for eliminating big outliers."
        )
        @app_commands.choices(selected_session=botUtils.getValuesSelectedSession())
        async def median(interaction: discord.Interaction, subsession_id: int | None, selected_session: int | None,
                         show_real_name: bool | None,
                         show_discdisq: bool | None,
                         max_seconds: float | None):

            sessionManager = SessionManager()
            sessionManager.newSession(self.cookieJar)

            try:

                start_time = await start_timer()

                discordId = interaction.user.id
                memberIdDatabase = self.apiDatabase.getMemberIdForDiscordId(discordId)

                if not memberIdDatabase:
                    await interaction.response.send_message(embed=botUtils.Messages.ERROR_NO_MEMBER_ID_FOUND.value, ephemeral=True)
                    return

                # check if at least one of subsession_id or selected_session is set
                if subsession_id is None and selected_session is None:
                    await interaction.response.send_message(embed=botUtils.Messages.ERROR_SESSION_ID.value, ephemeral=True)
                    return

                # image response
                await interaction.response.defer()

                params = {"memberId": memberIdDatabase, "selected_session": selected_session, "subsession_id": subsession_id, "show_real_name": show_real_name, "show_discdisq": show_discdisq, "max_seconds": max_seconds}
                imagefileLocation = await asyncio.wait_for(getMedianImage(sessionManager, params), 20)

                file = discord.File(imagefileLocation)
                await interaction.followup.send(file=file)

                await end_timer(start_time)

                return

            except Exception as e:
                await botUtils.handleException(e, interaction)
            finally:
                await closeSession(sessionManager)

    def cmdDelta(self):
        @self.bot.tree.command(name="delta", description="Shows the delta per lap to other drivers.")
        @app_commands.describe(
            subsession_id="Id of the subsession to be analyzed.",
            selected_session="One of your last ten races. '-1' for your latest race, '-2' for the race before that etc.",
            show_real_name="Display your real name in the diagram. Switched off by default",
            reference="Reference of the delta. Default is 'winner'",
            selection="How many drivers to display in your vicinity. Default is 'all'."
        )
        @app_commands.choices(selected_session=botUtils.getValuesSelectedSession(),
            reference=[app_commands.Choice(name="Winner", value=ReferenceMode.WINNER.value),
                       app_commands.Choice(name="Yourself", value=ReferenceMode.ME.value)
        ],
            selection=[app_commands.Choice(name="All", value=SelectionMode.ALL.value),
                       app_commands.Choice(name="5", value=SelectionMode.FIVE.value),
                       app_commands.Choice(name="7", value=SelectionMode.SEVEN.value),
                       app_commands.Choice(name="9", value=SelectionMode.NINE.value)
        ])
        async def delta(interaction: discord.Interaction, subsession_id: int | None, selected_session: int | None,
                        show_real_name: bool | None,
                        reference: int | None,
                        selection: int | None,
                        show_discdisq: bool | None):

            try:
                start_time = time.perf_counter()

                discordId = interaction.user.id
                memberIdDatabase = self.apiDatabase.getMemberIdForDiscordId(discordId)

                if not memberIdDatabase:
                    await interaction.response.send_message(embed=botUtils.Messages.ERROR_NO_MEMBER_ID_FOUND.value, ephemeral=True)
                    return

                # check if at least one of subsession_id or selected_session is set
                if subsession_id is None and selected_session is None:
                    await interaction.response.send_message(embed=botUtils.Messages.ERROR_SESSION_ID.value, ephemeral=True)
                    return

                # image response
                await interaction.response.defer()

                params = {"memberId": memberIdDatabase, "selected_session": selected_session, "subsession_id": subsession_id, "show_real_name": show_real_name, "reference": reference, "selection": selection, "show_discdisq": show_discdisq}
                imagefileLocation = await asyncio.wait_for(getDeltaImage(self.cookieJar, params), 20)
                file = discord.File(imagefileLocation)
                await interaction.followup.send(file=file)

                end_time = time.perf_counter()
                execution_time = end_time - start_time
                print(f"{execution_time:.2f} seconds")

                return

            except Exception as e:
                await botUtils.handleException(e, interaction)