import discord
from discord.ext import commands, tasks
import json
import aiohttp
from functions import fetch

with open('config.json') as f:
    constants = json.load(f)

onReadyRun = False
npcChannel = ""
npcReady = {}
npcEmbeds = {}
npcNames = ["Duke", "Leslie", "Jimmy"]
npcFourMessages = {}
for name in npcNames:
    npcFourMessages[name] = None
    npcReady[name] = True


async def checkNPC():
    async with aiohttp.ClientSession() as session:
        r = await fetch(session, "https://yata.alwaysdata.net/loot/timings/")
    npcInfo = json.loads(r)
    for npcID in npcInfo:
        npcName = npcInfo[npcID]['name']
        npcTimings = npcInfo[npcID]['timings']
        npcDue = npcTimings['4']['due']
        if 200 < npcDue < 400:
            if npcReady[npcName]:
                npcReady[npcName] = False
                embed = discord.Embed(title=f"{npcName} [{npcID}]", color=0xae0000)
                embed.set_thumbnail(url=constants["npcImageLinks"][npcName])
                embed.add_field(name="Ready to be attacked in: ", value=f"{npcDue // 60} minutes and "
                                                                        f"{npcDue % 60} seconds", inline=False)
                npcFourMessages[npcName] = await npcChannel.send(f"https://www.torn.com/loader.php?sid=attack&user"
                                                                 f"2ID={npcID} <@&612556617153511435>", embed=embed)


async def checkNpcAlerts():
    async with aiohttp.ClientSession() as session:
        r = await fetch(session, "https://yata.alwaysdata.net/loot/timings/")
    npcInfo = json.loads(r)
    for npcID in npcInfo:
        npcName = npcInfo[npcID]['name']
        if npcInfo[npcID]['timings']['4']['due'] > 400 and npcFourMessages[npcName]:
            await npcFourMessages[npcName].delete()
            npcReady[npcName] = True
            npcFourMessages[npcName] = None


async def startNpcEmbeds(channel):
    async with aiohttp.ClientSession() as session:
        r = await fetch(session, "https://yata.alwaysdata.net/loot/timings/")
    npcInfo = json.loads(r)
    for npcID in npcInfo:
        npcName = npcInfo[npcID]['name']
        npcTime = npcInfo[npcID]['timings']
        npcDue = npcTime['4']['due']
        currentLevel = constants["romanNumbers"][str(npcInfo[npcID]['levels']['current'])]
        if npcDue // 3600 == "0":
            hours = ""
        else:
            hours = f"{npcDue // 3600} hours, "
        if npcDue > 0:
            sendTime = f"{hours} {npcDue // 60 % 60} minutes, {npcDue % 60} seconds."
        else:
            sendTime = "Already Level Four"
        embed = discord.Embed(title=f"{npcName} [{npcID}]", url=f"https://www.torn.com/loader.php?sid=attack&user2ID="
                                                                f"{npcID}",
                              color=0x3251cb)
        embed.set_thumbnail(url=constants["npcImageLinks"][npcName])
        embed.add_field(name="Current Status", value="Level: " + currentLevel, inline=False)
        embed.add_field(name="Level IV is in:", value=sendTime, inline=True)
        npcEmbeds[npcName] = await channel.send(embed=embed)


async def refreshNpcEmbeds():
    async with aiohttp.ClientSession() as session:
        r = await fetch(session, "https://yata.alwaysdata.net/loot/timings/")
    npcInfo = json.loads(r)
    for npcID in npcInfo:
        npcName = npcInfo[npcID]['name']
        npcTime = npcInfo[npcID]['timings']
        npcDue = npcTime['4']['due']
        currentLevel = constants["romanNumbers"][str(npcInfo[npcID]['levels']['current'])]
        message = npcEmbeds[npcName]
        if npcDue // 3600 == "0":
            hours = ""
        else:
            hours = f"{npcDue // 3600} hours, "
        if npcDue > 0:
            sendTime = f"{hours} {npcDue // 60 % 60} minutes, {npcDue % 60} seconds."
        else:
            sendTime = "Already Level Four"
        embed = discord.Embed(title=f"{npcName} [{npcID}]", url="https://www.torn.com/loader.php?sid=attack&user2ID="
                                                                + npcID,
                              color=0x3251cb)
        embed.set_thumbnail(url=constants["npcImageLinks"][npcName])
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
    async def on_ready(self):
        global onReadyRun
        if onReadyRun is True:
            return
        onReadyRun = True
        print("NPC Cog Ready!")
        global npcChannel
        if not constants['botTestingMode']:
            npcChannel = self.bot.get_channel(685164100191649849)
        else:
            npcChannel = self.bot.get_channel(594322325852389397)
        await npcChannel.purge(limit=100)
        await startNpcEmbeds(npcChannel)
        self.timer.start()

    @tasks.loop(seconds=100)
    async def timer(self):
        await refreshNpcEmbeds()
        await checkNPC()
        await checkNpcAlerts()


def setup(bot):
    bot.add_cog(Npc(bot))
