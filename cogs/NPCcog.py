import discord
from discord.ext import commands, tasks
import json
import aiohttp
from Tornbot import fetch
import requests

with open('config.json') as f:
    constants = json.load(f)

npcList = ["Duke", "Leslie"]
npcChannel = ""
npcIndex = {}
npcReady = {}
npcTimes = {}
npcEmbedIDs = {}
inverseNpcList = {}
npcFourMessages = {}
npcIDs = ["4", "15"]
lCount = 0
for npc in npcList:
    npcIndex[npc] = lCount
    inverseNpcList[lCount] = npc
    npcTimes[npc] = 0
    npcReady[npc] = True
    npcFourMessages[npc] = None
    lCount += 1


async def checkNPC():
    async with aiohttp.ClientSession() as session:
        r = await fetch(session, "https://yata.alwaysdata.net/loot/timings/")
    npcRequest = json.loads(r)
    for i in npcRequest:
        npcInfo = npcRequest[i]
        npcName = npcInfo["name"]
        npcTimes[npcName] = npcInfo["timings"]["4"]["due"]
    for inverseNpc in inverseNpcList:
        npcName = npcList[int(inverseNpc)]
        fourTime = npcTimes[npcName]
        if fourTime > 10000 and npcReady[npcName] is False:
            await npcFourMessages[npcName].delete()
            npcFourMessages[npcName] = None
            npcReady[npcName] = True
            return
        if 100 < fourTime < 400:
            if npcReady[npcName] is True:
                readyMinutes = str(fourTime // 60)
                readySeconds = str(fourTime % 60)
                npcSendName = npcName + " [" + npcIDs[npcIndex[npcName]] + "]"
                npcSendTime = readyMinutes + " minutes and " + readySeconds + " seconds."
                npcSendLink = "https://www.torn.com/loader.php?sid=attack&user2ID=" + npcIDs[npcIndex[npcName]]
                embed = discord.Embed(title=npcSendName, color=0xae0000)
                embed.set_thumbnail(url=constants["npcImageLinks"][inverseNpc])
                embed.add_field(name="Ready to be attacked in: ", value=npcSendTime, inline=False)
                npcFourMessages[npcName] = await npcChannel.send(npcSendLink + " <@&612556617153511435>", embed=embed)
                npcReady[npcName] = False


async def clearMessages(channel, messages):
    await channel.delete_messages(messages)


async def getNpcTimes(name):
    async with aiohttp.ClientSession() as session:
        r = await fetch(session, "https://yata.alwaysdata.net/loot/timings/")
    npcRequest = json.loads(r)
    npcData = npcRequest[npcIDs[npcIndex[name]]]
    fourTime = npcData['timings']['4']['due']
    return fourTime


async def getNpcLevel(name):
    async with aiohttp.ClientSession() as session:
        r = await fetch(session, "https://yata.alwaysdata.net/loot/timings/")
    npcRequest = json.loads(r)
    npcData = npcRequest[npcIDs[npcIndex[name]]]
    currentLevel = npcData['levels']['current']
    return currentLevel


async def startNpcEmbeds(channel):
    for npcName in npcList:
        fourTime = await getNpcTimes(npcName)
        currentLevel = await getNpcLevel(npcName)
        currentLevel = constants["romanNumbers"][str(currentLevel)]
        npcSendName = npcName + " [" + npcIDs[npcIndex[npcName]] + "]"
        readyHours = str(fourTime // 3600)
        if readyHours == "0":
            hours = ""
        else:
            hours = readyHours + " hours, "
        if fourTime > 0:
            sendTime = hours + str(fourTime // 60 % 60) + " minutes, " + str(fourTime % 60) + " seconds."
        else:
            sendTime = "Already Level Four"
        embed = discord.Embed(title=npcSendName, url="https://www.torn.com/loader.php?sid=attack&user2ID=" + npcIDs[
            npcIndex[npcName]], color=0x3251cb)
        embed.set_thumbnail(url=constants["npcImageLinks"][npcIndex[npcName]])
        embed.add_field(name="Current Status", value="Level: " + currentLevel, inline=False)
        embed.add_field(name="Level IV is in:", value=sendTime, inline=True)
        npcEmbedIDs[npcName] = await channel.send(embed=embed)


async def refreshNpcEmbeds():
    for npcName in npcEmbedIDs:
        message = npcEmbedIDs[npcName]
        fourTime = await getNpcTimes(npcName)
        currentLevel = await getNpcLevel(npcName)
        currentLevel = constants["romanNumbers"][str(currentLevel)]
        npcSendName = npcName + " [" + npcIDs[npcIndex[npcName]] + "]"
        readyHours = str(fourTime // 3600)
        if readyHours == "0":
            hours = ""
        else:
            hours = readyHours + " hours, "
        if fourTime > 0:
            sendTime = hours + str(fourTime // 60 % 60) + " minutes, " + str(fourTime % 60) + " seconds."
        else:
            sendTime = "Already Level Four"
        embed = discord.Embed(title=npcSendName, url="https://www.torn.com/loader.php?sid=attack&user2ID=" + npcIDs[
            npcIndex[npcName]], color=0x3251cb)
        embed.set_thumbnail(url=constants["npcImageLinks"][npcIndex[npcName]])
        embed.add_field(name="Current Status", value="Level: " + currentLevel, inline=False)
        embed.add_field(name="Level IV is in:", value=sendTime, inline=True)
        await message.edit(embed=embed)


class Npc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

    @commands.Cog.listener()
    async def on_ready(self):
        print("NPC Cog Ready!")
        global npcChannel
        npcChannel = self.bot.get_channel(685164100191649849)
        messages = await npcChannel.history(limit=1000).flatten()
        await clearMessages(npcChannel, messages)
        await startNpcEmbeds(npcChannel)
        self.timer.start()

    @tasks.loop(seconds=100)
    async def timer(self):
        await refreshNpcEmbeds()
        await checkNPC()

    @commands.command()
    async def npcs(self, ctx):
        r = requests.get("https://yata.alwaysdata.net/loot/timings/")
        npcRequest = json.loads(r.text)
        for i in npcRequest:
            npcInfo = npcRequest[i]
            npcName = npcInfo["name"]
            npcTimes[npcName] = npcInfo["timings"]["4"]["due"]
        sendmessage = "The NPCs will be level four in:\n"
        for inverseNpc in inverseNpcList:
            npcName = npcList[int(inverseNpc)]
            fourTime = npcTimes[npcName]
            readyHours = str(fourTime // 3600)
            if readyHours == "0":
                hours = ""
            else:
                hours = readyHours + " hours, "
            if fourTime > 0:
                sendmessage = sendmessage + npcName + ": " + hours + str(fourTime // 60 % 60) + " minutes, " + str(
                    fourTime % 60) + " seconds.\n"
            else:
                sendmessage = sendmessage + npcName + ": Already Level Four\n"
        await ctx.send(sendmessage)


def setup(bot):
    bot.add_cog(Npc(bot))
