from discord.ext import commands
import json
import time
import asyncio
from Tornbot import checkFactionNames, apiKey, checkCouncilRoles, fetch
import aiohttp

with open('config.json') as f:
    constants = json.load(f)


lastMinute = ""
apiChecks = 0


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
        factionPass = checkFactionNames(factionid)
        if factionPass:
            factionid = str(factionPass)
        if factionid.isdigit() is False:
            await ctx.send(factionid + " is not a valid factionID!")
            return
        if factionid == "":
            await ctx.send("Error: Faction ID missing. Correct usage: !onliners [factionID]")
            return
        async with aiohttp.ClientSession() as session:
            r = await fetch(session, 'https://api.torn.com/faction/' + factionid + '?selections=basic&key=%s' % apiKey)
        parsedJSON = json.loads(r)
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
        factionPass = checkFactionNames(factionid)
        if factionPass:
            factionid = str(factionPass)
        if factionid.isdigit() is False:
            await ctx.send(factionid + " is not a valid factionID!")
            return
        if factionid == "":
            await ctx.send("Error: Faction ID missing. Correct usage: !inactives [factionID]")
            return
        async with aiohttp.ClientSession() as session:
            r = await fetch(session, 'https://api.torn.com/faction/' + factionid + '?selections=basic&key=%s' % apiKey)
        parsedJSON = json.loads(r)
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
        factionPass = checkFactionNames(factionid)
        if factionPass:
            factionid = str(factionPass)
        if factionid.isdigit() is False:
            await ctx.send(factionid + " is not a valid factionID!")
            return
        if factionid == "":
            await ctx.send("Error: Faction ID missing. Correct usage: !donators [factionID]")
            return
        async with aiohttp.ClientSession() as session:
            r = await fetch(session, 'https://api.torn.com/faction/' + factionid + '?selections=basic&key=%s' % apiKey)
        parsedJSON = json.loads(r)
        await apichecklimit()
        # checks if faction exists
        if parsedJSON['best_chain'] == 0:
            await ctx.send('Error: Invalid Faction ID')
            return
        await ctx.send('Please wait, generating list.')
        members = parsedJSON["members"]
        donatorList = []
        for tornID in members:
            donator = False
            is_property = False
            await apichecklimit()
            async with aiohttp.ClientSession() as session:
                r = await fetch(session, 'https://api.torn.com/user/' + tornID + '?selections=profile&key=%s' % apiKey)
            data = json.loads(r)
            playerName = data["name"]
            propString = ""
            donateString = ""
            if data["donator"] == 0:
                donator = True
                donateString = " Donator - False"
            if data["property"] != "Private Island":
                is_property = True
                propString = (" Property - " + data["property"])
            if donator is True or is_property is True:
                donatorList.append(playerName + ": " + donateString + propString)
        sendString = ""
        for string in donatorList:
            sendString = sendString + " " + string + " " + "\n"
        if sendString == "":
            sendString = "Everyone meets requirements!\n"
        await ctx.send("Players without Donator Status or PI: \n ```"+sendString + "```")

    @donators.error
    async def donator_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('You must include a faction ID.\nExample: !donators 11747')


def setup(bot):
    bot.add_cog(Faction(bot))
