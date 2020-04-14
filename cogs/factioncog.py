import random
from discord.ext import commands
import json
from functions import checkFactionNames, checkCouncilRoles, fetch
from bot_keys import apiKey
import aiohttp

with open('config.json') as f:
    constants = json.load(f)
onReadyRun = True

class Faction(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

    @commands.Cog.listener()
    async def on_ready(self):
        global onReadyRun
        if not onReadyRun:
            return
        onReadyRun = False
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
            splitStrings = lastAction.split()
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
    async def WWCD(self, ctx, *args):
        if not args:
            toPick = 1
        else:
            if not args[0].isdigit():
                await ctx.send("The number of picked members must be numbers only.")
                return
            else:
                toPick = int(args[0])
                if toPick > 25:
                    await ctx.send(f"{toPick} is too many members to choose, the maximum is 25.")
                    return
                elif toPick < 1:
                    await ctx.send("You must choose one or more members.")
                    return
        await ctx.send("Drawing...")
        memberList = []
        for factionID in constants["lottoFactions"]:
            async with aiohttp.ClientSession() as session:
                r = await fetch(session, f'https://api.torn.com/faction/{factionID}?selections=basic&key={apiKey}')
            factionInfo = json.loads(r)
            for playerID in factionInfo["members"]:
                memberList.append([factionInfo["members"][playerID]["name"], playerID])
        x = 0
        pickedMembers = []
        while x < toPick:
            rand = random.randrange(0, len(memberList))
            picked = memberList[rand]
            pickedMembers.append(f"{picked[0]} [{picked[1]}]")
            x += 1
        res = ", ".join(pickedMembers)
        await ctx.send(f"Winner winner chicken dinner! {res} wins a prize from {ctx.author}!")

    @WWCD.error
    async def wwcd_error(self, ctx, error):
        return


def setup(bot):
    bot.add_cog(Faction(bot))
