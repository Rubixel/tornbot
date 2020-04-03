import asyncio
import json
import random
import time

import aiohttp
import discord
from discord.ext import commands, tasks

from Tornbot import fetch, constants, checkCouncilRoles, jfetch
from bot_keys import apiKey

randBully = 0
apiChecks = 0
lastMinute = ""


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


class Other(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

    @tasks.loop(seconds=20)
    async def timer(self):
        global randBully
        randBully += 20
        if randBully >= 3600:
            randBully = 0
            random.seed()
            rand = random.randrange(0, len(constants["bullyList"]))
            await self.bot.change_presence(activity=discord.Game('Bullying ' + constants["bullyList"][rand] + "!"))

    @commands.Cog.listener()
    async def on_ready(self):
        if constants["onReadyRun"] is False:
            constants["onReadyRun"] = True
            random.seed()
            rand = random.randrange(0, len(constants["bullyList"]))
            await self.bot.change_presence(activity=discord.Game('Bullying ' + constants["bullyList"][rand] + "!"))
            print("================================")
            print("Start time: " + str(time.time()))
            print("Start time: " + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
            print("Tornbot.py is ready.")
            print("================================")
            self.timer.start()

    @commands.command()
    async def torn(self, ctx, playerID):
        if checkCouncilRoles(ctx.author.roles) is False:
            await ctx.send("You do not have permissions to use this command: \"" + ctx.message.content + "\"")
            return
        if playerID.isdigit() is False:
            await ctx.send(playerID + " is not a valid playerID!")
            return
        async with aiohttp.ClientSession() as session:
            r = await fetch(session, 'https://api.torn.com/user/' + playerID + '?selections=basic&key=%s' % apiKey)
        info = json.loads(r)
        if '{"error": {"code": 6, "error": "Incorrect ID"}}' == info:
            await ctx.send("Error: Incorrect ID")
            return
        await ctx.send(
            info['name'] + " is a level " + str(info['level']) + " " + info['gender'] + ". Currently, they are " +
            info['status']['description'] + '.')

    @torn.error
    async def torn_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('You must include a player ID.\nExample: !torn 2003693')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

    @commands.command()
    async def source(self, ctx):
        await ctx.author.send("Github repository link:\nhttps://github.com/Rubixel/tornbot")
        await ctx.message.delete(delay=5)

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(title="Help screen:", description="All available commands:")
        embed.set_thumbnail(url="https://i.imgur.com/JIsJGhb.png")
        embed.add_field(name="onliners [factionID]ᴿ", value="Prints players active in the last five minutes.",
                        inline=True)
        embed.add_field(name="inactives [factionID]ᴿ", value="Prints players inactive for over 10 hours.",
                        inline=True)
        embed.add_field(name="donators [factionID]ᴿ", value="Prints players without donator status, and or a PI.",
                        inline=True)
        embed.add_field(name="torn [playerID]ᴿ", value="Prints a player's basic information & status.", inline=True)
        embed.add_field(name="help", value="Prints help screen.", inline=True)
        embed.add_field(name="npcs", value="Prints how much time is left before each NPC reaches level four.",
                        inline=True)
        embed.add_field(name="source", value="Sends the message author the github repository link.")
        embed.add_field(name="Restricted:", value="ᴿIs restricted to council/leaders/admins.\n", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def verify(self, ctx, tornid):
        if constants["blockVerify"] is True:
            return
        if tornid.isdigit() is False:
            await ctx.send(tornid + " is not a valid playerID!")
            return
        verifyID = tornid
        async with aiohttp.ClientSession() as session:
            tornname = await json.loads(fetch(session, 'https://api.torn.com/user/' + verifyID +
                                              '?selections=basic&key=%s' % apiKey))["name"]
        async with aiohttp.ClientSession() as session:
            data = await json.loads(fetch(session, 'https://api.torn.com/user/' + verifyID +
                                          '?selections=discord&key=%s' % apiKey
                                          ))
        if '{"error": {"code": 6, "error": "Incorrect ID"}}' == json.dumps(data):
            await ctx.send("Error: Incorrect ID")
            return
        discordID = data["discord"]["discordID"]
        if discordID == "":
            await ctx.send(
                tornname + " [" + verifyID + "] is not associated with a discord account. Please verify in Torn's "
                                             "Discord server: https://discordapp.com/invite/TVstvww"
                + "<@" + str(ctx.author.id) + ">")
        elif discordID != str(ctx.author.id):
            await ctx.channel.send(
                tornname + " [" + verifyID + "] is associated with another discord account. Please verify with your "
                                             "Discord account in Torn's Discord server: https://discordapp.com/invite/"
                                             "TVstvww " + "<@" +
                str(ctx.author.id) + ">")
        elif discordID == str(ctx.author.id):
            await ctx.send("Welcome " + tornname + " [" + verifyID + "]!")
            await ctx.author.edit(nick=tornname + " [" + verifyID + "]")

    @verify.error
    async def verify_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You must include a player ID\nExample: !verify 2003693")

    @commands.command()
    async def getchannelinfo(self, ctx):
        # used for assigning channels that the bot posts in
        if checkCouncilRoles(ctx.author.roles) is False:
            await ctx.author.send("You do not have permissions to use this command: \"" + ctx.message.content + "\"")
        print(ctx.message.channel.id)
        print(ctx.message.author.id)

    @commands.command()
    async def WWCD(self, ctx):
        memberList = []
        for factionID in constants["lottoFactions"]:
            async with aiohttp.ClientSession() as session:
                r = await fetch(session, 'https://api.torn.com/faction/'
                                + str(factionID) + '?selections=basic&key=%s' % apiKey)
                factionInfo = json.loads(r)
                for playerID in factionInfo["members"]:
                    memberList.append([factionInfo["members"][playerID]["name"], playerID])
        rand = random.randrange(0, len(memberList))
        pickedMember = memberList[rand]
        await ctx.send("Winner winner chicken dinner! {} [{}] "
                       "wins a prize from {}!".format(pickedMember[0], pickedMember[1], ctx.author.name))

    @WWCD.error
    async def inactive_error(self, ctx, error):
        return


def setup(bot):
    bot.add_cog(Other(bot))
