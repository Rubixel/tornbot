# imports
from discord.ext import commands
import json
import datetime
import bot_keys
import os
# todo always check bot testing mode
from functions import userIsAdmin

with open('config.json') as f:
    constants = json.load(f)
bot = commands.Bot(command_prefix="!", case_insensitive=True)
apiKey = bot_keys.apiKey
botID = bot_keys.bot_id
startTime = datetime.datetime.now()
bot.remove_command("help")
apiChecks = 0
randBully = 0
lastMinute = ""

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

if constants["botTestingMode"] is True:
    botID = bot_keys.testingBotID
bot.run(botID)


@bot.command()
async def load(ctx, extension):
    if userIsAdmin(ctx.author) is False:
        await ctx.atuhor.send("You need to be an administrator of the bot to use this command!")
    if extension not in constants["cogNames"]:
        await ctx.send("Cog " + extension + " not found!")
        return
    bot.load_extension(f'cogs.{extension}')
    await ctx.send("Loaded " + extension)


@bot.command()
async def unload(ctx, extension):
    if userIsAdmin(ctx.author) is False:
        await ctx.atuhor.send("You need to be an administrator of the bot to use this command!")
    if extension not in constants["cogNames"]:
        await ctx.send("Cog " + extension + " not found!")
        return
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send("Unloaded " + extension)


@bot.command()
async def reloadcogs(ctx):
    if userIsAdmin(ctx.author) is False:
        await ctx.atuhor.send("You need to be an administrator of the bot to use this command!")
    for extension in constants["cogNames"]:
        bot.reload_extension(f'cogs.{extension}')
    await ctx.send("Cogs reloaded!")