import asyncio
import os
import random
import time

import discord
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
        onlinerCount = 0
        await ctx.send('Please wait, generating list.')
        for tornID in members:
            playerInfo = members[tornID]
            lastAction = playerInfo["last_action"]["relative"]
            playerName = playerInfo['name']
            splitStrings = lastAction.split()
            if splitStrings[1] == "minutes" and int(splitStrings[0]) < 6:
                onlinerCount += 1
                onlinerList.append(playerName + " [" + tornID + '] ' + lastAction)
        sendString = "Players online in the past 5 minutes: \n ```"
        for state in onlinerList:
            sendString = (sendString + " " + state + " " + "\n")
        await asyncio.sleep(3)
        await ctx.send(sendString + f'\nIn total, {onlinerCount} players are online.```')

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
        inactiveCount = 0
        for tornID in members:
            playerInfo = members[tornID]
            lastAction = playerInfo["last_action"]["relative"]
            playerName = playerInfo['name']
            splitStrings = (lastAction.split())
            if splitStrings[1] == "hours" and int(splitStrings[0]) > 10:
                inactiveCount += 1
                inactivePlayers.append(playerName + " [" + tornID + '] ' + lastAction)
            elif splitStrings[1] == "day" or splitStrings[1] == "days":
                inactiveCount += 1
                inactivePlayers.append(playerName + " [" + tornID + '] ' + lastAction)
        sendString = "Players Inactive for 10 hours or more: \n ```"
        for state in inactivePlayers:
            sendString = (sendString + " " + state + " " + "\n")
        await asyncio.sleep(3)
        await ctx.send(sendString + f"In total, {inactiveCount} players are inactive.```")

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
        await asyncio.sleep(1)
        await ctx.send(f"Winner winner chicken dinner! {res} wins a prize from {ctx.author.nick}!")

    @WWCD.error
    async def wwcd_error(self, ctx, error):
        return

    @commands.command()
    async def trackxanax(self, ctx, name=None):
        if checkCouncilRoles(ctx.author.roles) is False:
            await ctx.author.send("You do not have permissions to use this command: \"" + ctx.message.content + "\"")
            return
        if not name:
            name = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        if os.path.exists(f"./xanax/{name}-xanaxinfo.json"):
            await ctx.send("Error, this will overwrite an existing file! Please choose a custom name.")
            return
        await ctx.send("Please wait, this will take around a minute.")
        async with aiohttp.ClientSession() as session:
            r = await fetch(session, f'https://api.torn.com/faction/?selections=basic&key={apiKey}')
        factionInfo = json.loads(r)
        members = factionInfo["members"]
        memberDict = {}
        for memberID in members:
            memberName = members[memberID]["name"]
            async with aiohttp.ClientSession() as session:
                r = await fetch(session, f'https://api.torn.com/user/{memberID}?selections=personalstats&key={apiKey}')
            userInfo = json.loads(r)
            if "error" in userInfo:
                await asyncio.sleep(50)
            xanaxTaken = userInfo["personalstats"]["xantaken"]
            overdoses = userInfo["personalstats"]["overdosed"]
            memberDict[memberName] = {"xantaken": xanaxTaken, "overdoses": overdoses}
            await asyncio.sleep(1)
        fullTime = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(time.time()))
        jsonInfo = json.dumps({"time": time.time(), "date": fullTime, "members": memberDict}, indent=2)
        outf = open(f"./xanax/{name}-xanaxinfo.json", "w")
        outf.write(jsonInfo)
        outf.close()
        with open(f"./xanax/{name}-xanaxinfo.json", "rb") as outf:
            print("opened")
            await ctx.send(f"Here is your report. The file is saved as: \'{name}-xanaxinfo.json\'",
                           file=discord.File(outf, "xanax_report.json"))

    @commands.command()
    async def checkxanax(self, ctx, minimum):
        if checkCouncilRoles(ctx.author.roles) is False:
            await ctx.author.send("You do not have permissions to use this command: \"" + ctx.message.content + "\"")
            return
        if ctx.author.id not in constants["adminUsers"]:
            await ctx.send("Only a bot administrator can use this command!")
        xanaxFiles = []
        for name in os.listdir("./xanax"):
            if name.endswith("xanaxinfo.json"):
                xanaxFiles.append(name)
        if not xanaxFiles:
            await ctx.send("There are no files to compare!")
            return
        sendFiles = []
        fileIndex = {}
        i = 1
        for file in xanaxFiles:
            sendFiles.append(f"{i} -> {file}")
            fileIndex[str(i)] = file
            i += 1
        fn = "\n".join(sendFiles)
        await ctx.send("Here are the availible files to check: \n" + fn)
        await ctx.send("Choose the file you want to check by responding with the number to the left of the filename.")

        def check(m):
            if m.author == ctx.author and m.channel == ctx.channel:
                return True
            else:
                return False

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            return
        else:
            file = fileIndex[msg.content]
            if msg.content.isdigit is False:
                await ctx.send("That is an invalid number.")
                return
        with open(f"./xanax/{file}", "r") as ofile:
            previousJson = json.load(ofile)
        previousTime = previousJson["time"]
        days = abs(previousTime - time.time()) / 86400
        if days < 1:
            await ctx.send("You cannot check a report that was generated less than 24 hours ago. ")
            return
        await ctx.send(f"Checking members who have a lower than {minimum} xanax/day ratio, across {round(days,2)} days. "
                       f"\nPlease wait, this will take around a minute.")
        previousCheck = previousJson["members"]
        async with aiohttp.ClientSession() as session:
            r = await fetch(session, f'https://api.torn.com/faction/?selections=basic&key={apiKey}')
        factionInfo = json.loads(r)
        members = factionInfo["members"]
        belowMin = []
        for memberID in members:
            memberName = members[memberID]["name"]
            if memberName not in previousCheck:
                continue
            async with aiohttp.ClientSession() as session:
                r = await fetch(session, f'https://api.torn.com/user/{memberID}?selections=personalstats&key={apiKey}')
            userInfo = json.loads(r)
            xanaxTaken = userInfo["personalstats"]["xantaken"]
            xanaxDifference = xanaxTaken - previousCheck[memberName]['xantaken']
            if xanaxDifference / int(days) < int(minimum):
                overdoses = userInfo["personalstats"]["overdosed"] - previousCheck[memberName]["overdoses"]
                belowMin.append([memberName, round((xanaxDifference + overdoses * 3) / int(days), 2), overdoses])
            await asyncio.sleep(1)
        belowMin.sort(key=lambda x: x[1])
        toJoin = []
        for n in belowMin:
            toJoin.append(f"{n[0]}, Xan/Day: {n[1]}, ODs: {n[2]}")
        await ctx.send("\n".join(toJoin))

    @checkxanax.error
    async def checkxanax_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('You must include a minimum xanax intake!\nEx: !checkxanax 2')

    @commands.command()
    async def comparexanax(self, ctx):
        if checkCouncilRoles(ctx.author.roles) is False:
            await ctx.author.send("You do not have permissions to use this command: \"" + ctx.message.content + "\"")
            return
        xanaxFiles = []
        for name in os.listdir("./xanax"):
            if name.endswith("xanaxinfo.json"):
                xanaxFiles.append(name)
        if not xanaxFiles:
            await ctx.send("There are no files to compare!")
            return
        sendFiles = []
        fileIndex = {}
        i = 1
        for file in xanaxFiles:
            sendFiles.append(f"{i} -> {file}")
            fileIndex[str(i)] = file
            i += 1
        fn = "\n".join(sendFiles)
        await ctx.send("Here are the availible files to compare: \n" + fn)
        await ctx.send("Choose two files to compare by using the number to the left of the filename. Seperate the two "
                       "selections by a comma and a space.")

        def check(m):
            if m.author == ctx.author and m.channel == ctx.channel:
                return True
            else:
                return False

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            return
        else:
            files = []
            choices = msg.content.split(", ")
            if len(choices) != 2:
                await ctx.send("There must be only two arguments")
            files.append(fileIndex[choices[0]])
            files.append(fileIndex[choices[1]])
            with open(f"./xanax/{files[0]}", "r") as ofile:
                fileOne = json.load(ofile)
            with open(f"./xanax/{files[1]}", "r") as ofile:
                fileTwo = json.load(ofile)
            compared = {}
            for member in fileOne["members"]:
                if member not in fileTwo["members"]:
                    continue
                xanDifference = abs(fileOne["members"][member]["xantaken"] - fileTwo["members"][member]["xantaken"])
                odDifference = abs(fileOne["members"][member]["overdoses"] - fileTwo["members"][member]["overdoses"])
                compared[member] = {'xantaken': xanDifference, 'overdoses': odDifference}
            jsonInfo = json.dumps(compared, indent=2)
            with open("tempfile.json", "w+") as ofile:
                ofile.write(jsonInfo)
            with open("tempfile.json", "rb") as ofile:
                await ctx.send(file=discord.File(ofile, 'xanaxinfo.json'))
            await ctx.send("Would you like me to check if people are meeting reqs for this?\nIf yes, respond to this"
                           " with how many xanax a day they should be making. If you do not wish for me to compare, "
                           "ignore this message or respond \"no\".")

            def check(m):
                if m.author == ctx.author and m.channel == ctx.channel:
                    return True
                else:
                    return False

            try:
                msg = await self.bot.wait_for('message', check=check, timeout=30)
            except asyncio.TimeoutError:
                os.remove("tempfile.json")
                return
            else:
                os.remove("tempfile.json")
                if msg.content.isdigit():
                    xanNeeded = int(msg.content)
                else:
                    return
            toJoin = []
            for member in compared:
                daysDiff = abs(fileOne['time'] - fileTwo['time']) / 86400
                if compared[member]['xantaken'] / daysDiff < xanNeeded:
                    toJoin.append(f"{member}, Xan/Day: {round(compared[member]['xantaken'] / daysDiff, 2)}, ODs: "
                                  f"{compared[member]['overdoses']}")
            await ctx.send("\n".join(toJoin))

    @commands.command()
    async def files(self, ctx, arg1):
        if checkCouncilRoles(ctx.author.roles) is False:
            await ctx.author.send("You do not have permissions to use this command: \"" + ctx.message.content + "\"")
            return
        if arg1 == "list":
            xanF = []
            for name in os.listdir("./xanax"):
                if name.endswith("xanaxinfo.json"):
                    xanF.append(name)
            await ctx.send("\n".join(xanF))
        elif arg1 == "remove":
            await ctx.send("What file would you like to remove? Respond with the files corresponding number.")
            sendFiles = []
            fileIndex = {}
            i = 1
            xanF = []
            for name in os.listdir("./xanax"):
                if name.endswith("xanaxinfo.json"):
                    xanF.append(name)
            for file in xanF:
                sendFiles.append(f"{i} -> {file}")
                fileIndex[str(i)] = file
                i += 1
            await ctx.send("\n".join(sendFiles))

            def check(m):
                if m.author == ctx.author and m.channel == ctx.channel:
                    return True
                else:
                    return False

            try:
                msg = await self.bot.wait_for('message', check=check, timeout=30)
            except asyncio.TimeoutError:
                return
            else:
                file = fileIndex[msg.content]
                if msg.content.isdigit is False:
                    await ctx.send("That is an invalid number.")
                    return
                os.remove(f"./xanax/{file}")
                await ctx.send(f"{file} has been removed")
        else:
            await ctx.send("That is not a valid argument")

    @files.error
    async def files_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('You must include an argument.')


def setup(bot):
    bot.add_cog(Faction(bot))
