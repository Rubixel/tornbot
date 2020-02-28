# imports
import discord
import json
import requests
import time
import datetime
import asyncio
import random

# bot info
client = discord.Client()
# api key
apiKey = 'SmKfloSmgSDgHZ6e'

# Stuff to prevent API key being used >100 times.


# todo print version number/time etc information for debugging
# todo also create stuff to help debugging in nohup.out


startTime = datetime.datetime.now()
apiLimit = 85
apiChecks = 0
lastMinute = True
armory_time_stamp = 0
shutdown = False
leslie_ready = False
duke_ready = False
# testing mode, for testing only one thing so it doesnt interfere with running bot
testing_mode = True
council_plus = ["ns leaders", "ns council i", "ns council ii", "ns council iii", "ns ii leaders"]
admin_users = [200676892024504320, 547926928313548801, 547986194055692289]
bloodBagChannel = ""
npcChannel = ""
# todo assign timer() variables on the first call instead of having them in global
npcTime = 0
bagTime = 0
printTime = 0
randBully = 0
debug = False
bully_list = ["Hcom", "jukka", "Gratify", "ZeroTwo", "STEVE_HOLT", "Rhino", "LTJELLOMAN", "Bones", "Roxy", "Everyone"]

def printd(*args):
    if debug:
        print(args)


# todo Comment all of the code before making repository public.

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


async def check_bags():
    global armory_time_stamp
    global bloodBagChannel
    temp_armory_time_stamp = 0
    r = requests.get('https://api.torn.com/faction/?selections=armorynews&key=%s' % apiKey)
    armory_logs = json.loads(r.text)["armorynews"]
    bagFound = False
    if bloodBagChannel is False:
        return
    for log_ID in armory_logs:
        log = armory_logs[log_ID]
        log_timestamp = int(log["timestamp"])
        if log_timestamp <= armory_time_stamp:
            if bagFound is True:
                armory_time_stamp = temp_armory_time_stamp
            return
        if log_timestamp > armory_time_stamp:
            if temp_armory_time_stamp < log_timestamp:
                temp_armory_time_stamp = log_timestamp
        if log["news"].find("filled one of the faction's Empty Blood Bag items.") != -1:
            bagFound = True
            string = log["news"]
            playerid = string[string.find("XID=")+4:string.find("\">")]
            playername = string[string.find("\">")+2:string.find("</a>")]
            await bloodBagChannel.send(playername + " ["+playerid+"] filled one of the faction's "
                                                                  "Empty Blood Bag ""items.")
    if bagFound is True:
        armory_time_stamp = temp_armory_time_stamp

# todo add in bit of formatting for leslie & duke message: NPC_NAME will be at level four in etc etc...
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
        ready_minutes = str(four_time // 60)
        ready_seconds = str(four_time % 60)
        await npcChannel.send("Leslie will be ready in: "+ready_minutes+" minutes and "+ready_seconds+" "
                              "seconds! <@&612556617153511435>\n"+"https://www.torn.com/loader2.php?sid=get"
                                                                  "InAttack&user2ID=15")
        
        
async def check_duke():
    global npcChannel
    global duke_ready
    r = requests.get("https://yata.alwaysdata.net/loot/timings/")
    npc_info = json.loads(r.text)
    four_time = npc_info["4"]["timings"]["4"]["due"]
    if four_time < 0:
        duke_ready = False
    if four_time < 200:
        return
    if four_time < 400 and duke_ready is False:
        duke_ready = True
        ready_minutes = str(four_time // 60)
        ready_seconds = str(four_time % 60)
        await npcChannel.send("Duke will be ready in: "+ready_minutes+" minutes and "+ready_seconds+" "
                              "seconds! <@&612556617153511435>\n"+"https://www.torn.com/loader2.php?sid=get"
                                                                  "InAttack&user2ID=4")


def check_council_roles(role_list):
    global council_plus
    for authorRole in role_list:
        for councilRole in council_plus:
            if authorRole.name.lower() == councilRole:
                return True
    return False


async def timer():
    global bagTime
    global npcTime
    global printTime
    global randBully
    global bully_list
    bagTime += 20
    npcTime += 20
    printTime += 20
    randBully += 20
    if bagTime >= 60:
        bagTime = 0
        await check_bags()
    if npcTime >= 100:
        npcTime = 0
        await check_duke()
        await check_leslie()
    if printTime >= 1800:
        printTime = 0
        print("================================")
        print("Bi-hourly time:")
        print("Start time: " + str(time.time()))
        print("Start time: " + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1347517370))))
    if randBully >= 3600:
        random.seed()
        rand = random.randrange(0, len(bully_list))
        await client.change_presence(activity=discord.Game('Bullying ' + bully_list[rand] + "!"))
    await asyncio.sleep(20)
    await timer()


@client.event
# on bot load
async def on_ready():
    printd("on ready")
    global armory_time_stamp
    global bully_list
    random.seed()
    rand = random.randrange(0, len(bully_list))
    await client.change_presence(activity=discord.Game('Bullying ' + bully_list[rand]+"!"))
    global bloodBagChannel
    bloodBagChannel = client.get_channel(645540955688271872)
    r = requests.get('https://api.torn.com/torn/?selections=timestamp&key=%s' % apiKey)
    armory_time_stamp = json.loads(r.text)["timestamp"]
    global npcChannel
    npcChannel = client.get_channel(586185860505010176)
    print("================================")
    print("Start time: "+str(time.time()))
    print("Start time: "+str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1347517370))))
    print("Tornbot.py is ready.")
    print("================================")
    await timer()


@client.event
# whenever a message is sent
async def on_message(message):
    # ignore own messages
    if message.author == client.user:
        return
    # checks a player for info
    if message.content[0:5] == "!torn":
        if check_council_roles(message.author.roles) is False:
            await message.author.send("You do not have permissions to use this command: \"" + message.content + "\"")
            return
        if testing_mode is True:
            return
        idtocheck = message.content[6:len(message.content)]
        if idtocheck == "":
            await message.channel.send("Error: Player ID missing. Correct usage: !torn [player_id]")
            return
        r = requests.get('https://api.torn.com/user/' + idtocheck + '?selections=basic&key=%s' % apiKey)
        apichecklimit()
        info = json.loads(r.text)
        if '{"error": {"code": 6, "error": "Incorrect ID"}}' == json.dumps(info):
            await message.channel.send("Error(Code6): Incorrect ID")
            return
        await message.channel.send(
            info['name'] + " is a level " + str(info['level']) + " " + info['gender'] + ". Currently, they are " +
            info['status']['description'] + '.')
    # all faction onliners last 5 mins
    elif message.content[0:9] == '!onliners':
        if check_council_roles(message.author.roles) is False:
            await message.author.send("You do not have permissions to use this command: \""+message.content+"\"")
            return
        if testing_mode is True:
            return
        factionid = ""
        if message.content[9:len(message.content)]:
            factionid = message.content[9:len(message.content)]
        if factionid == "":
            await message.channel.send("Error: Faction ID missing. Correct usage: !onliners [faction_id]")
            return
        r = requests.get('https://api.torn.com/faction/' + factionid + '?selections=basic&key=%s' % apiKey)
        apichecklimit()
        parsedJSON = json.loads(r.text)
        # checks if faction exists
        if parsedJSON['best_chain'] == 0:
            await message.channel.send('Error: Invalid Faction ID')
            return
        members = parsedJSON["members"]
        onliners = []
        await message.channel.send('Please wait, generating list.')
        for torn_id in members:
            player_info = members[torn_id]
            last_action = player_info["last_action"]["relative"]
            player_name = player_info['name']
            split_strings = (last_action.split())
            if split_strings[1] == "minutes" and int(split_strings[0]) < 6:
                onliners.append(player_name + " [" + torn_id + '] ' + last_action)
        send_string = "Players online in the past 5 minutes: \n ```"
        for state in onliners:
            send_string = (send_string + " " + state + " " + "\n")
        await message.channel.send(send_string + '```')
        # prints faction inactives
    elif message.content[0:10] == '!inactives':
        if check_council_roles(message.author.roles) is False:
            await message.author.send("You do not have permissions to use this command: \""+message.content+"\"")
            return
        if testing_mode is True:
            return
        factionid = ""
        if message.content[10:len(message.content)]:
            factionid = message.content[10:len(message.content)]
        if factionid == "":
            await message.channel.send("Error: Faction ID missing. Correct usage: !inactives [faction_id]")
            return
        r = requests.get('https://api.torn.com/faction/' + factionid + '?selections=basic&key=%s' % apiKey)
        apichecklimit()
        parsedJSON = json.loads(r.text)
        # checks if faction exists
        if parsedJSON['best_chain'] == 0:
            await message.channel.send('Error: Invalid Faction ID')
            return
        inactives = []
        members = parsedJSON["members"]
        await message.channel.send('Please wait, generating list.')
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
        await message.channel.send(send_string + "```")
    elif message.content[0:9] == "!donators":
        if check_council_roles(message.author.roles) is False:
            await message.author.send("You do not have permissions to use this command: \""+message.content+"\"")
            return
        if testing_mode is True:
            return
        factionid = ""
        if message.content[10:len(message.content)]:
            factionid = message.content[10:len(message.content)]
        if factionid == "":
            await message.channel.send("Error: Faction ID missing. Correct usage: !donators [faction_id]")
            return
        r = requests.get('https://api.torn.com/faction/' + factionid + '?selections=basic&key=%s' % apiKey)
        apichecklimit()
        parsedJSON = json.loads(r.text)
        # checks if faction exists
        if parsedJSON['best_chain'] == 0:
            await message.channel.send('Error: Invalid Faction ID')
            return
        await message.channel.send('Please wait, generating list.')
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
        await message.channel.send(send_string + "```")
    elif message.content == "!help":
        # todo update todo to use embed format
        if testing_mode is True:
            return
        await message.channel.send(
            "```css\nHelp screen:\n\nFaction:\n\t!onliners [faction_ID] -> Prints players active in the last five "
            "minutes.ᴿ\n\t!inactives [faction_ID] -> Prints players inactive for over 10 hours.ᴿ\n\t!donators "
            "[faction_ID]  -> Prints players without donator status, and or a PI.ᴿ\n\nPlayer:\n\t!torn [player_ID] -> "
            "Prints a player's basic information & status.ᴿ\n\nMisc:\n\t!help -> Prints help screen.\n\t!bindbags -> "
            "Posts all bloodbag filling info in this channel.ᴿ(Do not use twice, or it will break)\n\t!bindNPC -> "
            "Prints NPC updates int his channel.ᴿ\n\t\tᴿIs restricted to council & leaders."
            "```")
    elif message.content[0:7] == "!verifyBullyBot":
        verifyID = message.content[8:len(message.content)]
        tornname = json.loads(
            requests.get(('https://api.torn.com/user/' + verifyID + '?selections=basic&key=%s' % apiKey)).text)[
            "name"]
        data = json.loads(requests.get('https://api.torn.com/user/' + verifyID + '?selections=discord&key=%s' % apiKey
                                       ).text)
        apichecklimit()
        if '{"error": {"code": 6, "error": "Incorrect ID"}}' == json.dumps(data):
            await message.channel.send("Error(Code6): Incorrect ID")
            return
        discordID = data["discord"]["discordID"]
        if discordID == "":
            await message.channel.send(
                tornname + " [" + verifyID + "] is not associated with a discord account. Please verify in Torn's "
                                            "Discord server: https://discordapp.com/invite/TVstvww" + "<@" + str(
                                           message.author.id) + ">")
        elif discordID != str(message.author.id):
            await message.channel.send(
                tornname + " [" + verifyID + "] is associated with another discod account. Please verify with your "
                                             "Discord account in Torn's Discord server: https://discordapp.com/invite/"
                                             "TVstvww " + "<@" + str(
                                              message.author.id) + ">")
        elif discordID == str(message.author.id):
            await message.channel.send("Welcome " + tornname + " [" + verifyID + "]!")
            await message.author.edit(nick=tornname + " [" + verifyID + "]")
    elif message.content == "!shutdown":
        if check_council_roles(message.author.roles) is False:
            await message.author.send("You do not have permissions to use this command: \""+message.content+"\"")
            return
        if testing_mode is True:
            return
        global shutdown
        shutdown = True
    elif message.content == "!getchannelinfo":
        if check_council_roles(message.author.roles) is False:
            await message.author.send("You do not have permissions to use this command: \"" + message.content + "\"")
        print(message.channel.id)
        print(message.author.id)


client.run('NTc4Mzk0MzIwNTMzNzE3MDIy.XNy-TA.qNJMsPDOraaATcoBYb-ZxivYn94')


