import discord
from discord.ext import commands
import json
import requests
import time
from Tornbot import checkFactionNames, apiKey, checkCouncilRoles

with open('config.json') as f:
    constants = json.load(f)


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


class Faction(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

    @commands.Cog.listener()
    async def on_ready(self):
        print("Faction Cog ready!")

    @commands.command()
    async def onliners(self, ctx, factionid):
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
    async def onliners_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('You must include a faction ID.\nExample: !onliners 11747')

    @commands.command()
    async def inactives(self, ctx, factionid):
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
    async def inactive_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('You must include a faction ID.\nExample: !inactives 11747')

    @commands.command()
    # todo donators formatting could use some work
    async def donators(self, ctx, factionid):
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
                donatorList.append(playerName + ": " + donateString + propString)
        sendString = "Players without Donator Status or PI: \n ```"
        for string in donatorList:
            sendString = (sendString + " " + string + " " + "\n")
        await ctx.send(sendString + "```")

    @donators.error
    async def donator_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('You must include a faction ID.\nExample: !donators 11747')


def setup(bot):
    bot.add_cog(Faction(bot))
