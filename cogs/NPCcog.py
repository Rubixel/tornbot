import discord
from discord.ext import commands, tasks
import json
import aiohttp
from Tornbot import fetch

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
reactMessage = ""
for npc in npcList:
    npcIndex[npc] = lCount
    inverseNpcList[lCount] = npc
    npcTimes[npc] = 0
    npcReady[npc] = True
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
        if 200 < fourTime < 400:
            if npcReady[npcName] is True:
                readyMinutes = str(fourTime // 60)
                readySeconds = str(fourTime % 60)
                npcSendName = npcName + " [" + npcIDs[npcIndex[npcName]] + "]"
                npcSendTime = readyMinutes + " minutes and " + readySeconds + " seconds."
                npcSendLink = "https://www.torn.com/loader.php?sid=attack&user2ID=" + npcIDs[npcIndex[npcName]]
                embed = discord.Embed(title=npcSendName, color=0xae0000)
                embed.set_thumbnail(url=constants["npcImageLinks"][inverseNpc])
                embed.add_field(name="Ready to be attacked in: ", value=npcSendTime, inline=False)
                npcFourMessages[npcName] = await npcChannel.send(npcSendLink + "<@&612556617153511435>", embed=embed)
                npcReady[npcName] = False


async def checkNpcAlerts():
    for name in npcFourMessages:
        fourTime = await getNpcTimes(name)
        if fourTime > 400:
            npcReady[name] = True
            # todo add an alive function for NPC that doesnt use YATA api, after othercog
            await npcFourMessages[name].delete()
            del npcFourMessages[name]
            return


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
    global reactMessage
    reactMessage = await channel.send("Click the emote attached to this message to add/remove the NPC role!")
    await reactMessage.add_reaction(emoji="✅")
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


async def hasNPC(roles):
    for role in roles:
        if role.name == "NPC":
            return True
    return False


class Npc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        userID = user.id
        message = reaction.message
        if userID == 578674131344556043 or userID == 578394320533717022:
            return
        if message.id == reactMessage.id:
            await message.remove_reaction("✅", user)
        else:
            return
        roles = user.roles
        if await hasNPC(roles):
            role = discord.utils.get(message.guild.roles, id=612556617153511435)
            await user.remove_roles(role)
            await user.send("NPC removed!")
        else:
            role = discord.utils.get(message.guild.roles, id=612556617153511435)
            await user.add_roles(role)
            await user.send("NPC added!")

    @commands.Cog.listener()
    async def on_ready(self):
        print("NPC Cog Ready!")
        global npcChannel
        npcChannel = self.bot.get_channel(685164100191649849)
        #npcChannel = self.bot.get_channel(594322325852389397)
        await npcChannel.purge(limit=1000)
        await startNpcEmbeds(npcChannel)
        self.timer.start()

    @tasks.loop(seconds=100)
    async def timer(self):
        await refreshNpcEmbeds()
        await checkNPC()
        await checkNpcAlerts()

    @commands.command()
    async def npcs(self, ctx):
        async with aiohttp.ClientSession() as session:
            r = await fetch(session, "https://yata.alwaysdata.net/loot/timings/")
        npcRequest = json.loads(r)
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
