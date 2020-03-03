# imports
import discord
from discord.ext import commands, tasks
import json
import requests
import time
import datetime
import random
import bot_keys
import os

with open('config.json') as f:
    constants = json.load(f)

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
printTime = 0
randBully = 0
lastMinute = True


# used for debugging
def printd(*args):
    if constants['debug']:
        print(args)


# Limit API use function
def apichecklimit():
    global lastMinute
    global apiChecks
    # takes current time
    currentMinute = time.time()
    # sees if API has been called at all
    if lastMinute is True:
        lastMinute = time.time()
        return
    # checks if it has been longer than a minute since last API call,
    if lastMinute + 61 < currentMinute:
        apiChecks = 0
        lastMinute = currentMinute
    apiChecks = apiChecks + 1
    # if too many calls make program sleep to refresh the limit
    if apiChecks >= constants["apiLimit"]:
        print("Sleeping: 60s")
        time.sleep(60)


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


# runs every 10 seconds, keeps all of the npcTimers, and blood bag timers, and a few other things running
@tasks.loop(seconds=20)
async def timer():
    constants["printTime"] += 20
    constants["randBully"] += 20
    if constants["printTime"] >= 1800:
        # used for debugging
        constants["printTime"] = 0
        print("================================")
        print("Bi-hourly time:")
        print("Start time: " + str(time.time()))
        print("Start time: " + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
    if constants["randBully"] >= 3600:
        constants["randBully"] = 0
        random.seed()
        rand = random.randrange(0, len(constants["bullyList"]))
        await bot.change_presence(activity=discord.Game('Bullying ' + constants["bullyList"][rand] + "!"))


@bot.event
async def on_ready():
    if constants["onReadyRun"] is False:
        constants["onReadyRun"] = True
        random.seed()
        rand = random.randrange(0, len(constants["bullyList"]))
        await bot.change_presence(activity=discord.Game('Bullying ' + constants["bullyList"][rand] + "!"))

        print("================================")
        print("Start time: " + str(time.time()))
        print("Start time: " + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
        print("Tornbot.py is ready.")
        if constants["testingMode"] is True:
            print("Testing mode is Enabled")
        print("================================")
        timer.start()


@bot.command()
async def torn(ctx, playerID):
    if checkCouncilRoles(ctx.author.roles) is False:
        await ctx.send("You do not have permissions to use this command: \"" + ctx.message.content + "\"")
        return
    if constants["testingMode"] is True:
        return
    if playerID.isdigit() is False:
        await ctx.send(playerID + " is not a valid playerID!")
        return
    r = requests.get('https://api.torn.com/user/' + playerID + '?selections=basic&key=%s' % apiKey)
    apichecklimit()
    info = json.loads(r.text)
    if '{"error": {"code": 6, "error": "Incorrect ID"}}' == json.dumps(info):
        await ctx.send("Error: Incorrect ID")
        return
    await ctx.send(
        info['name'] + " is a level " + str(info['level']) + " " + info['gender'] + ". Currently, they are " +
        info['status']['description'] + '.')
    # all faction onliners last 5 mins


@torn.error
async def torn_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You must include a player ID.\nExample: !torn 2003693')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return


@bot.command()
async def help(ctx):
    if constants["testingMode"] is True:
        return
    embed = discord.Embed(title="Help screen:", description="All available commands:")
    embed.set_thumbnail(url="https://i.imgur.com/JIsJGhb.png")
    embed.add_field(name="!onliners [factionID]ᴿ", value="Prints players active in the last five minutes.",
                    inline=True)
    embed.add_field(name="!inactives [factionID]ᴿ", value="Prints players inactive for over 10 hours.",
                    inline=True)
    embed.add_field(name="!donators [factionID]ᴿ", value="Prints players without donator status, and or a PI.",
                    inline=True)
    embed.add_field(name="!torn [playerID]ᴿ", value="Prints a player's basic information & status.", inline=True)
    embed.add_field(name="!help", value="Prints help screen.", inline=True)
    embed.add_field(name="Restricted:", value="ᴿIs restricted to council/leaders/admins.", inline=True)
    await ctx.send(embed=embed)


@bot.command()
async def verify(ctx, tornid):
    if constants["blockVerify"] is True:
        return
    if tornid.isdigit() is False:
        await ctx.send(tornid + " is not a valid playerID!")
        return
    verifyID = tornid
    tornname = json.loads(
        requests.get(('https://api.torn.com/user/' + verifyID + '?selections=basic&key=%s' % apiKey)).text)[
        "name"]
    data = json.loads(requests.get('https://api.torn.com/user/' + verifyID + '?selections=discord&key=%s' % apiKey
                                   ).text)
    apichecklimit()
    if '{"error": {"code": 6, "error": "Incorrect ID"}}' == json.dumps(data):
        await ctx.send("Error: Incorrect ID")
        return
    discordID = data["discord"]["discordID"]
    if discordID == "":
        await ctx.send(
            tornname + " [" + verifyID + "] is not associated with a discord account. Please verify in Torn's "
                                         "Discord server: https://discordapp.com/invite/TVstvww"
            + "<@" + str(ctx.author.id) + ">")
    elif discordID != str(ctx.author.id):
        await ctx.channel.send(
            tornname + " [" + verifyID + "] is associated with another discord account. Please verify with your "
                                         "Discord account in Torn's Discord server: https://discordapp.com/invite/"
                                         "TVstvww " + "<@" +
            str(ctx.author.id) + ">")
    elif discordID == str(ctx.author.id):
        await ctx.send("Welcome " + tornname + " [" + verifyID + "]!")
        await ctx.author.edit(nick=tornname + " [" + verifyID + "]")


@verify.error
async def verify_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You must include a player ID\nExample: !verify 2003693")


@bot.command()
async def getchannelinfo(ctx):
    # used for assigning channels that the bot posts in
    if checkCouncilRoles(ctx.author.roles) is False:
        await ctx.author.send("You do not have permissions to use this command: \"" + ctx.message.content + "\"")
    print(ctx.message.channel.id)
    print(ctx.message.author.id)


def userIsAdmin(user):
    if user.id in constants["adminUsers"]:
        return True
    else:
        return False


@bot.command()
async def load(ctx, extention):
    if userIsAdmin(ctx.author) is False:
        await ctx.atuhor.send("You need to be an administrator of the bot to use this command!")
    if extention not in constants["cogNames"]:
        await ctx.send("Cog " + extention + " not found!")
        return
    bot.load_extension(f'cogs.{extention}')
    await ctx.send("Loaded " + extention)


@bot.command()
async def unload(ctx, extention):
    if userIsAdmin(ctx.author) is False:
        await ctx.atuhor.send("You need to be an administrator of the bot to use this command!")
    if extention not in constants["cogNames"]:
        await ctx.send("Cog " + extention + " not found!")
        return
    bot.unload_extension(f'cogs.{extention}')
    await ctx.send("Unloaded " + extention)


@bot.command()
async def reloadcogs(ctx):
    if userIsAdmin(ctx.author) is False:
        await ctx.atuhor.send("You need to be an administrator of the bot to use this command!")
    for extention in constants["cogNames"]:
        bot.reload_extension(f'cogs.{extention}')
    await ctx.send("Cogs reloaded!")


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(botID)
