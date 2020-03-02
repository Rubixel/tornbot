# imports
import discord
from discord.ext import commands, tasks
import json
import requests
import time
import datetime
import asyncio
import random
import bot_keys
import os
from itertools import cycle

with open('config.json') as f:
    constants = json.load(f)
# todo bring back some "constants" that need to change in the code

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
npcList = ["Duke", "Leslie"]
npcIndex = {}
npcTimes = {}
npcReady = {}
inverseNpcList = {}
npcIDs = ["4", "15"]
lcount = 0
for npc in npcList:
    npcIndex[npc] = lcount
    inverseNpcList[lcount] = npc
    npcTimes[npc] = 0
    npcReady[npc] = True
    lcount += 1


# used for debugging
def printd(*args):
    if constants['debug']:
        print(args)


# Limit API use function
def apichecklimit():
    # takes current time
    currentMinute = time.time()
    # sees if API has been called at all
    if constants["lastMinute"] is True:
        constants["lastMinute"] = time.time()
        return
    # checks if it has been longer than a minute since last API call,
    if constants["lastMinute"] + 61 < currentMinute:
        constants["apiChecks"] = 0
        constants["lastMinute"] = currentMinute
    constants["apiChecks"] = constants["apiChecks"] + 1
    # if too many calls make program sleep to refresh the limit
    if constants["apiChecks"] >= constants["apiLimit"]:
        print("Sleeping: 60s")
        time.sleep(60)


async def checkNPC():
    npcChannel = bot.get_channel(586185860505010176)
    r = requests.get("https://yata.alwaysdata.net/loot/timings/")
    npcRequest = json.loads(r.text)
    for i in npcRequest:
        npcInfo = npcRequest[i]
        npcName = npcInfo["name"]
        npcTimes[npcName] = npcInfo["timings"]["4"]["due"]
    for inverseNpc in inverseNpcList:
        npcName = npcList[int(inverseNpc)]
        fourTime = npcTimes[npcName]
        if fourTime < 0:
            npcReady[npcName] = True
        if 200 < fourTime < 400:
            if npcReady[npcName] is True:
                readyMinutes = str(fourTime // 60)
                readySeconds = str(fourTime % 60)
                npcSendName = npcName + " [" + npcIDs[npcIndex[npcName]] + "]"
                npcSendTime = readyMinutes + " minutes and " + readySeconds + " seconds."
                npcSendLink = "https://www.torn.com/loader.php?sid=attack&user2ID=" + npcIDs[npcIndex[npcName]]
                embed = discord.Embed(title=npcSendName, color=0xae0000)
                embed.set_thumbnail(url=constants["npcImageLinks"][inverseNpc])
                embed.add_field(name="Ready to be attacked in: ", value=npcSendTime, inline=False)
                await npcChannel.send(embed=embed)
                await npcChannel.send(npcSendLink + " <@&612556617153511435>")
                npcReady[npcName] = False


# used for permission checking
def checkCouncilRoles(roleList):
    for authorRole in roleList:
        for councilRole in constants["councilPlus"]:
            if authorRole.name.lower() == councilRole:
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
    constants["npcTime"] += 20
    constants["printTime"] += 20
    constants["randBully"] += 20
    if constants["npcTime"] >= 100:
        constants["npcTime"] = 0
        await checkNPC()
    if constants["printTime"] >= 1800:
        # used for debugging
        constants["printTime"] = 0
        print("================================")
        print("Bi-hourly time:")
        print("Start time: " + str(time.time()))
        print("Start time: " + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
    if constants["randBully"] >= 40:
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
        await checkNPC()


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


@bot.command()
async def onliners(ctx, factionid):
    if checkCouncilRoles(ctx.author.roles) is False:
        await ctx.author.send("You do not have permissions to use this command: \"" + ctx.message.content + "\"")
        return
    if constants["testingMode"] is True:
        return
    factionPass = checkFactionNames(factionid)
    if factionPass:
        factionid = str(factionPass)
    if factionid.isdigit() is False:
        await ctx.send(factionid + " is not a valid factionID!")
        return
    if factionid == "":
        await ctx.send("Error: Faction ID missing. Correct usage: !onliners [factionID]")
        return
    r = requests.get('https://api.torn.com/faction/' + factionid + '?selections=basic&key=%s' % apiKey)
    apichecklimit()
    parsedJSON = json.loads(r.text)
    # checks if faction exists
    if parsedJSON['best_chain'] == 0:
        await ctx.send('Error: Invalid Faction ID')
        return
    members = parsedJSON["members"]
    onlinerList = []
    await ctx.send('Please wait, generating list.')
    for tornID in members:
        playerInfo = members[tornID]
        lastAction = playerInfo["last_action"]["relative"]
        playerName = playerInfo['name']
        splitStrings = (lastAction.split())
        if splitStrings[1] == "minutes" and int(splitStrings[0]) < 6:
            onlinerList.append(playerName + " [" + tornID + '] ' + lastAction)
    sendString = "Players online in the past 5 minutes: \n ```"
    for state in onlinerList:
        sendString = (sendString + " " + state + " " + "\n")
    await ctx.send(sendString + '```')


@onliners.error
async def onliners_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You must include a faction ID.\nExample: !onliners 11747')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return


# prints faction inactives
@bot.command()
async def inactives(ctx, factionid):
    if checkCouncilRoles(ctx.author.roles) is False:
        await ctx.author.send("You do not have permissions to use this command: \"" + ctx.message.content + "\"")
        return
    if constants["testingMode"] is True:
        return
    factionPass = checkFactionNames(factionid)
    if factionPass:
        factionid = str(factionPass)
    if factionid.isdigit() is False:
        await ctx.send(factionid + " is not a valid factionID!")
        return
    if factionid == "":
        await ctx.send("Error: Faction ID missing. Correct usage: !inactives [factionID]")
        return
    r = requests.get('https://api.torn.com/faction/' + factionid + '?selections=basic&key=%s' % apiKey)
    apichecklimit()
    parsedJSON = json.loads(r.text)
    # checks if faction exists
    if parsedJSON['best_chain'] == 0:
        await ctx.send('Error: Invalid Faction ID')
        return
    inactivePlayers = []
    members = parsedJSON["members"]
    await ctx.send('Please wait, generating list.')
    for tornID in members:
        playerInfo = members[tornID]
        lastAction = playerInfo["last_action"]["relative"]
        playerName = playerInfo['name']
        splitStrings = (lastAction.split())
        if splitStrings[1] == "hours" and int(splitStrings[0]) > 10:
            inactivePlayers.append(playerName + " [" + tornID + '] ' + lastAction)
        elif splitStrings[1] == "day" or splitStrings[1] == "days":
            inactivePlayers.append(playerName + " [" + tornID + '] ' + lastAction)
    sendString = "Players Inactive for 10 hours or more: \n ```"
    for state in inactivePlayers:
        sendString = (sendString + " " + state + " " + "\n")
    await ctx.send(sendString + "```")


@inactives.error
async def inactive_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You must include a faction ID.\nExample: !inactives 11747')


@bot.command()
# todo donators formatting could use some work
async def donators(ctx, factionid):
    if checkCouncilRoles(ctx.author.roles) is False:
        await ctx.author.send("You do not have permissions to use this command: \"" + ctx.message.content + "\"")
        return
    if constants["testingMode"] is True:
        return
    factionPass = checkFactionNames(factionid)
    if factionPass:
        factionid = str(factionPass)
    if factionid.isdigit() is False:
        await ctx.send(factionid + " is not a valid factionID!")
        return
    if factionid == "":
        await ctx.send("Error: Faction ID missing. Correct usage: !donators [factionID]")
        return
    r = requests.get('https://api.torn.com/faction/' + factionid + '?selections=basic&key=%s' % apiKey)
    apichecklimit()
    parsedJSON = json.loads(r.text)
    # checks if faction exists
    if parsedJSON['best_chain'] == 0:
        await ctx.send('Error: Invalid Faction ID')
        return
    await ctx.send('Please wait, generating list.')
    members = parsedJSON["members"]
    donatorList = []
    for tornID in members:
        donator = False
        property = False
        apichecklimit()
        data = json.loads(requests.get('https://api.torn.com/user/' + tornID + '?selections=profile&key=%s' %
                                       apiKey).text)
        playerName = data["name"]
        propString = ""
        donateString = ""
        if data["donator"] == 0:
            donator = True
            donateString = " Donator - False"
        if data["property"] != "Private Island":
            property = True
            propString = (" Property - " + data["property"])
        if donator is True or property is True:
            donatorList.append(playerName + ": " + donateString + " " + propString)
    sendString = "Players without Donator Status or PI: \n ```"
    for string in donatorList:
        sendString = (sendString + " " + string + " " + "\n")
    await ctx.send(sendString + "```")


@donators.error
async def donator_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You must include a faction ID.\nExample: !donators 11747')


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


# todo put all of the cogs here or add a !refresh cogs command
# todo check for admin IDs
def userIsAdmin(user):
    userID = user.id
    for id in constants["adminUsers"]:
        if id == userID:
            return True
    return False

@bot.command()
async def load(ctx, extention):
    await ctx.send("Loaded " + extention)
    bot.load_extention(f'cogs.{extention}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
       bot.load_extension(f'cogs.{filename[:-3]}')


bot.run(botID)
