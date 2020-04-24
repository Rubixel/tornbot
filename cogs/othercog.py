import json
import random
import re
import time
import aiohttp
import discord
from discord.ext import commands, tasks

from functions import fetch, constants, getIDfromDiscord, jfetch
from bot_keys import apiKey, imKey, imSecret

randBully = 0
tessaChannel = ""


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
        global tessaChannel
        if constants["onReadyRun"] is False:
            constants["onReadyRun"] = True
            random.seed()
            rand = random.randrange(0, len(constants["bullyList"]))
            await self.bot.change_presence(activity=discord.Game('Bullying ' + constants["bullyList"][rand] + "!"))
            if constants["botTestingMode"]:
                tessaChannel = self.bot.get_channel(id=594322325852389397)
            else:
                tessaChannel = self.bot.get_channel(id=559776463126134818)
            print("================================")
            print("Start time: " + str(time.time()))
            print("Start time: " + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
            print("Tornbot.py is ready.")
            print("================================")
            self.timer.start()

    @commands.command()
    async def profile(self, ctx, arg1):
        # detects if the command format is used: xprofile @Hcom [2003693]
        if ctx.message.mentions:
            mention = ctx.message.mentions[0]
            memberID = await getIDfromDiscord(mention.id)
        else:
            if arg1.isdigit():
                memberID = arg1
            else:
                # if they put a number or non digit symbol in their command, returns and error
                await ctx.send("Error! TornID must be only digits!")
                return
        if memberID:
            # gets player info
            async with aiohttp.ClientSession() as session:
                r = await fetch(session,
                                "https://api.torn.com/user/" + memberID + "?selections=profile,personalstats&key="
                                                                          "" + apiKey)
            userInfo = json.loads(r)
            # detects if there was an error/ if the ID provided isn't a real one
            if "error" in userInfo:
                await ctx.send(f"Error: Code: {userInfo['error']['code']}, {userInfo['error']['error']}")
                return
            # gets all of the information from the API request
            personalStats = userInfo['personalstats']
            lifeInfo = userInfo["life"]
            facInfo = userInfo["faction"]
            jobInfo = userInfo["job"]
            # changes the output depending on the result of the API
            if facInfo["faction_id"] == 0:
                factionStatus = "Not in a faction"
            else:
                factionStatus = f"{facInfo['position']} of [{facInfo['faction_name']}](https://www.torn.com/factions" \
                                f".php?step=profile&ID={facInfo['faction_id']}) for {facInfo['days_in_faction']} days"
            if jobInfo["company_id"] == 0:
                if jobInfo["position"] == "None":
                    jobStatus = "Not in a job"
                else:
                    jobStatus = jobInfo['position']
            else:
                jobStatus = f"{jobInfo['position']} of [{jobInfo['company_name']}](https://www.torn.com/joblist.php#/" \
                            f"p=corpinfo&ID={jobInfo['company_id']})"
            if userInfo["married"]["duration"] == 0:
                marriageStatus = "Single"
            else:
                marriageStatus = f"Married to: [{userInfo['married']['spouse_name']}]" \
                                 f"(https://www.torn.com/profiles.php?XID={userInfo['married']['spouse_id']}) " \
                                 f"for {userInfo['married']['duration']} days"
            embed = discord.Embed(color=0x0eaf0a, title=f"{userInfo['name']} [{memberID}]",
                                  url=f"https://www.torn.com/profiles.php?XID={memberID}")
            embed.add_field(name="**Basic Details**:",
                            value=f"Level: {userInfo['level']}\nRank: {userInfo['rank']}\nAge: {userInfo['age']}\n"
                                  f"Gender: {userInfo['gender']}\nProperty: {userInfo['property']}\n"
                                  f"Awards: {userInfo['awards']}\nNetworth: ${personalStats['networth']:,}\n"
                                  f"Xanax Taken: {personalStats['xantaken']}", inline=False)
            embed.add_field(name="**Status**:", value=f"Life: {lifeInfo['current']}/{lifeInfo['maximum']}\n"
                                                      f"Status: {userInfo['status']['description']}\nLast "
                                                      f"Online: {userInfo['last_action']['relative']}", inline=False)
            embed.add_field(name="**Faction/Job**:", value=factionStatus + "\n" + jobStatus, inline=False)
            embed.add_field(name="**Marriage Status**:", value=marriageStatus, inline=False)
            await ctx.author.send(embed=embed)
            await ctx.message.add_reaction(emoji="👍")
            await ctx.message.delete(delay=15)

    @profile.error
    async def profile_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('You must include a player ID, or ping a player.\nExample: '
                           '!profile 2003693 or !profile @hcom')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

    @commands.command()
    async def bbhelp(self, ctx):
        embed = discord.Embed(title="Help screen:", description="All available commands:")
        embed.set_thumbnail(url="https://i.imgur.com/JIsJGhb.png")
        embed.add_field(name="onliners [factionID]ᴿ", value="Prints players active in the last five minutes.",
                        inline=True)
        embed.add_field(name="inactives [factionID]ᴿ", value="Prints players inactive for over 10 hours.",
                        inline=True)
        embed.add_field(name="profile [playerID]ᴿ", value="Prints a player's basic information & status.", inline=True)
        embed.add_field(name="help", value="Prints help screen.", inline=True)
        embed.add_field(name="Restricted:", value="ᴿIs restricted to council/leaders/admins.\n", inline=True)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel != tessaChannel:
            return
        if message.author.id == 525443694644559894 or message.author.id == 200676892024504320:
            text = message.content
            urls = re.findall('http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
            for img in message.attachments:
                urls.append(img.url)
            for url in urls:
                if url.endswith(".png") or url.endswith(".jpeg") or url.endswith(".jpg"):
                    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(imKey, imSecret)) as session:
                        response = await jfetch(session, 'https://api.imagga.com/v2/tags?image_url=%s' % url)
                    tags = response["result"]["tags"]
                    for x in tags:
                        print(x)
                        if x["tag"]["en"] in constants["dogs"]:
                            print("its a dog!")
                            for tag in tags:
                                print(tag)
                                if tag["tag"]["en"] in constants["tessa"]:
                                    if tag["confidence"] > 40:
                                        print("tessa")
                                        await message.add_reaction(emoji="🥇")
                                        return
                                elif tag["tag"]["en"] in constants["bestBoy"]:
                                    if tag["confidence"] > 40:
                                        print("easton")
                                        return
                            return


def setup(bot):
    bot.add_cog(Other(bot))
