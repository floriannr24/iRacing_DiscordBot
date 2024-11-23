import asyncio
from enum import Enum
import discord

from _api.api import getMedianData, getBoxplotData
from _api.apiDatabase import storeNewMemberId, updateMemberId
from _backend.application.session.sessionmanager import SessionManager


def extractMemberIdToUse(memberIdDatabase, member_id, status):
    if status == MemberIdStatus.FIRST_ID:
        result = member_id
    elif status == MemberIdStatus.CACHE_ID:
        result = memberIdDatabase
    elif status == MemberIdStatus.EXISTS_ALREADY_ID:
        result = memberIdDatabase
    elif status == MemberIdStatus.REFRESH_ID:
        result = member_id
    else:
        result = member_id  # fallback

    return result

def getMemberIdStatus(member_id, activeMemberIdDatabase):
    if not activeMemberIdDatabase and not member_id:
        result = MemberIdStatus.NO_ID

    elif not activeMemberIdDatabase and member_id:
        result = MemberIdStatus.FIRST_ID

    elif activeMemberIdDatabase and not member_id:
        result = MemberIdStatus.CACHE_ID

    elif activeMemberIdDatabase and member_id and member_id == activeMemberIdDatabase:
        result = MemberIdStatus.EXISTS_ALREADY_ID

    elif activeMemberIdDatabase and member_id and member_id != activeMemberIdDatabase:
        result = MemberIdStatus.REFRESH_ID

    else:
        raise RuntimeError(
            f"No id combination found for given member_id {member_id} and memberIdDatabase {activeMemberIdDatabase}")

    return result

async def createBoxplotImage(memberIdToUse, selected_session, show_real_name, subsession_id, show_laptimes, cookieJar):
    sessionManager = SessionManager()
    sessionManager.cookie_jar = cookieJar

    imagefileLocation = await asyncio.wait_for(getBoxplotData(userId=memberIdToUse, selectedSession=selected_session, subsessionId=subsession_id,
                       showRealName=show_real_name, showLaptimes=show_laptimes, sessionManager=sessionManager), 20)
    file = discord.File(imagefileLocation)
    return file

async def postMessage(file, interaction, status):
    if status == MemberIdStatus.FIRST_ID or status == MemberIdStatus.EXISTS_ALREADY_ID or status == MemberIdStatus.REFRESH_ID:
        await interaction.followup.send(file=file,
                                        content="⚠️ Hint: The bot will now remember your entered member_id. You don't have to provide it anymore.")
    else:
        await interaction.followup.send(file=file)

def updateDatabase(status, member_id, discordId):
    if status == MemberIdStatus.FIRST_ID:
        storeNewMemberId(member_id, discordId)
    if status == MemberIdStatus.REFRESH_ID:
        updateMemberId(member_id, discordId)

class MemberIdStatus(Enum):
    NO_ID = 1,                  # no member_id provided, no memberId in db -> error
    FIRST_ID = 2                # member_id provided, no memberId in db -> use new id and save in db
    CACHE_ID = 3                # no member_id provided, memberId found in db -> use id from db (caching)
    EXISTS_ALREADY_ID = 4       # member_id provided, member_id == memberId from db -> use from db
    REFRESH_ID = 5              # member_id provided, member_id != memberId from db -> replace old memberId with new member_id


async def createMedianImage(memberIdToUse, selected_session, show_real_name, subsession_id, cookieJar):
    sessionManager = SessionManager()
    sessionManager.cookie_jar = cookieJar

    imagefileLocation = await asyncio.wait_for(getMedianData(userId=memberIdToUse, selectedSession=selected_session, subsessionId=subsession_id, showRealName=show_real_name, sessionManager=sessionManager), 20)
    file = discord.File(imagefileLocation)
    return file