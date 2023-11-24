import discord
from discord.ext import commands, bridge
import psutil
import datetime, time
from lib.formatting import formatting
from lib.shared import Shared
start = time.time()
class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @bridge.bridge_command(description="Pulls the host computer's statistics.")
    async def cstats(self, ctx):
        system_uptime = time.time() - psutil.boot_time()
        script_uptime = time.time() - start
        cpu_percent = psutil.cpu_percent()
        ram_info = psutil.virtual_memory()

        embed = discord.Embed(color=discord.Color.green(), title='Atheno Stats')

        embed.add_field(name='System Uptime', value=f'`{formatting.timeformat(system_uptime)}`', inline=True)
        embed.add_field(name='Bot Uptime', value=f'`{formatting.timeformat(script_uptime)}`', inline=True)
        embed.add_field(name='CPU Usage', value=f'`{cpu_percent}%`', inline=True)
        ramused = ram_info.used / (1024 ** 3)
        ramtotal = ram_info.total / (1024 ** 3)
        embed.add_field(name='RAM Usage', value=f'`{ramused:.2f}GB / {ramtotal:.2f}GB ` (`{formatting.percent(ramused,ramtotal):.2f}%`)', inline=True)
        embed.add_field(name="Environment",value=Shared.buffer['env'])
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Stats(bot))
