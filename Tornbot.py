# imports
import discord
from discord.ext import commands
import json
import requests
import time
import datetime
import asyncio
import random
import bot_keys
# Code written/used by: Hcom [2003603]. Hcom3#7142

# bot info
bot = commands.Bot(command_prefix="!")

# replace with your own Torn API key in. apiKey = "TORN_API_KEY"
apiKey = bot_keys.apiKey
# replace with your own discord bot token in bot_id = "DISCORD_BOT_TOKEN"
bot_id = bot_keys.bot_id

# constants
startTime = datetime.datetime.now()
apiLimit = 80
apiChecks = 0
lastMinute = True
armory_time_stamp = 0
shutdown = False
leslie_ready = False
duke_ready = False
# testing mode, for testing only one thing so it doesnt interfere with running bot
testing_mode = False
bot_testing_mode = False
if bot_testing_mode is True:
    bot_id = bot_keys.testing_bot_id
bot.remove_command("help")
# roles allowed to use commands
council_plus = ["ns leaders", "ns council i", "ns council ii", "ns council iii", "ns ii leaders"]
# discord IDs allowed to bypass permissions, WIP.
admin_users = [200676892024504320, 547926928313548801, 547986194055692289]
bloodBagChannel = ""
npcChannel = ""
debug = False
bagTime = 0
npcTime = 0
printTime = 0
randBully = 0
# !verify would interfere with NS discord verify, so its disabled through this
block_verify = True
on_ready_run = False
# cycles between these for status
bully_list = ["Hcom", "jukka", "Gratify", "ZeroTwo", "Johnny_G", "FidelCashFlow",
              "STEVE_HOLT", "Rhino", "LTJELLOMAN", "Bones", "Roxy", "Everyone", "ttyper", "Vicarious", "Stretch",
              "Karen", "Itself"]


# used for debugging
def printd(*args):
    if debug:
        print(args)


# Limit API use function
def apichecklimit():
    global apiLimit
    global apiChecks
    global lastMinute
    now = datetime.datetime.now()
    # takes current time
    currentMinute = [int(now.year), int(now.month), int(now.day), int(now.hour), int(now.minute), int(now.second)]
    # sees if API has been called at all
    if lastMinute is True:
        now = datetime.datetime.now()
        lastMinute = [int(now.year), int(now.month), int(now.day), int(now.hour), int(now.minute), int(now.second)]
        return
    # checks if it has been longer than a minute since last API call, if it has reset apiChecks since limit is back to 0
    if lastMinute[0] < currentMinute[0] or lastMinute[1] < currentMinute[1] or lastMinute[2] < currentMinute[2] or \
            lastMinute[3] < currentMinute[3] or lastMinute[4] + 2 < currentMinute[4] or (
            lastMinute[4] + 1 <= currentMinute[4] and lastMinute[5] < currentMinute[5] + 1):
        apiChecks = 0
        lastMinute = currentMinute
    apiChecks = apiChecks + 1
    # if too many calls make program sleep to refresh the limit
    if apiChecks >= apiLimit:
        print("Sleeping: 60s")
        time.sleep(60)


# todo edit NPC functions to prepare for the launch of the new NPCs

# checks leslie, and if they are ready for attack
async def check_leslie():
    global npcChannel
    global leslie_ready
    r = requests.get("https://yata.alwaysdata.net/loot/timings/")
    npc_info = json.loads(r.text)
    four_time = npc_info["15"]["timings"]["4"]["due"]
    if four_time < 0:
        leslie_ready = False
    if four_time < 200:
        return
    if four_time < 400 and leslie_ready is False:
        leslie_ready = True
        # formats seconds left into minutes and seconds
        ready_minutes = str(four_time // 60)
        ready_seconds = str(four_time % 60)
        await npcChannel.send("Leslie will be ready in: "
                              + ready_minutes + " minutes and " + ready_seconds + " seconds! <@&612556617153511435>\n" +
                              "https://www.torn.com/loader2.php?sid=getInAttack&user2ID=15")


# checks duke, and if they are ready for attack
async def check_duke():
    global npcChannel
    global duke_ready
    r = requests.get("https://yata.alwaysdata.net/loot/timings/")
    npc_info = json.loads(r.text)
    four_time = npc_info["4"]["timings"]["4"]["due"]
    # four_time is how many seconds to level four, if its between 200 and 400 seconds it will print a message in the
    # npcChannel
    if four_time < 0:
        duke_ready = False
    if four_time < 200:
        return
    if four_time < 400 and duke_ready is False:
        duke_ready = True
        # formats seconds left into minutes and seconds
        ready_minutes = str(four_time // 60)
        ready_seconds = str(four_time % 60)
        await npcChannel.send("Duke will be ready in: " + ready_minutes +
                              " minutes and " + ready_seconds + " ""seconds! <@&612556617153511435>\n" +
                              "https://www.torn.com/loader2.php?sid=getInAttack&user2ID=4")


# used for permission checking
def check_council_roles(role_list):
    global council_plus
    for authorRole in role_list:
        for councilRole in council_plus:
            if authorRole.name.lower() == councilRole:
                return True
    return False


# runs every 10 seconds, keeps all of the npcTimers, and blood bag timers, and a few other things running
async def timer():
    global npcTime
    global printTime
    global randBully
    npcTime += 20
    printTime += 20
    randBully += 20
    if npcTime >= 100:
        npcTime = 0
        await check_duke()
        await check_leslie()
    if printTime >= 1800:
        # used for debugging
        printTime = 0
        print("================================")
        print("Bi-hourly time:")
        print("Start time: " + str(time.time()))
        print("Start time: " + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1347517370))))
    if randBully >= 3600:
        random.seed()
        rand = random.randrange(0, len(bully_list))
        await bot.change_presence(activity=discord.Game('Bullying ' + bully_list[rand] + "!"))
    await asyncio.sleep(20)
    await timer()


@bot.event
# on bot load
async def on_ready():
    global on_ready_run
    if on_ready_run is False:
        on_ready_run = True
        printd("on ready")
        global bully_list
        random.seed()
        rand = random.randrange(0, len(bully_list))
        await bot.change_presence(activity=discord.Game('Bullying ' + bully_list[rand] + "!"))
        global bloodBagChannel
        bloodBagChannel = bot.get_channel(645540955688271872)
        global npcChannel
        npcChannel = bot.get_channel(586185860505010176)
        print("================================")
        print("Start time: " + str(time.time()))
        print("Start time: " + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
        print("Tornbot.py is ready.")
        if testing_mode is True:
            print("Testing mode is Enabled")
        print("================================")
        await timer()


@bot.command()
async def torn(ctx, player_id):
    if check_council_roles(ctx.author.roles) is False:
        await ctx.send("You do not have permissions to use this command: \"" + ctx.message.content + "\"")
        return
    if testing_mode is True:
        return
    if player_id.isdigit() is False:
        await ctx.send(player_id + " is not a valid playerID!")
        return
    idtocheck = player_id
    if idtocheck == "":
        await ctx.send("Error: Player ID missing. Correct usage: !torn [player_id]")
        return
    r = requests.get('https://api.torn.com/user/' + idtocheck + '?selections=basic&key=%s' % apiKey)
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
    if check_council_roles(ctx.author.roles) is False:
        await ctx.author.send("You do not have permissions to use this command: \"" + ctx.message.content + "\"")
        return
    if testing_mode is True:
        return
    if factionid.isdigit() is False:
        await ctx.send(factionid + " is not a valid factionID!")
        return
    if factionid == "":
        await ctx.send("Error: Faction ID missing. Correct usage: !onliners [faction_id]")
        return
    r = requests.get('https://api.torn.com/faction/' + factionid + '?selections=basic&key=%s' % apiKey)
    apichecklimit()
    parsedJSON = json.loads(r.text)
    # checks if faction exists
    if parsedJSON['best_chain'] == 0:
        await ctx.send('Error: Invalid Faction ID')
        return
    members = parsedJSON["members"]
    onliner_list = []
    await ctx.send('Please wait, generating list.')
    for torn_id in members:
        player_info = members[torn_id]
        last_action = player_info["last_action"]["relative"]
        player_name = player_info['name']
        split_strings = (last_action.split())
        if split_strings[1] == "minutes" and int(split_strings[0]) < 6:
            onliner_list.append(player_name + " [" + torn_id + '] ' + last_action)
    send_string = "Players online in the past 5 minutes: \n ```"
    for state in onliner_list:
        send_string = (send_string + " " + state + " " + "\n")
    await ctx.send(send_string + '```')


@bot.event
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
    if check_council_roles(ctx.author.roles) is False:
        await ctx.author.send("You do not have permissions to use this command: \"" + ctx.message.content + "\"")
        return
    if testing_mode is True:
        return
    if factionid.isdigit() is False:
        await ctx.send(factionid + " is not a valid factionID!")
        return
    if factionid == "":
        await ctx.send("Error: Faction ID missing. Correct usage: !inactives [faction_id]")
        return
    r = requests.get('https://api.torn.com/faction/' + factionid + '?selections=basic&key=%s' % apiKey)
    apichecklimit()
    parsedJSON = json.loads(r.text)
    # checks if faction exists
    if parsedJSON['best_chain'] == 0:
        await ctx.send('Error: Invalid Faction ID')
        return
    inactives = []
    members = parsedJSON["members"]
    await ctx.send('Please wait, generating list.')
    for torn_id in members:
        player_info = members[torn_id]
        last_action = player_info["last_action"]["relative"]
        player_name = player_info['name']
        split_strings = (last_action.split())
        if split_strings[1] == "hours" and int(split_strings[0]) > 10:
            inactives.append(player_name + " [" + torn_id + '] ' + last_action)
        elif split_strings[1] == "day" or split_strings[1] == "days":
            inactives.append(player_name + " [" + torn_id + '] ' + last_action)
    send_string = "Players Inactive for 4 hours or more: \n ```"
    for state in inactives:
        send_string = (send_string + " " + state + " " + "\n")
    await ctx.send(send_string + "```")


@inactives.error
async def inactives_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You must include a faction ID.\nExample: !inactives 11747')


@bot.command()
async def donators(ctx, factionid):
    if check_council_roles(ctx.author.roles) is False:
        await ctx.author.send("You do not have permissions to use this command: \"" + ctx.message.content + "\"")
        return
    if testing_mode is True:
        return
    if factionid.isdigit() is False:
        await ctx.send(factionid + " is not a valid factionID!")
        return
    if factionid == "":
        await ctx.send("Error: Faction ID missing. Correct usage: !donators [faction_id]")
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
    donators = []
    for torn_id in members:
        donator = False
        property = False
        apichecklimit()
        data = json.loads(requests.get('https://api.torn.com/user/' + torn_id + '?selections=profile&key=%s' %
                                       apiKey).text)
        playerName = data["name"]
        prop_string = ""
        donate_string = ""
        if data["donator"] == 0:
            donator = True
            donate_string = " Donator - False"
        if data["property"] != "Private Island":
            property = True
            prop_string = (" Property - " + data["property"])
        if donator is True or property is True:
            donators.append(playerName + ": " + donate_string + " " + prop_string)
    send_string = "Players without Donator Status or PI: \n ```"
    for string in donators:
        send_string = (send_string + " " + string + " " + "\n")
    await ctx.send(send_string + "```")


@donators.error
async def donators_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You must include a faction ID.\nExample: !donators 11747')

@bot.command()
async def help(ctx):
    if testing_mode is True:
        return
    embed = discord.Embed(title="Help screen:", description="All availible commands:")
    embed.set_thumbnail(url="https://i.imgur.com/JIsJGhb.png")
    embed.add_field(name="!onliners [faction_ID]ᴿ", value="Prints players active in the last five minutes.",
                    inline=True)
    embed.add_field(name="!inactives [faction_ID]ᴿ", value="Prints players inactive for over 10 hours.",
                    inline=True)
    embed.add_field(name="!donators [faction_ID]ᴿ", value="Prints players without donator status, and or a PI.",
                    inline=True)
    embed.add_field(name="!torn [player_ID]ᴿ", value="Prints a player's basic information & status.", inline=True)
    embed.add_field(name="!help", value="Prints help screen.", inline=True)
    embed.add_field(name="Restricted:", value="ᴿIs restricted to council/leaders/admins.", inline=True)
    await ctx.send(embed=embed)


@bot.command()
async def verify(ctx, tornid):
    global block_verify
    if block_verify is True:
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
            tornname + " [" + verifyID + "] is associated with another discod account. Please verify with your "
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
    if check_council_roles(ctx.author.roles) is False:
        await ctx.author.send("You do not have permissions to use this command: \"" + ctx.message.content + "\"")
    print(ctx.message.channel.id)
    print(ctx.message.author.id)


bot.run(bot_id)
