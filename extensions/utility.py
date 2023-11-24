import discord
from discord.ext import bridge, commands
from lib.shared import Shared
import subprocess
import logging
import aiohttp
import urllib
import math,asyncio,requests,json
from lib.emojify import emojify
from lib.builder import *
from lib.utils import Utils
class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @bridge.bridge_command(description="Nukes a channel, removing all messages and pings.")
    async def nuke(self, ctx, channel: discord.TextChannel = None):
        if (not Utils.paramcheck(Utils,channel)):
         channel = ctx.channel
        if not (ctx.author.guild_permissions.manage_channels and ctx.author.guild_permissions.manage_messages):
            
            embed = MessageBuilder.error(self=MessageBuilder,type=ErrorTypes.USER_NO_PERMS,vars=["`Manage Channels` and `Manage Messages`"])
            await ctx.respond(embed=embed)
            return
            
        await ctx.respond('Nuking channel...')
        clone = await channel.clone()
        pos = channel.position
        await channel.delete()
        await clone.edit(position=pos)
        await clone.send(f"Nuked by `{ctx.author}`.")
    @bridge.bridge_command(description="[DANGEROUS] [RESTRICTED: DEVMODE+BOTOWNER]")
    async def restart(self, ctx):
        if Shared.buffer['env'] != 'dev':
            await ctx.respond("The restart command can only be used in development mode.")
            return
        if ctx.author.id != 1129545353717366884:
            await ctx.respond("You are not authorized to use this command.")
            return
        await ctx.respond("Restarting the bot...")
        subprocess.Popen("run_dev.bat")
        await self.bot.close()
    @bridge.bridge_command(description="Grabs the member count")
    async def membercount(self, ctx):
        total = ctx.guild.member_count
        bots = sum(member.bot for member in ctx.guild.members)
        humans = total - bots
        embed = discord.Embed(
            color=discord.Color.og_blurple(),
            title=None,
            description=f"**Member Count**: {total}\n(bots: {bots}, people: {humans})"
        )
        await ctx.respond(embed=embed)
    @bridge.bridge_command(description="Tells you information about the server you are currently in.")
    async def serverinfo(self, ctx):
        guild = ctx.guild
        boosters = sum(1 for member in guild.members if any("booster" in role.name.lower() or role.color == discord.Color(0xf47fff) for role in member.roles))
        roles = sorted(guild.roles, key=lambda r: len(r.members), reverse=True)[:6][1:]
        denseroles = "\n".join(f"{role.name}: {len(role.members)} members" for role in roles)
        owner = self.bot.get_user(int(ctx.guild.owner.id))
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title=f"About {guild.name}",
            description=f"Age: <t:{int(guild.created_at.timestamp())}:R> (created on <t:{int(guild.created_at.timestamp())}:f>)\n"
                        f"ID: {guild.id}\n"
                        f"Member Count: {guild.member_count} (humans: {len([member for member in guild.members if not member.bot])}, bots: {len([member for member in guild.members if member.bot])})\n"
                        f"Server Owner: {owner} ({owner.mention})\n"
                        f"Channels:\n"
                        f"- Text: {len(guild.text_channels)} channels\n"
                        f"- Voice: {len(guild.voice_channels)} channels\n"
                        f"- AFK Channel: {guild.afk_channel}\n"
                        f"Boosters (if applicable): {boosters}\n"
                        f"Boosting Level: {guild.premium_tier}\n"
                        f"Most Dense Roles:\n```\n{denseroles}\n```\n"
                        f"Invites Disabled? {emojify(guild.invites_disabled)}\n"
                        f"Features: {','.join(guild.features)}\n"
                        
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.banner:
            embed.set_image(url=guild.banner.url)
        await ctx.respond(embed=embed)
    @bridge.bridge_command(description="Give a shortened URL, see it's destination.")
    async def whereamigoing(self, ctx, url: str):
        if (not Utils.paramcheck(Utils,url)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["url"]),ephemeral=True);return
        await ctx.defer()
        logging.debug(f'Where am I going?')
        logging.debug(f'Input URL: {url}')

        try:
            async with aiohttp.ClientSession() as session:
             async with session.get(url, allow_redirects=True) as response:
                finurl = str(response.url)
            if url == finurl:
                await ctx.respond(embed=discord.Embed(color=discord.Color.og_blurple(),description=f"**No URL change.**"));return
            await ctx.respond(embed=discord.Embed(color=discord.Color.green(),description=f"`{url}` **->** `{finurl}`"))
            logging.debug(f'Destination URL: {finurl}')
        except Exception as e:
            logging.error(f'Error during URL follow: {e}')
            await ctx.respond(f'Error during URL follow.\n**What went Wrong**:\n```\n{e}\n```')
    @bridge.bridge_command(description="Cleans tracking URL paramaters out of your url.")
    async def urlclean(self, ctx, url):
        if (not Utils.paramcheck(Utils,url)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["url"]),ephemeral=True);return
        logging.debug(f'Input URL: {url}')

        try:
            clean_url = self.remove_tracking_params(url)
            if url == clean_url:
                await ctx.respond(embed=discord.Embed(color=discord.Color.og_blurple(),description=f"**Nothing to remove.**"));return
            await ctx.respond(embed=discord.Embed(color=discord.Color.green(),description=f"`{url}` \n**->** `{clean_url}`"))
        except Exception as e:
            logging.error(f'Error during URL cleaning: {e}')
            await ctx.respond(f'Error during URL follow.\n**What went Wrong**:\n```\n{e}\n```')

    def remove_tracking_params(self, url):

        parsed_url = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed_url.query)
        tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content','ref','crid','keywords','qid','sprefix','utm_ref','ref_','ua','useragent','ip','ipaddr','ipaddress','os','system']
        clean_params = {k: v for k, v in params.items() if k.lower() not in tracking_params}
        clean_query = urllib.parse.urlencode(clean_params, doseq=True)
        clean_url = urllib.parse.urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path,
                                             parsed_url.params, clean_query, parsed_url.fragment))

        return clean_url
    @bridge.bridge_command(name="pfp", description="Get the avatar of yourself, or others.")
    async def pfp(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        try:
          embed = discord.Embed(title=f"{user.name}'s avatar", color=discord.Color.og_blurple())
          embed.set_image(url=user.avatar.url)

          await ctx.respond(embed=embed)
        except:
          embed = discord.Embed(title=f"{user.name} does not have a profile picture.", color=discord.Color.red())
          await ctx.respond(embed=embed)
    @commands.slash_command(name="math", description="uh, make me do some of your homework!")
    async def calculate(self, ctx, expression: str = None, help: bool = False):
     if (not Utils.paramcheck(Utils,expression)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["expression"]),ephemeral=True);return
     help_guide = """
## `/math` Help Guide: \n 
To do operations like rounding, square root, etc, you can do something like `math.sqrt(144)`. This can be done for any operation set by
the C standard (or in Python), for simple operations, you can do `9+69/4*176`, if you need to use parentheses, you can do that by: `(99*0.33)+57`.
 
## Cheat Sheet:\n

* multiplication: `*`
* addition: `+`
* subtraction: `-`
* division: `/`
* to the power of: `math.pow` / `math.powf` / `math.powl` 
(powf for floats (6.142), powl for longs)
* square root: `math.sqrt`
* sine: `math.sin`
* cosine: `math.cosin`
* floor: `math.floor`
* ceil: `math.ceiling`
     """
     if help or expression == None:
         await ctx.respond(embed=discord.Embed(title="", description=f"{help_guide}", color=discord.Color.blue()))
         return
 
     try:
         result = eval(expression, {"__builtins__": None, "math": math})
         await ctx.respond(f"The result of `{expression}` is: {result}")
     except ZeroDivisionError:
      await ctx.respond(f"EMERGENCY: DIVIDING BY ZERO!!! Activating Divide by 0 machine...")
      await asyncio.sleep(1.11)
      await ctx.respond(f"The Divide by 0 machine gave you this: \n The result of `{expression}` is: <https://www.youtube.com/watch?v=oHg5SJYRHA0> because you are a dumbass that tried dividing by 0.")
     except Exception as e:
         await ctx.respond(f"An error occurred while evaluating the expression: {e}\n\nIf you need help, make the `help` parameter `True`", ephemeral=True)
    
    @commands.slash_command()
    async def weather(self, ctx, location: str):
        if (not Utils.paramcheck(Utils,location)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["location"]),ephemeral=True);return
        api_key = "ed2c35261325435d8d3180351232206"
        url = f"https://api.weatherapi.com/v1/forecast.json?key={api_key}&q={location}&days=4"
        response = requests.get(url)

        if response.status_code == 200:
            data = json.loads(response.text)
            location_name = data["location"]["name"]
            current_temp_c = data["current"]["temp_c"]
            current_temp_f = data["current"]["temp_f"]
            current_condition = data["current"]["condition"]["text"]
            forecast_days = data["forecast"]["forecastday"]

            embed = discord.Embed(title="Weather Information", description=f"Weather in {location_name}\nWeather provided by www.weatherapi.com", color=discord.Color.blue())
            embed.add_field(name="Current Temperature", value=f"{current_temp_c}°C / {current_temp_f}°F", inline=True)
            embed.add_field(name="Current Condition", value=current_condition, inline=True)
            embed.add_field(name="    ", value="    ", inline=True)
            for day in forecast_days[:3]:
                date = day["date"]
                forecast = day["day"]["condition"]["text"]
                temp_c = day["day"]["avgtemp_c"]
                temp_f = day["day"]["avgtemp_f"]
                high_temp_c = day["day"]["maxtemp_c"]
                high_temp_f = day["day"]["maxtemp_f"]
                low_temp_c = day["day"]["mintemp_c"]
                low_temp_f = day["day"]["mintemp_f"]
                embed.add_field(name=f"Forecast for {date}", value=f"{forecast}\n{temp_c}°C / {temp_f}°F\nHigh: {high_temp_c}°C / {high_temp_f}°F\nLow: {low_temp_c}°C / {low_temp_f}°F", inline=True)
            
            await ctx.respond(embed=embed)
        else: await ctx.respond("Failed to retrieve weather information.")
        
   
def setup(bot):
    bot.add_cog(Utility(bot))
