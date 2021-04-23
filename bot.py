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

# Toggle wiki command & functionality on or off
use_wiki_commands = false # toggle
use_wikis = ["example", "iris", "vehiclesplus", "react"]  # specific toggle (included => on)
if use_wiki_commands:
    try:
        import wiki as wikilib
        wikilib.toggle_keys(use_wikis)
    except ImportError:
        print("Unable to import wiki functions. Is the file in your directory?")

# Import subprocess
bot = commands.Bot(command_prefix=".", intents=discord.Intents.default(),
                   case_insensitive=True)

load_dotenv()
#token = os.getenv('token')
token = "ODM1MTE3NDUwNTAwNTA1NjMw.YIKxuw.CcDXLj2JFGYWZmsfpIKslSzGBTM"

logging.basicConfig(filename='console.log',
                    level=logging.INFO,
                    format='[%(asctime)s %(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    )
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

@bot.event
async def on_ready():
    # Marks bot as running
    await bot.change_presence(activity=discord.Game('Reading your timing reports'))
    logging.info('Bota bağlanıldı: {}'.format(bot.user.name))
    logging.info('Bot ID: {}'.format(bot.user.id))
    logging.info('Bot tamamen yüklendi')
    logging.info('Bu botun asıl kodunu yazan: https://github.com/Pemigrade/botflop')

@bot.event
async def on_message(message):
    # Binflop
    if len(message.attachments) > 0 and not message.attachments[0].url.endswith(
        ('.png', '.jpg', '.jpeg', '.mp4', '.mov', '.avi', '.gif', '.image', '.svg')):
        download = message.attachments[0].url
        async with aiohttp.ClientSession() as session:
            async with session.get(download, allow_redirects=True) as r:

                #. r = requests.get(download, allow_redirects=True)
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
                    response = "https://bin.bloom.host/" + key
                    response += "\nTalep eden kişi" + message.author.mention
                    if truncated:
                        response += "\n(dosya çok uzun olduğundan kesildi.)"
                    embed_var = discord.Embed(title="Lütfen bir paste hizmeti kullanın", color=0x1D83D4)
                    embed_var.description = response
                    await message.channel.send(embed=embed_var)
    timings = bot.get_cog('Timings')
    await timings.analyze_timings(message)
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send(f'Treas Timings Anlık Ping: {round(bot.latency * 1000)}ms')

@bot.command()
async def wiki(ctx, *args):
    if use_wiki_commands:
        await wikilib.wiki(ctx, *args)

@bot.command()
async def invite(ctx):
    await ctx.send('Kendi sunucuna davet edebilmen için:\nhttps://discord.com/oauth2/authorize?client_id=835117450500505630&permissions=68608&scope=bot')

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
