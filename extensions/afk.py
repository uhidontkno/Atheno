from discord.ext import bridge, commands
import discord
import logging
import asyncio

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afk_users = {}

    @bridge.bridge_command(description="Set yourself as AFK, tracks mentions.")
    async def afk(self, ctx, message: str = " "):
        await ctx.defer()
        user_id = ctx.author.id
        sanitized = message.replace("@everyone",'@| some mf tried to ping everyone 😂😂')
        sanitized = message.replace("@here",'@| some mf tried to ping here 😂😂')
        sanitized = message.replace("@",'_@_')
        await ctx.respond(f'{ctx.author.mention} is now AFK. Reason: {sanitized}')
        self.afk_users[user_id] = message
        logging.debug(self.afk_users)
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id in self.afk_users:
            del self.afk_users[message.author.id]
            await message.channel.send(f'Welcome back {message.author}! I have removed your AFK.', delete_after=10)

        mentions = message.mentions
        for mention in mentions:
            if mention.id in self.afk_users:
                rawmsg = self.afk_users[mention.id]
                sanitized = rawmsg.replace("@everyone",'@| some mf tried to ping everyone 😂😂')
                sanitized = rawmsg.replace("@here",'@| some mf tried to ping here 😂😂')
                sanitized = rawmsg.replace("@",'_@_')
                await message.channel.send(f'{self.bot.get_user(mention.id)} is currently AFK. \nMessage: `{sanitized}`', delete_after=20)

def setup(bot):
    bot.add_cog(AFK(bot))
