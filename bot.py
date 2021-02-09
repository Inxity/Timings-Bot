import os
import discord
import requests
import json
import logging
import sys
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions, MissingPermissions
from dotenv import load_dotenv
import aiohttp
from unidecode import unidecode
from difflib import get_close_matches

# Import subprocess

bot = commands.Bot(command_prefix=".", intents=discord.Intents.default(),
                   case_insensitive=True)

load_dotenv()
token = os.getenv('token')

logging.basicConfig(filename='console.log',
                    level=logging.INFO,
                    format='[%(asctime)s %(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    )
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

"""
    Wiki definitions
    'wikis' contains number to function name mappings.
    'wikialts' contains name to number mappings.
    The dict keys in 'wikialts' are approximations to the inputted command.
    We later search for the closest match in the dictionary.
    e.g. 'example' points to 'wiki_example(*defs)' through wikialts and then wikis 

    If you want to delete a plugin, remove its respective entries from 'wikis' and 'wikialts'.
    It does not work if you only delete the index registry under wiki_<name>_pages
"""
wikis = {
    # Name as in function (e.g. wiki_example() )
    -1: 'example',
    0: 'iris',
    1: 'vehiclesplus',
    2: 'react'
}
wikialts = {
    # Example alts
    'example': -1,
    'exam': -1,
    'ex': -1,

    # Iris alts
    'iris': 0,
    'ir': 0,
    'iri': 0,
    'i': 0,

    # VehiclesPlus alts
    'vehiclesplus': 1,
    'vp': 1,
    'vehclesplus': 1,

    # React alts
    'react': 2,
    're': 2,
    'ract': 2,
    'rea': 2
}

"""
    _path describes the main directory path
    _pages is a dictionary of all subsequent pages.
        Keys should be the title of the page
        Make sure to define "main" at least.
"""
wiki_example_path = 'https://docs.gitbook.com/'
wiki_example_pages = {
    "start exploring": "getting-started/start-exploring", # Real page for Gitbook
    "main": "" # Main entry also points to main page
}

wiki_iris_path = 'https://volmitsoftware.gitbook.io/iris/'
wiki_iris_pages = {
    # Main
    "main": "",
    "intro": "",

    "getting started": "getting-started",
    "get started": "getting-started",
    "started": "getting-started",



    # Plugin category
    "commands": "plugin/commands",
    "cmd": "plugin/commands",

    "permissions": "plugin/permissions",
    "perms": "plugin/permissions",

    "configuration": "plugin/configuration",
    "config": "plugin/configuration",

    "faq": "plugin/faq",
    "frequently asked questions": "plugin/faq",



    # Engine category
    "introduction to the engine": "engine/introduction-to-the-engine",
    "engine intro": "engine/introduction-to-the-engine",
    "introduction": "engine/introduction-to-the-engine",

    "studio": "engine/studio",
    "studio intro": "engine/studio",
    "std": "engine/studio",

    "creating a new project": "engine/new-project",
    "new project": "engine/new-project",
    "project": "engine/new-project",

    "understanding": "engine/understanding",
    "understand": "engine/understanding",
        # Understanding subcategory

        "dimension": "engine/understanding/dimensions",
        "dimensions": "engine/understanding/dimensions",
        "dim": "engine/understanding/dimensions",

        "region": "engine/understanding/regions",
        "regions": "engine/understanding/regions",
        "reg": "engine/understanding/regions",

        "biome": "engine/understanding/biomes",
        "biomes": "engine/understanding/biomes",
        "bio": "engine/understanding/biomes",
        
        "generator": "engine/understanding/generators",
        "generators": "engine/understanding/generators",
        "gen": "engine/understanding/generators",
        
        "object": "engine/understanding/objects",
        "objects": "engine/understanding/objects",
        "obj": "engine/understanding/objects",
        
        "jigsaw": "engine/understanding/jigsaw",
        "jig": "engine/understanding/jigsaw",
        
        "loot": "engine/understanding/loot",
        
        "entity": "engine/understanding/entities",
        "entities": "engine/understanding/entities",
        "ent": "engine/understanding/entities",

    "mastering": "engine/mastering",
    "master": "engine/mastering",
        # Mastering subcategory

        "mastering dimension": "engine/mastering/dimensions",
        "mastering dimensions": "engine/mastering/dimensions",
        "mastering dim": "engine/mastering/dimensions",

        "mastering biome": "engine/mastering/biomes",
        "mastering biomes": "engine/mastering/biomes",
        "mastering bio": "engine/mastering/biomes",

        "mastering universal": "engine/mastering/universal-parameters",
        "universal": "engine/mastering/universal-parameters",
        "universal parameters": "engine/mastering/universal-parameters",
        "master universal": "engine/mastering/universal-parameters",

    "packaging and publishing dimension": "engine/packaging-and-publishing",
    "packaging and publishing": "engine/packaging-and-publishing",
    "package and publish": "engine/packaging-and-publishing",
    "package and publish dimension": "engine/packaging-and-publishing",
    "publish dimension": "engine/packaging-and-publishing",
    "upload dimension": "engine/packaging-and-publishing",

    "updating the overworld": "engine/updateoverworld",
    "update overworld": "engine/updateoverworld",
    "updating overworld": "engine/updateoverworld"}

wiki_react_path = 'https://volmitsoftware.gitbook.io/react/'
wiki_react_pages = {
    "main": "" # Main entry also points to main page
}

wiki_vehiclesplus_path = 'https://volmitsoftware.gitbook.io/vehiclesplus/'
wiki_vehiclesplus_pages = {
    "main": "" # Main entry also points to main page
}

@bot.event
async def on_ready():
    # Marks bot as running
    await bot.change_presence(activity=discord.Game('Reading your timing reports'))
    logging.info('Connected to bot: {}'.format(bot.user.name))
    logging.info('Bot ID: {}'.format(bot.user.id))
    logging.info('Bot fully loaded')
    logging.info('Original creators: https://github.com/Pemigrade/botflop')

@bot.event
async def on_message(message):
    # Binflop
    if len(message.attachments) > 0:
        if not message.attachments[0].url.endswith(
                ('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.avi', '.gif', '.image', '.svg')):
            download = message.attachments[0].url
            async with aiohttp.ClientSession() as session:
                async with session.get(download, allow_redirects=True) as r:

                    # r = requests.get(download, allow_redirects=True)
                    text = await r.text()
                    text = unidecode(text)
                    text = "\n".join(text.splitlines())
                    if '�' not in text:  # If it's not an image/gif
                        truncated = False
                        if len(text) > 100000:
                            text = text[:99999]
                            truncated = True
                        req = requests.post('https://bin.bloom.host/documents', data=text)
                        key = json.loads(req.content)['key']
                        response = ""
                        response = response + "https://bin.bloom.host/" + key
                        response = response + "\nRequested by " + message.author.mention
                        if truncated:
                            response = response + "\n(file was truncated because it was too long.)"
                        embed_var = discord.Embed(title="Please use a paste service", color=0x1D83D4)
                        embed_var.description = response
                        await message.channel.send(embed=embed_var)
    timings = bot.get_cog('Timings')
    await timings.analyze_timings(message)
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send(f'Kahti bot ping is {round(bot.latency * 1000)}ms')

@bot.command()
async def invite(ctx):
    await ctx.send('Invite me with this link:\nhttps://discord.com/oauth2/authorize?client_id=801178754772500500&permissions=0&scope=bot')

"""
Used to get Iris wiki page index.
Modify dictionaries "wikis" and "wikialts" to properly map.
Note the example wiki.
"""
@bot.command()
async def wiki(ctx, *args):
    # Prevent passing no plugin or argument
    if len(args) <= 1 or args[0] == 'help':
        await ctx.send('Please specify the plugin & page you want to link e.g. `.wiki <name> main.' + 
            '\nYou can also use `.wiki index <name>` to get the full index.')
        return

    # Send indexing if available
    if args[0] == 'index':
        close_match = get_close_matches(args[1], wikialts.keys(), 1, 0.4)[0] # Gets most likely wiki in dictionary
        if len(close_match) == 0:
            ctx.send('No match found for plugin entry. Please doublecheck.')
            return
        wiki = wikis[wikialts[close_match[0]]] # Finds actual wiki name as in function
        indexing = "**{} index:**\n\n".format(wiki.capitalize())
        for key in eval('wiki_{}_pages'):
            indexing += " - {}\n".format(key)
        indexing += "\nMain path: {}".format(eval("wiki_{}_path".format(wiki)))
        ctx.send(indexing)

    # Get wiki type and run respective function
    close_match = get_close_matches(args[0], wikialts.keys(), 1, 0.4)[0] # Gets most likely wiki in dictionary
    if len(close_match) == 0:
        ctx.send('No match found for plugin entry. Please doublecheck.')
        return
    wiki = wikis[wikialts[close_match[0]]] # Finds actual wiki name as in function
    result = eval('wiki_' + wiki + '({args[1]})') # Evaluates function
    wiki = wiki.capitalize() # Make first letter caps
    ctx.send('Match: {} |  Wiki page for {} is: \n{}.'.format(wiki, result['match'], result['url']))

"""
    Returns closest matched page to the specified command
    To create a new entry, copy-paste the function and replace:
    'example' with the name of your plugin everywhere, and
    create new definitions at the top for the path and pages.
    You find more examples there.
"""
async def wiki_example(page):
    # Add path to url and find closest match to entry
    url = wiki_example_path
    match = get_close_matches(page, wiki_example_pages.keys(), 1, 0.4)

    # Make sure a match was found
    if len(match) == 0:
        return 'no URL found, please doublecheck the page entry'
    else:
        return {'url': url, 'match': match}

async def wiki_iris(page):
    # Add path to url and find closest match to entry
    url = wiki_iris_path
    match = get_close_matches(page, wiki_iris_pages.keys(), 1, 0.4)

    # Make sure a match was found
    if len(match) == 0:
        return 'no URL found, please doublecheck the page entry'
    else:
        return {url: url, match: match}

async def wiki_vehiclesplus(page):
    # Add path to url and find closest match to entry
    url = wiki_vehiclesplus_path
    match = get_close_matches(page, wiki_vehiclesplus_pages.keys(), 1, 0.4)

    # Make sure a match was found
    if len(match) == 0:
        return 'no URL found, please doublecheck the page entry'
    else:
        return {'url': url, 'match': match}
    
async def wiki_react(page):
    # Add path to url and find closest match to entry
    url = wiki_react_path
    match = get_close_matches(page, wiki_react_pages.keys(), 1, 0.4)

    # Make sure a match was found
    if len(match) == 0:
        return 'no URL found, please doublecheck the page entry'
    else:
        return {'url': url, 'match': match}

@bot.command(name="react", pass_context=True)
@has_permissions(administrator=True)
async def react(ctx, url, reaction):
    channel = await bot.fetch_channel(int(url.split("/")[5]))
    message = await channel.fetch_message(int(url.split("/")[6]))
    await message.add_reaction(reaction)
    logging.info('reacted to ' + url + ' with ' + reaction)

for file_name in os.listdir('./cogs'):
    if file_name.endswith('.py'):
        bot.load_extension(f'cogs.{file_name[:-3]}')

bot.run(token)

# full name: message.author.name + "#" + str(message.author.discriminator) + " (" + str(message.author.id) + ")"
