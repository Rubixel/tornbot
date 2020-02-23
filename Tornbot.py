# imports
import discord
import json
import requests
import time
import datetime

# botinfo
client = discord.Client()
# apikey
apiKey = 'SmKfloSmgSDgHZ6e'

# Stuff to prevent API key being used >100 times.

startTime = datetime.datetime.now()
apiLimit = 85
apiChecks = 0
lastMinute = True


# Limit API use function
def apichecklimit():
    global apiLimit
    global apiChecks
    global lastMinute
    now = datetime.datetime.now()
    # takes current time
    currentMinute = [int(now.year), int(now.month), int(now.day), int(now.hour), int(now.minute), int(now.second)]
    # sees if API has been called at all
    if lastMinute == True:
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


@client.event
# onbotload
async def on_ready():
    print("Program is ready.")


@client.event
# whenever a message is sent
async def on_message(message):
    # ignore own messages
    if message.author == client.user:
        return
    # checks a player for info
    if message.content[0:5] == "!torn":
        idtocheck = message.content[6:len(message.content)]
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
        r = requests.get('https://api.torn.com/faction/' + factionid + '?selections=basic&key=%s' % (apiKey))
        apichecklimit()
        parsedJSON = json.loads(r.text)
        # checks if faction exists
        if parsedJSON['best_chain'] == 0:
            await message.channel.send('Error: Invalid Faction ID')
            return
        members = parsedJSON["members"]
        onliners = []
        await message.channel.send('Please wait, generating list.')
        for tornid in members:
            # checks every members and adds to table
            rID = requests.get('https://api.torn.com/user/' + tornid + '?selections=profile&key=%s' % (apiKey))
            apichecklimit()
            idrequest = json.loads(rID.text)
            if json.dumps(idrequest)[0:8] == '{"error"':
                await message.channel.send(json.dumps(idrequest))
                return
            lastaction = idrequest['last_action']['relative']
            playername = idrequest['name']
            splitstrings = (lastaction.split())
            if splitstrings[1] == "minutes" and int(splitstrings[0]) < 6:
                onliners.append(playername + " [" + tornid + '] ' + lastaction)
        sendstring = "Players online in the past 5 minutes: \n ```"
        for state in onliners:
            sendstring = (sendstring + " " + state + " " + "\n")
        await message.channel.send(sendstring + '```')
        # prints faction inactives
    elif message.content[0:10] == '!inactives':
        factionid = ""
        if message.content[10:len(message.content)]:
            factionid = message.content[10:len(message.content)]
        if factionid == "":
            await message.channel.send("Error: Faction ID missing. Correct usage: !inactives [faction_id]")
            return
        r = requests.get('https://api.torn.com/faction/' + factionid + '?selections=basic&key=%s' % (apiKey))
        apichecklimit()
        parsedJSON = json.loads(r.text)
        # checks if faction exists
        if parsedJSON['best_chain'] == 0:
            await message.channel.send('Error: Invalid Faction ID')
            return
        inactives = []
        members = parsedJSON["members"]
        await message.channel.send('Please wait, generating list.')
        for tornid in members:
            getData = requests.get('https://api.torn.com/user/' + tornid + '?selections=profile&key=%s' % (apiKey))
            apichecklimit()
            data = json.loads(getData.text)
            actiondata = data['last_action']['relative']
            playername = data['name']
            splitstrings = (actiondata.split())
            if splitstrings[1] == "hours" and int(splitstrings[0]) > 10:
                inactives.append(playername + " [" + tornid + '] ' + actiondata)
            elif splitstrings[1] == "day" or splitstrings[1] == "days":
                inactives.append(playername + " [" + tornid + '] ' + actiondata)
        sendstring = "Players Inactive for 4 hours or more: \n ```"
        for state in inactives:
            sendstring = (sendstring + " " + state + " " + "\n")
        await message.channel.send(sendstring + "```")
    elif message.content[0:9] == "!donators":
        factionid = ""
        if message.content[9:len(message.content)]:
            factionid = message.content[9:len(message.content)]
        if factionid == "":
            await message.channel.send("Error: Faction ID missing. Correct usage: !donators [faction_id]")
            return
        print(factionid)
        r = requests.get('https://api.torn.com/faction/' + factionid + '?selections=basic&key=%s' % (apiKey))
        apichecklimit()
        parsedJSON = json.loads(r.text)
        # checks if faction exists
        if parsedJSON['best_chain'] == 0:
            await message.channel.send('Error: Invalid Faction ID')
            return
        await message.channel.send('Please wait, generating list.')
        members = parsedJSON["members"]
        donators = []
        for tornid in members:
            donator = False
            property = False
            getData = requests.get('https://api.torn.com/user/' + tornid + '?selections=profile&key=%s' % (apiKey))
            apichecklimit()
            data = json.loads(getData.text)
            playerName = data["name"]
            propstring = ""
            donatestring = ""
            if data["donator"] == 0:
                donator = True
                donatestring = (" Donator - False")
            if data["property"] != "Private Island":
                property = True
                propstring = (" Property - " + data["property"])
            if donator == True or property == True:
                donators.append(playerName + ": " + donatestring + " " + propstring)
        sendstring = "Players without Donator Status or PI: \n ```"
        for string in donators:
            sendstring = (sendstring + " " + string + " " + "\n")
        await message.channel.send(sendstring + "```")
    elif message.content == "!help":
        await message.channel.send(
            "```css\nHelp screen:\n\nFaction:\n\t!onliners [faction_ID] -> Prints players active in the last five minutes.\n\t!inactives [faction_ID] -> Prints players inactive for over 10 hours.\n\t!donator [faction_ID]  -> Prints players without donator status, and or a PI.\n\nPlayer:\n\t!torn [player_ID] -> Prints a player's basic information & status.\n\nMisc:\n\t!help -> Prints help screen.```")
    elif message.content[0:7] == "!verify":
        verifyID = message.content[8:len(message.content)]
        getData = requests.get('https://api.torn.com/user/' + verifyID + '?selections=discord&key=%s' % (apiKey))
        tornname = json.loads(
            requests.get(('https://api.torn.com/user/' + verifyID + '?selections=basic&key=%s' % (apiKey))).text)[
            "name"]
        data = json.loads(getData.text)
        apichecklimit()
        if '{"error": {"code": 6, "error": "Incorrect ID"}}' == json.dumps(data):
            await message.channel.send("Error(Code6): Incorrect ID")
            return
        discordID = data["discord"]["discordID"]
        if discordID == "":
            await message.channel.send(
                tornname + " [" + verifyID + "] is not associated with a discord account. Please verify in Torn's Discord server: https://discordapp.com/invite/TVstvww" + "<@" + str(
                    message.author.id) + ">")
        elif discordID != str(message.author.id):
            await message.channel.send(
                tornname + " [" + verifyID + "] is associated with another discod account. Please verify with your Discord account in Torn's Discord server: https://discordapp.com/invite/TVstvww " + "<@" + str(
                    message.author.id) + ">")
        elif discordID == str(message.author.id):
            await message.channel.send("Welcome "+ tornname + " [" + verifyID + "]!")
            await message.author.edit(nick=tornname + " [" + verifyID + "]")


client.run('NTc4Mzk0MzIwNTMzNzE3MDIy.XNy-TA.qNJMsPDOraaATcoBYb-ZxivYn94')
