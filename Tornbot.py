import discord
import json
import requests

client = discord.Client()
version = "1.0.0"
prefix = '!?'

apiKey = 'SmKfloSmgSDgHZ6e'


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    print('Bot is currently running version ' + version + ' with the prefix: ' + prefix)
    print("Program is ready.")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == "!torn":
        r = requests.get('https://api.torn.com/user/?selections=basic&key=%s' % (apiKey))
        info = json.loads(r.text)
        tornmessage = (info['name'] + " is a " + str(info['level']))
        await message.channel.send(
            info['name'] + " is a level " + str(info['level']) + " " + info['gender'] + ". Currently, they are " +
            info['status']['description'] + '.')

    elif message.content[0:9] == '!onliners':
        factionid = ""
        r = ""
        parsedJSON = ""
        splitstrings = ""
        idrequest = ""
        if message.content[9:len(message.content)]:
            factionid = message.content[9:len(message.content)]
        r = requests.get('https://api.torn.com/faction/' + factionid + '?selections=basic&key=%s' % (apiKey))
        parsedJSON = json.loads(r.text)
        if error_check(str(parsedJSON), True, message.channel):
            print("a")
        if parsedJSON['best_chain'] == 0:
            await message.channel.send('Error: Invalid Faction ID')
            return
        members = parsedJSON["members"]
        onliners = []
        await message.channel.send('Please wait, generating list.')
        for tornid in members:
            rID = requests.get('https://api.torn.com/user/' + tornid + '?selections=profile&key=%s' % (apiKey))
            idrequest = json.loads(rID.text)
            print(json.dumps(idrequest))
            print(type(json.dumps(idrequest)))
            if json.dumps(idrequest)[0:8] == '{"error"':
                print(json.dumps(idrequest))
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
    elif message.content == '!inactives':
        await message.channel.send('Please wait, generating list.')
        inactives = []
        getData = requests.get('https://api.torn.com/faction/?selections=basic&key=%s' % (apiKey))
        dataAsText = getData.text
        data = json.loads(dataAsText)
        members = data["members"]
        print('inactives')
        for tornid in members:
            getData = requests.get('https://api.torn.com/user/' + tornid + '?selections=profile&key=%s' % (apiKey))
            data = json.loads(getData.text)
            actiondata = data['last_action']['relative']
            playername = data['name']
            splitstrings = (actiondata.split())
            if splitstrings[1] == "hours" and int(splitstrings[0]) > 4:
                inactives.append(playername + " [" + tornid + '] ' + actiondata)
            elif splitstrings[1] == "day" or splitstrings[1] == "days":
                inactives.append(playername + " [" + tornid + '] ' + actiondata)
        sendstring = "Players Inactive for 4 hours or more: \n ```"
        for state in inactives:
            sendstring = (sendstring + " " + state + " " + "\n")
        await message.channel.send(sendstring + "```")


def error_check(request, output, channel):
    if request == "{'error': {'code': 5, 'error': 'Too many requests'}}":
        print("ERROR: Too Many Requests")
        return True


client.run('NTc4Mzk0MzIwNTMzNzE3MDIy.XNy-TA.qNJMsPDOraaATcoBYb-ZxivYn94')
