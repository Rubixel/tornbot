import json
import aiohttp
from discord.ext import commands

from bot_keys import apiKey

bot = commands.Bot(command_prefix="!")

with open('config.json') as f:
    constants = json.load(f)


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def jfetch(session, url):
    async with session.get(url) as response:
        return await response.json()


async def getIDfromDiscord(discordID):
    async with aiohttp.ClientSession() as session:
        r = await fetch(session, "https://api.torn.com/user/" + str(discordID) + "?selections=discord&key=" + apiKey)
        info = json.loads(r)
    return str(info["discord"]["userID"])


# used for permission checking
def checkCouncilRoles(roleList):
    for authorRole in roleList:
        if authorRole.name.lower() in constants["councilPlus"]:
            return True
    return False


def checkFactionNames(s):
    factions = constants["factionNames"]
    for faction in factions:
        if faction.lower() == s.lower():
            return constants["factionNames"][s]
    return False


def userIsAdmin(user):
    if user.id in constants["adminUsers"]:
        return True
    else:
        return False
