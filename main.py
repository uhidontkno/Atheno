import discord
from discord.ext import commands
import os, sys, logging
from pathlib import Path
from lib.help import AthenoHelpCommand
from importlib import import_module
from http.server import SimpleHTTPRequestHandler, HTTPServer
import time, math
import threading
from lib.shared import Shared;Shared.buffer['ATHENOPATH'] = os.getcwd()
def exception_hook(exc_type, exc_value, exc_traceback):
    logging.exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
# Set the exception hook
sys.excepthook = exception_hook
env_mode = 'prod'
def logs(silent,loglevel):
    log_format = "[ATHENO %(levelname)s] (%(asctime)s): %(message)s"

    if not silent:
     logging.basicConfig(level=loglevel, format=log_format)
    if silent:
        print(f"ATHENO: Disabling logs.")

def gettoken(env):
    token_file = f'environ/{env}'
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            return f.read().strip()
    else:
        logging.critical(f"'{token_file}' not found. Make sure the file exists.")
        sys.exit(1)

def exts(bot):
 for filename in os.listdir("extensions"):
    if filename.endswith(".py"):
        bot.load_extension(f"extensions.{filename[:-3]}")
        logging.info(f"Loaded extension {filename[:-3]}!")
env = 'prod'

silent = False
loglevel = logging.WARNING;
for arg in sys.argv:
    if arg == "-dev":
        env = 'dev'
        env_mode = env
    
    if arg.startswith('-level='):
        level = arg.split('=')[1].lower()
        if level in ('fatal', 'critical', 'major'):
            loglevel = logging.CRITICAL
        elif level in ('error','err'):
            loglevel = logging.ERROR
        elif level in ('warn', 'warning'):
            loglevel = logging.WARNING
        elif level in ('info', 'information'):
            loglevel = logging.INFO
        elif level in ('debug','verbose'):
            loglevel = logging.DEBUG
    elif arg == '-silent':
        silent = True
    elif arg in ("-?","-help","--help"):
        print(f'''ATHENO HELP:
main.py [args]
-? or --help returns this text
-level=[level] controls the logging level 
(critical (aliases:fatal,major), error (aliases: err),warn (aliases: warning),info (aliases: information),debug (alises:verbose))  
-silent logs to file (eg. logs/{env}-{math.floor(time.time())}.out) and disables console output

''');sys.exit(0);

env_mode = env
logs(silent,loglevel)
from discord.ext import bridge
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = bridge.Bot(command_prefix="-", intents=intents, help_command = AthenoHelpCommand())
bot.lavalink_nodes = [
    {"host": "n1.ll.darrennathanael.com", "port": 2269, "password": "glasshost1984"},
    {"host": "lava.horizxon.tech", "port": 80, "password": "horizxon.tech"},
    {"host": "lavalink1.albinhakanson.se", "port": 1141, "password": "albinhakanson.se"}
]

# --> DISMUSIC LOADER CODE:
from extensions.dismusic._version import __version__, version_info
from extensions.dismusic.events import MusicEvents
from extensions.dismusic.music import Music
bot.add_cog(Music(bot))
bot.add_cog(MusicEvents(bot))
# <--

token = gettoken(env)
exts(bot)
Shared.buffer['env'] = env_mode

bot.run(token)
