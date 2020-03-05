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
inverseNpcList = {}
npcIDs = ["4", "15"]
lcount = 0
for npc in npcList:
    npcIndex[npc] = lcount
    inverseNpcList[lcount] = npc
    npcTimes[npc] = 0
    npcReady[npc] = True
    lcount += 1

#async def clearMessages(bot, messages):
    #for message in messages:
      #  print(message)

async def checkNPC():
    r = requests.get("https://yata.alwaysdata.net/loot/timings/")
    npcRequest = json.loads(r.text)
    for i in npcRequest:
        npcInfo = npcRequest[i]
        npcName = npcInfo["name"]
        npcTimes[npcName] = npcInfo["timings"]["4"]["due"]
    for inverseNpc in inverseNpcList:
        npcName = npcList[int(inverseNpc)]
        fourTime = npcTimes[npcName]
        if fourTime < 0:
            npcReady[npcName] = True
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
                await npcChannel.send(embed=embed)
                await npcChannel.send(npcSendLink + " <@&612556617153511435>")
                npcReady[npcName] = False



class Npc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        global npcChannel

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

    @commands.Cog.listener()
    async def on_ready(self):
        print("NPC Cog Ready!")
        global npcChannel
        npcChannel = self.bot.get_channel(685164100191649849)
        #npcChannel = self.bot.get_channel(594322325852389397)
        #print(npcChannel.name)
       # print(npcChannel.get_messages())
       # clearMessages(self.bot,npcChannel.messages)
        self.timer.start()

    @tasks.loop(seconds=10)
    async def timer(self):
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