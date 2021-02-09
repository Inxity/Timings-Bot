"""
This is the file where you add wiki pages with URLs and plugin command alts.
This can be omitted, in which case none of these functions will be available.
All command functionality is included in this file.

Feel free to add more indexes, command alts, and other plugins' wikis altogether.
"""

from difflib import get_close_matches

""" Wiki definitions
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

def get_wikis():
    return wikis

def set_wikis(wiki):
    global wikis
    wikis = wiki

def toggle_keys(keys):
    for key in list(wikis.keys()):
        if wikis[key] not in keys:
            wikis[key] = "none"
    set_wikis(wikis)

""" Wiki variable description
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



"""
Used to get wiki page index.
Modify dictionaries "wikis" and "wikialts" to properly map.
Note the example wiki.
"""
async def wiki(ctx, *args):
    # Prevent passing no plugin or argument
    if len(args) <= 1 or args[0] == 'help':
        await ctx.send('Please specify the plugin & page you want to link e.g. `.wiki <name> main.`' + 
            '\nYou can also use `.wiki index <name>` to get the full index.')
        return

    # Send indexing if available
    if args[0] == 'index':
        close_match = get_close_matches(args[1], list(wikialts.keys()), 1, 0.4)[0] # Gets most likely wiki in dictionary
        if len(close_match) == 0 or close_match == 'none':
            await ctx.send('No match found for plugin entry. Please doublecheck.')
            return
        wiki_name = wikis[wikialts[close_match[0]]] # Finds actual wiki name as in function
        indexing = "**{} index:**\n\n".format(wiki_name.capitalize())
        for key in list(eval('wiki_{}_pages'.format(wiki_name))):
            indexing += " - {}\n".format(key)
        indexing += "\nMain path: {}".format(eval("wiki_{}_path".format(wiki_name)))
        await ctx.send(indexing)
        return

    # Get wiki type and run respective function
    close_match = get_close_matches(args[0], list(wikialts.keys()), 1, 0.4) # Gets most likely wiki in dictionary
    if len(close_match) == 0 or wikis[wikialts[close_match[0]]] == "none":
        await ctx.send('No match found for plugin entry. Please doublecheck.')
        return
    wiki_name = wikis[wikialts[close_match[0]]] # Finds actual wiki name as in function
    result = await eval('wiki_' + wiki_name + '("'+ str(args[1]).lower() + '")') # Evaluates function
    if result[0] == -1:
        await ctx.send('no URL found, please doublecheck the page entry')
        return
    wiki_name = wiki_name.capitalize() # Make first letter caps
    await ctx.send('Match: {} | Wiki page ({}) URL is: \n{}.'.format(wiki_name, result[1], result[0]))



""" Returns closest matched page to the specified command
    To create a new entry, copy-paste the function and replace:
    'example' with the name of your plugin everywhere, and
    create new definitions at the top for the path and pages.
    You find more examples there.
"""
async def wiki_example(page):
    # Add path to url and find closest match to entry
    match = get_close_matches(page, list(wiki_example_pages.keys()), 1, 0.4)

    # Make sure a match was found
    if len(match) == 0:
        return [-1, -1]
    else:
        url = wiki_example_path + wiki_example_pages[match[0]]
        return [url, match[0]]

async def wiki_iris(page):
    # Add path to url and find closest match to entry
    match = get_close_matches(page, list(wiki_iris_pages.keys()), 1, 0.4)

    # Make sure a match was found
    if len(match) == 0:
        return [-1, -1]
    else:
        url = wiki_iris_path + wiki_iris_pages[match[0]]
        return [url, match[0]]

async def wiki_vehiclesplus(page):
    # Add path to url and find closest match to entry
    match = get_close_matches(page, list(wiki_vehiclesplus_pages.keys()), 1, 0.4)

    # Make sure a match was found
    if len(match) == 0:
        return [-1, -1]
    else:
        url = wiki_vehiclesplus_path + wiki_vehiclesplus_pages[match[0]]
        return [url, match[0]]
    
async def wiki_react(page):
    # Add path to url and find closest match to entry
    match = get_close_matches(page, list(wiki_react_pages.keys()), 1, 0.4)

    # Make sure a match was found
    if len(match) == 0:
        return [-1, -1]
    else:
        url = wiki_react_path + wiki_react_pages[match[0]]
        return [url, match[0]]