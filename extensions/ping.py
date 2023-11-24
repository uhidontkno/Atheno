import discord
from discord.ext import bridge, commands
import time
import websockets
import math
async def ping_ws():
    start_time = time.time()
    async with websockets.connect("wss://gateway.discord.gg") as ws:
        end_time = time.time()
    latency = (end_time - start_time) * 1000
    return latency

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(name="ping", description="Get the bot's latency.")
    async def ping(self, ctx):
        start_time = time.time()
        msg = await ctx.defer()
        end_time = time.time()

        ping = (end_time - start_time) * 1000
        ws_ping = self.bot.latency * 1000
        api_ping = await ping_ws()

        
        await ctx.respond(
            content=f"🏓 **PONG**!\n"
                    f"- Bot Ping: `{ping:.2f}ms` (`{ping * 1000:.3f}µ`)\n"
                    f"- Websocket Ping: `{ws_ping:.2f}`ms (`{ws_ping * 1000:.3f}µ`)\n"
                    f"- API Ping: `{api_ping:.2f}`ms (`{api_ping * 1000:.3f}µ`)"
        )

def setup(bot):
    bot.add_cog(Ping(bot))
