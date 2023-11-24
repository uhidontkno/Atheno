import discord
from discord.ext import commands, tasks
import json
import random
import asyncio

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    @commands.Cog.listener()
    async def on_ready(self):
        with open('extensions/status/statuses.json', 'r',errors='replace') as file:
            statuses = json.load(file)
        while True:
         type, msg = random.choice(statuses['statuses'])
         await self.bot.change_presence(activity=discord.Activity(name=msg, type=getattr(discord.ActivityType, type.lower())))
         await asyncio.sleep(30)

def setup(bot):
    bot.add_cog(StatusCog(bot))
