import discord
from discord.ext import commands
import aiohttp
import yaml
import re
import logging

TIMINGS_CHECK = None
YAML_ERROR = None
with open("cogs/timings_check.yml", 'r', encoding="utf8") as stream:
    try:
        TIMINGS_CHECK = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        logging.info(exc)
        YAML_ERROR = exc

VERSION_REGEX = re.compile(r"\d+\.\d+\.\d+")


class Timings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.TIMINGS_TITLE = "Timings Analizi"

    # TODO: Check Tuinity.yml for spawn rate changes
    async def analyze_timings(self, message):
        words = message.content.replace("\n", " ").split(" ")
        timings_url = ""
        embed_var = discord.Embed(title=self.TIMINGS_TITLE)
        embed_var.set_footer(text=f"Unutma, bu değerler en düşük değerler. Kendiniz sunucunuza göre ayarlayabilirsiniz. Bu analizi isteyen kişi {message.author.name}#{message.author.discriminator}", icon_url=message.author.avatar_url)

        for word in words:
            if word.startswith("https://timin") and "/d=" in word:
                word.replace("/d=", "/?id=")
            if word.startswith("https://timin") and "/?id=" in word:
                timings_url = word
                embed_var.url = timings_url
                break
            if word.startswith("https://www.spigotmc.org/go/timings?url=") or word.startswith(
                    "https://timings.spigotmc.org/?url="):
                embed_var.add_field(name="❌ Spigot",
                                    value="Spigot Timings'i çok eski ve az detay içeriyor. Daha iyi bir Timings Analizi için[Paper](https://papermc.io/) kullan.")
                embed_var.url = word
                await message.reply(embed=embed_var)
                return

        if timings_url == "":
            return
        if "#" in timings_url:
            timings_url = timings_url.split("#")[0]
        if "?id=" not in timings_url:
            return
        logging.info(timings_url)

        timings_host, timings_id = timings_url.split("?id=")
        timings_json = timings_host + "data.php?id=" + timings_id
        timings_url_raw = timings_url + "&raw=1"

        async with aiohttp.ClientSession() as session:
            async with session.get(timings_url_raw) as response:
                request_raw = await response.json(content_type=None)
            async with session.get(timings_json) as response:
                request = await response.json(content_type=None)
        if request is None or request_raw is None:
            embed_var.add_field(name="❌ Geçersiz Timings",
                                value="Yeni bir Timings oluştur, -/timings report.")
            await message.reply(embed=embed_var)
            return

        try:
            try:
                version = request["timingsMaster"]["version"] if "version" in request["timingsMaster"] else None
                if "version" in TIMINGS_CHECK and version:
                    version_result = VERSION_REGEX.search(version)
                    version_result = version_result.group() if version_result else None
                    if version_result:
                        if compare_versions(version_result, TIMINGS_CHECK["version"]) == -1:
                            version = version.replace("git-", "").replace("MC: ", "")
                            embed_var.add_field(name="❌ Eski Versiyon",
                                                value=f'Kullandığın versiyon: `{version}`. Lütfen şu versiyona yükseltin: `{TIMINGS_CHECK["version"]}`.')
                    else:
                        embed_var.add_field(name="❗ Değer Hatası",
                                            value=f'Versiyonu anlayamadım, özel bir sürüm mü? `{version}`')
                if "servers" in TIMINGS_CHECK:
                    for server in TIMINGS_CHECK["servers"]:
                        if server["name"] in version:
                            embed_var.add_field(**create_field(server))
                            break
            except KeyError as key:
                logging.info("Missing: " + str(key))

            try:
                timing_cost = int(request["timingsMaster"]["system"]["timingcost"])
                if timing_cost > 300:
                    embed_var.add_field(name="❌ Timingcost",
                                        value=f"Timingcost'un {timing_cost}. CPU'n fazla yükleniyor veya yavaş. Daha iyi bir makineye geçebilirsin.")
            except KeyError as key:
                logging.info("Missing: " + str(key))

            try:
                jvm_version = request["timingsMaster"]["system"]["jvmversion"]
                if jvm_version.startswith("1.8.") or jvm_version.startswith("9.") or jvm_version.startswith("10."):
                    embed_var.add_field(name="❌ Java Sürümü",
                                        value=f"Kullandığın Java Sürümü {jvm_version}. [Java 11](https://adoptopenjdk.net/installation.html) Sürümüne geçin.")
            except KeyError as key:
                logging.info("Missing: " + str(key))

            try:
                flags = request["timingsMaster"]["system"]["flags"]
                if "-XX:+UseZGC" in flags:
                    jvm_version = request["timingsMaster"]["system"]["jvmversion"]
                    java_version = jvm_version.split(".")[0]
                    if int(java_version) < 14:
                        embed_var.add_field(name="❌ Java " + java_version,
                                            value="ZGC Sadece Java 15'de kullanılmalı")
                    if "-Xmx" in flags:
                        max_mem = 0
                        flaglist = flags.split(" ")
                        for flag in flaglist:
                            if flag.startswith("-Xmx"):
                                max_mem = flag.split("-Xmx")[1]
                                max_mem = max_mem.replace("G", "000")
                                max_mem = max_mem.replace("M", "")
                                max_mem = max_mem.replace("g", "000")
                                max_mem = max_mem.replace("m", "")
                                if int(max_mem) < 10000:
                                    embed_var.add_field(name="❌ Düşük Ram",
                                                        value="ZGC sadece fazla ram ile düzgün çalışır")
                elif "-Daikars.new.flags=true" in flags:
                    if "-XX:+PerfDisableSharedMem" not in flags:
                        embed_var.add_field(name="❌ Eski Bayrak Kullanımı",
                                            value="Bayraklarınıza `-XX:+PerfDisableSharedMem` ekleyin.")
                    if "XX:G1MixedGCCountTarget=4" not in flags:
                        embed_var.add_field(name="❌ Eski Bayrak Kullanımı",
                                            value="Bayraklarınıza `-XX:G1MixedGCCountTarget=4` ekleyin.")
                    jvm_version = request["timingsMaster"]["system"]["jvmversion"]
                    if "-XX:+UseG1GC" not in flags and jvm_version.startswith("1.8."):
                        embed_var.add_field(name="❌ Aikar's Flags",
                                            value="Aikar's Flags kullanırkan G1GC kullanmalısın.")
                    if "-Xmx" in flags:
                        max_mem = 0
                        flaglist = flags.split(" ")
                        for flag in flaglist:
                            if flag.startswith("-Xmx"):
                                max_mem = flag.split("-Xmx")[1]
                                max_mem = max_mem.replace("G", "000")
                                max_mem = max_mem.replace("M", "")
                                max_mem = max_mem.replace("g", "000")
                                max_mem = max_mem.replace("m", "")
                        if int(max_mem) < 5400:
                            embed_var.add_field(name="❌ Düşük Ram",
                                                value="Karşılayabiliyorsanız, sunucunuza 6-8GB arası ram tanımlayın.")
                        index = 0
                        max_online_players = 0
                        while index < len(request["timingsMaster"]["data"]):
                            timed_ticks = request["timingsMaster"]["data"][index]["minuteReports"][0]["ticks"][
                                "timedTicks"]
                            player_ticks = request["timingsMaster"]["data"][index]["minuteReports"][0]["ticks"][
                                "playerTicks"]
                            players = (player_ticks / timed_ticks)
                            max_online_players = max(players, max_online_players)
                            index = index + 1
                        if 1000 * max_online_players / int(max_mem) > 6 and int(max_mem) < 10000:
                            embed_var.add_field(name="❌ Düşük Ram",
                                                value="Bu kadar oyuncuyla daha fazla ram kullanmalısın.")
                        if "-Xms" in flags:
                            min_mem = 0
                            flaglist = flags.split(" ")
                            for flag in flaglist:
                                if flag.startswith("-Xms"):
                                    min_mem = flag.split("-Xms")[1]
                                    min_mem = min_mem.replace("G", "000")
                                    min_mem = min_mem.replace("M", "")
                                    min_mem = min_mem.replace("g", "000")
                                    min_mem = min_mem.replace("m", "")
                            if min_mem != max_mem:
                                embed_var.add_field(name="❌ Aikar's Flags",
                                                    value="Aikar's Flags kullanırken XMX ve XMS değerleriniz eşit olmalı.")
                elif "-Dusing.aikars.flags=mcflags.emc.gs" in flags:
                    embed_var.add_field(name="❌ Eski Bayrak Kullanımı",
                                        value="Güncel versiyon [Aikar's flags](https://aikar.co/2018/07/02/tuning-the-jvm-g1gc-garbage-collector-flags-for-minecraft/).")
                else:
                    embed_var.add_field(name="❌ Aikar's Flags",
                                        value="Aikar's Flags kullanın. [Aikar's flags](https://aikar.co/2018/07/02/tuning-the-jvm-g1gc-garbage-collector-flags-for-minecraft/).")
            except KeyError as key:
                logging.info("Missing: " + str(key))

            try:
                cpu = int(request["timingsMaster"]["system"]["cpu"])
                if cpu == 1:
                    embed_var.add_field(name="❌ Çekirdek",
                                        value=f"Sadece {cpu} işlemci çekirdeğin bulunuyor. Daha iyi bir makine almalısın.")
                if cpu == 2:
                    embed_var.add_field(name="❌ Çekirdek",
                                        value=f"Sadece {cpu} işlemci çekirdeğin bulunuyor. Daha iyi bir makine almalısın.")
            except KeyError as key:
                logging.info("Missing: " + str(key))

            try:
                handlers = request_raw["idmap"]["handlers"]
                for handler in handlers:
                    handler_name = request_raw["idmap"]["handlers"][handler][1]
                    if handler_name.startswith("Command Function - ") and handler_name.endswith(":tick"):
                        handler_name = handler_name.split("Command Function - ")[1].split(":tick")[0]
                        embed_var.add_field(name=f"❌ {handler_name}",
                                            value=f"Bu DataPack komut özelliklerini kullanıyor, lag yaptığından önerilmez.")
            except KeyError as key:
                logging.info("Missing: " + str(key))

            plugins = request["timingsMaster"]["plugins"] if "plugins" in request["timingsMaster"] else None
            server_properties = request["timingsMaster"]["config"]["server.properties"] if "server.properties" in request["timingsMaster"]["config"] else None
            bukkit = request["timingsMaster"]["config"]["bukkit"] if "bukkit" in request["timingsMaster"]["config"] else None
            spigot = request["timingsMaster"]["config"]["spigot"] if "spigot" in request["timingsMaster"]["config"] else None
            paper = request["timingsMaster"]["config"]["paper"] if "paper" in request["timingsMaster"]["config"] else None
            tuinity = request["timingsMaster"]["config"]["tuinity"] if "tuinity" in request["timingsMaster"]["config"] else None
            purpur = request["timingsMaster"]["config"]["purpur"] if "purpur" in request["timingsMaster"]["config"] else None
            if not YAML_ERROR:
                if "plugins" in TIMINGS_CHECK:
                    for server_name in TIMINGS_CHECK["plugins"]:
                        if server_name in request["timingsMaster"]["config"]:
                            for plugin in plugins:
                                for plugin_name in TIMINGS_CHECK["plugins"][server_name]:
                                    if plugin == plugin_name:
                                        stored_plugin = TIMINGS_CHECK["plugins"][server_name][plugin_name]
                                        if isinstance(stored_plugin, dict):
                                            stored_plugin["name"] = plugin_name
                                            embed_var.add_field(**create_field(stored_plugin))
                                        else:
                                            eval_field(embed_var, stored_plugin, plugin_name, plugins,
                                                       server_properties, bukkit, spigot, paper, tuinity, purpur)
                if "config" in TIMINGS_CHECK:
                    for config_name in TIMINGS_CHECK["config"]:
                        config = TIMINGS_CHECK["config"][config_name]
                        for option_name in config:
                            option = config[option_name]
                            eval_field(embed_var, option, option_name, plugins, server_properties, bukkit,
                                       spigot, paper, tuinity, purpur)
            else:
                embed_var.add_field(name="YAML dosyasını yüklerken bir hata oluştu",
                                    value=YAML_ERROR)

            try:
                for plugin in plugins:
                    authors = request["timingsMaster"]["plugins"][plugin]["authors"]
                    if authors is not None and "songoda" in request["timingsMaster"]["plugins"][plugin]["authors"].casefold():
                        if plugin == "EpicHeads":
                            embed_var.add_field(name="❌ EpicHeads",
                                                value="Songoda pluginleri özensiz kodlanmış ve lag'a neden oluyorlar. Bu eklentileri deneyebilirsin [HeadsPlus](https://spigotmc.org/resources/headsplus-»-1-8-1-16-4.40265/) ya da [HeadDatabase](https://www.spigotmc.org/resources/head-database.14280/).")
                        elif plugin == "UltimateStacker":
                            embed_var.add_field(name="❌ UltimateStacker",
                                                value="Stackleme pluginleri daha çok lag'a neden oluyor. "
                                                      "UltimateStacker eklentisini kaldır.")
                        else:
                            embed_var.add_field(name="❌ " + plugin,
                                                value="Songoda pluginleri özensiz kodlanmış ve lag'a neden oluyorlar. Başka bir eklenti bulabilirsin.")
            except KeyError as key:
                logging.info("Missing: " + str(key))

            try:
                using_tweaks = "ViewDistanceTweaks" in plugins
                if not using_tweaks:
                    worlds = request_raw["worlds"]
                    for world in worlds:
                        tvd = int(request_raw["worlds"][world]["ticking-distance"])
                        ntvd = int(request_raw["worlds"][world]["notick-viewdistance"])
                        if ntvd <= tvd and tvd >= 5:
                            if spigot["world-settings"]["default"]["view-distance"] == "default":
                                embed_var.add_field(name="❌ no-tick-view-distance",
                                                    value=f"[paper.yml](http://bit.ly/paperconf) Değerini düzenleyin. Önerilen: {tvd}. "
                                                          f"And reduce view-distance from default ({tvd}) in [spigot.yml](http://bit.ly/spiconf). Önerilen: 4.")
                            else:
                                embed_var.add_field(name="❌ no-tick-view-distance",
                                                    value=f"[paper.yml](http://bit.ly/paperconf) Değerini düzenleyin. Önerilen: {tvd}. "
                                                          f"ayrıca view-distance değerini ({tvd}) değiştirin [spigot.yml](http://bit.ly/spiconf). Önerilen: 4.")
                            break
            except KeyError as key:
                logging.info("Missing: " + str(key))

            try:
                normal_ticks = request["timingsMaster"]["data"][0]["totalTicks"]
                worst_tps = 20
                for index in range(len(request["timingsMaster"]["data"])):
                    total_ticks = request["timingsMaster"]["data"][index]["totalTicks"]
                    if total_ticks == normal_ticks:
                        end_time = request["timingsMaster"]["data"][index]["end"]
                        start_time = request["timingsMaster"]["data"][index]["start"]
                        tps = total_ticks / (end_time - start_time)
                        if tps < worst_tps:
                            worst_tps = tps
                if worst_tps < 10:
                    red = 255
                    green = int(205 * (0.1 * worst_tps))
                else:
                    red = int(205 * (-0.1 * worst_tps + 2))
                    green = 205
                color = int(red*256*256 + green*256)
                embed_var.color = color
            except KeyError as key:
                logging.info("Missing: " + str(key))

        except ValueError as value_error:
            logging.info(value_error)
            embed_var.add_field(name="❗ Değer Hatası",
                                value=value_error)

        if len(embed_var.fields) == 0:
            embed_var.add_field(name="✅ Mükemmel!",
                                value="Herhangi bir sorun bulamadım")
            await message.reply(embed=embed_var)
            return

        issue_count = len(embed_var.fields)
        field_at_index = 24
        if issue_count >= 25:
            embed_var.insert_field_at(index=24, name=f"+{issue_count - 24} daha fazla öneri",
                                      value="Yukarıdaki önerileri çözdükten sonra yeni bir Timings oluşturun ve kalan önerileri görün.")
        while len(embed_var) > 6000:
            embed_var.insert_field_at(index=field_at_index,
                                      name=f"+{issue_count - field_at_index} daha fazla öneri",
                                      value="Yukarıdaki önerileri çözdükten sonra yeni bir Timings oluşturun ve kalan önerileri görün.")
            del embed_var._fields[(field_at_index + 1):]
            field_at_index -= 1
        await message.reply(embed=embed_var)


def eval_field(embed_var, option, option_name, plugins, server_properties, bukkit, spigot, paper, tuinity, purpur):
    dict_of_vars = {"plugins": plugins, "server_properties": server_properties, "bukkit": bukkit, "spigot": spigot,
                    "paper": paper, "tuinity": tuinity, "purpur": purpur}
    try:
        for option_data in option:
            add_to_field = True
            for expression in option_data["expressions"]:
                for config_name in dict_of_vars:
                    if config_name in expression and not dict_of_vars[config_name]:
                        add_to_field = False
                        break
                if not add_to_field:
                    break
                try:
                    if not eval(expression):
                        add_to_field = False
                        break
                except ValueError as value_error:
                    add_to_field = False
                    logging.info(value_error)
                    embed_var.add_field(name="❗ Değer Hatası",
                                        value=f'`{value_error}`\nexpression:\n`{expression}`\noption:\n`{option_name}`')
                except TypeError as type_error:
                    add_to_field = False
                    logging.info(type_error)
                    embed_var.add_field(name="❗ Tür Hatası",
                                        value=f'`{type_error}`\nexpression:\n`{expression}`\noption:\n`{option_name}`')
            for config_name in dict_of_vars:
                if config_name in option_data["value"] and not dict_of_vars[config_name]:
                    add_to_field = False
                    break
            if add_to_field:
                """ f strings don't like newlines so we replace the newlines with placeholder text before we eval """
                option_data["value"] = eval('f"""' + option_data["value"].replace("\n", "\\|n\\") + '"""').replace(
                    "\\|n\\", "\n")
                embed_var.add_field(**create_field({**{"name": option_name}, **option_data}))
                break

    except KeyError as key:
        logging.info("Missing: " + str(key))


def create_field(option):
    field = {"name": option["name"],
             "value": option["value"]}
    if "prefix" in option:
        field["name"] = option["prefix"] + " " + field["name"]
    if "suffix" in option:
        field["name"] = field["name"] + option["suffix"]
    if "inline" in option:
        field["inline"] = option["inline"]
    return field


# Returns -1 if version A is older than version B
# Returns 0 if version A and B are equivalent
# Returns 1 if version A is newer than version B
def compare_versions(version_a, version_b):
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$', '', v).split(".")]

    return (normalize(version_a) > normalize(version_b)) - (normalize(version_a) < normalize(version_b))


def setup(bot):
    bot.add_cog(Timings(bot))