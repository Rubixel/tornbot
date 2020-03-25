# imports
from discord.ext import commands
import json
import time
import datetime
import asyncio
import bot_keys
import os

with open('config.json') as f:
    constants = json.load(f)

# todo always check bot testing mode

# Code written/used by: Hcom [2003603]. Hcom3#7142

# bot info
bot = commands.Bot(command_prefix="!")

# replace with your own Torn API key in. apiKey = "TORN_API_KEY"
apiKey = bot_keys.apiKey
# replace with your own discord bot token in botID = "DISCORD_BOT_TOKEN"
botID = bot_keys.bot_id
startTime = datetime.datetime.now()
bot.remove_command("help")
if constants["botTestingMode"] is True:
    botID = bot_keys.testingBotID

apiChecks = 0
randBully = 0
lastMinute = ""


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def jfetch(session, url):
    async with session.get(url) as response:
        return await response.json()

# used for debugging
def printd(*args):
    if constants['debug']:
        print(args)


# Limit API use function
async def apichecklimit():
    global lastMinute
    global apiChecks
    # takes current time
    currentMinute = time.time()
    # sees if API has been called at all
    if lastMinute == "":
        lastMinute = time.time()
        return
    # checks if it has been longer than a minute since last API call,
    if lastMinute + 61 < currentMinute:
        apiChecks = 0
        lastMinute = currentMinute
    apiChecks = apiChecks + 1
    # if too many calls make program sleep to refresh the limit
    if apiChecks >= constants["apiLimit"]:
        print("Sleeping 60s")
        await asyncio.sleep(60)


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


@bot.command()
async def load(ctx, extension):
    if userIsAdmin(ctx.author) is False:
        await ctx.atuhor.send("You need to be an administrator of the bot to use this command!")
    if extension not in constants["cogNames"]:
        await ctx.send("Cog " + extension + " not found!")
        return
    bot.load_extension(f'cogs.{extension}')
    await ctx.send("Loaded " + extension)


@bot.command()
async def unload(ctx, extension):
    if userIsAdmin(ctx.author) is False:
        await ctx.atuhor.send("You need to be an administrator of the bot to use this command!")
    if extension not in constants["cogNames"]:
        await ctx.send("Cog " + extension + " not found!")
        return
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send("Unloaded " + extension)


@bot.command()
async def reloadcogs(ctx):
    if userIsAdmin(ctx.author) is False:
        await ctx.atuhor.send("You need to be an administrator of the bot to use this command!")
    for extension in constants["cogNames"]:
        bot.reload_extension(f'cogs.{extension}')
    await ctx.send("Cogs reloaded!")


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(botID)
