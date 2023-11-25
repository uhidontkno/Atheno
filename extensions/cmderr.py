
import discord
from discord.ext import commands
from lib.builder import *
import logging
class CMDErrorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        logging.exception(error)
        if isinstance(error, commands.MissingRequiredArgument):
            param_name = error.param.name
            expected_type = error.param.annotation.__name__ if error.param.annotation else "any"
            em = MessageBuilder.error(MessageBuilder, ErrorTypes.INVALID_PARAMS, ["placeholder"])
            em.description = f"Required argument `{param_name}` (expecting `{expected_type}`) missing."
            await ctx.respond(embed=em)
        else:
            em = MessageBuilder.error(MessageBuilder, ErrorTypes.GENERIC, [f"{error}"])
            await ctx.respond(embed=em)
            

def setup(bot):
    bot.add_cog(CMDErrorCog(bot))
