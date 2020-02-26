# imports
import discord
import json
import requests
import time
import datetime
import asyncio

# bot info
client = discord.Client()
# api key
apiKey = 'SmKfloSmgSDgHZ6e'

# Stuff to prevent API key being used >100 times.

startTime = datetime.datetime.now()
apiLimit = 85
apiChecks = 0
lastMinute = True
bloodBagChannel = False
temp_armory_time_stamp = False
armory_time_stamp = 0
shutdown = False

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
    r = requests.get("https://api.torn.com/faction/?selections=armorynews&key=SmKfloSmgSDgHZ6e")
    armory_logs = json.loads(r.text)["armorynews"]
    bagFound = False
    if bloodBagChannel == False:
        return
    for log_ID in armory_logs:
        log = armory_logs[log_ID]
        log_timestamp = int(log["timestamp"])
        print("saved TS" + str(armory_time_stamp))
        print('log TS' + str(log_timestamp))
        if log_timestamp <= armory_time_stamp:
            if bagFound is True:
                armory_time_stamp = temp_armory_time_stamp
            return
        if log_timestamp > armory_time_stamp:
            if temp_armory_time_stamp < log_timestamp:
                print("temp updated")
                temp_armory_time_stamp = log_timestamp
        if log["news"].find("filled one of the faction's Empty Blood Bag items.") != -1:
            bagFound = True
            string = log["news"]
            playerid = string[string.find("XID=")+4:string.find("\">")]
            playername = string[string.find("\">")+2:string.find("</a>")]
            await bloodBagChannel.send(playername + " ["+playerid+"] filled one of the faction's Empty Blood Bag ""items.")
            print(log_timestamp)
            print(playername + " ["+playerid+"] filled one of the faction's Empty Blood Bag ""items.")
    if bagFound is True:
        armory_time_stamp = temp_armory_time_stamp
    print("End Saved TS" + str(armory_time_stamp))

async def wait_minute():
    print("waiting")
    if shutdown is True:
        print("Blood bag command shutdown")
        await bloodBagChannel.send("Blood Bags shutdown")
        return
    await asyncio.sleep(60)
    await check_bags()
    await wait_minute()

@client.event
# on bot load
async def on_ready():
    print("Program is ready.")
    await client.change_presence(activity=discord.Game('Bullying Everyone!'))

@client.event
# whenever a message is sent
async def on_message(message):
    # ignore own messages
    if message.author == client.user:
        return
    # checks a player for info
    if message.content[0:5] == "!torn":
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
            # checks every members and adds to table
            rID = requests.get('https://api.torn.com/user/' + torn_id + '?selections=profile&key=%s' % apiKey)
            apichecklimit()
            id_request = json.loads(rID.text)
            if json.dumps(id_request)[0:8] == '{"error"':
                await message.channel.send(json.dumps(id_request))
                return
            last_action = id_request['last_action']['relative']
            player_name = id_request['name']
            split_strings = (last_action.split())
            if split_strings[1] == "minutes" and int(split_strings[0]) < 6:
                onliners.append(player_name + " [" + torn_id + '] ' + last_action)
        send_string = "Players online in the past 5 minutes: \n ```"
        for state in onliners:
            send_string = (send_string + " " + state + " " + "\n")
        await message.channel.send(send_string + '```')
        # prints faction inactives
    elif message.content[0:10] == '!inactives':
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
            apichecklimit()
            data = json.loads(requests.get('https://api.torn.com/user/' + torn_id + '?selections='
                                                                                    'profile&key=%s' % apiKey
                                           ).text)
            actiondata = data['last_action']['relative']
            player_name = data['name']
            split_strings = actiondata.split()
            if split_strings[1] == "hours" and int(split_strings[0]) > 10:
                inactives.append(player_name + " [" + torn_id + '] ' + actiondata)
            elif split_strings[1] == "day" or split_strings[1] == "days":
                inactives.append(player_name + " [" + torn_id + '] ' + actiondata)
        send_string = "Players Inactive for 4 hours or more: \n ```"
        for state in inactives:
            send_string = (send_string + " " + state + " " + "\n")
        await message.channel.send(send_string + "```")
    elif message.content[0:9] == "!donators":
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
        await message.channel.send(
            "```css\nHelp screen:\n\nFaction:\n\t!onliners [faction_ID] -> Prints players active in the last five "
            "minutes.\n\t!inactives [faction_ID] -> Prints players inactive for over 10 hours.\n\t!donator "
            "[faction_ID]  -> Prints players without donator status, and or a PI.\n\nPlayer:\n\t!torn [player_ID] -> "
            "Prints a player's basic information & status.\n\nMisc:\n\t!help -> Prints help screen.\n\t!bindbags -> "
            "Posts all bloodbag filling info in this channel.(Do not use twice, or it will break)"
            "```")
    elif message.content[0:7] == "!verify":
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
    elif message.content == "!bindbags":
        global bloodBagChannel
        bloodBagChannel = client.get_channel(message.channel.id)
        await bloodBagChannel.send("Bloodbag filling will now output to: #" + message.channel.name+"!")
        await wait_minute()
        await check_bags()
    elif message.content == "!shutdown":
        global shutdown
        shutdown = True



client.run('NTc4Mzk0MzIwNTMzNzE3MDIy.XNy-TA.qNJMsPDOraaATcoBYb-ZxivYn94')
