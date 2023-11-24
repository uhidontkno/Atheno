from discord.ext import bridge, commands
import discord
import logging
import sys
from lib.builder import *
from lib.shared import *;ATHENO = Shared.buffer['ATHENOPATH']
import json
from lib.utils import *
from pathlib import Path
from lib.builder import MessageBuilder
from lib.builder import ErrorTypes as ErrorType
import asyncio
class Ticketing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    class TicketReasonModal(discord.ui.Modal):
     def __init__(self, bot,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.add_item(discord.ui.InputText(label="Reason for Ticket", style=discord.InputTextStyle.long,min_length=16,max_length=768))

     async def callback(self, interaction: discord.Interaction):
        reason = self.children[0].value
        server_id = interaction.guild.id
        if Path(f'{ATHENO}/extensions/data/ticketing_configuration.json').is_file():
          with Path(f'{ATHENO}/extensions/data/ticketing_configuration.json').open("r", encoding="utf-8") as config_file:
              tcconfig = json.load(config_file)
        else:
            embed = MessageBuilder.error(
                self=MessageBuilder,
                type=ErrorType.GENERIC,
                vars=["Cannot Create Ticket:\nUnable to read the Ticketing Configuration file."]
            )
            await interaction.response.send_message(embed=embed)
        if str(server_id) in tcconfig['servers']:
            staffrolei = tcconfig['servers'][str(server_id)]["roleid"]
            staffrole = interaction.guild.get_role(staffrolei)
            cat = interaction.guild.get_channel(tcconfig['servers'][str(server_id)]["catid"])
            if cat and isinstance(cat, discord.CategoryChannel):
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.user: discord.PermissionOverwrite(read_messages=True),
                    staffrole: discord.PermissionOverwrite(read_messages=True),
                }
                channel = await cat.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites)
                await channel.send(content=f"<@{interaction.user.id}> | <@&{staffrolei}>")
                embed = discord.Embed(title="New Ticket",description=f"\n**Reason for Ticket**:\n```\n{reason}\n```",color=discord.Color.og_blurple())
                embed.set_footer(text="Powered by Atheno")
                await channel.send(embed=embed,view=Ticketing.InsideTicketView(self.bot))
                
                view = discord.ui.View()
                button = discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="Go To Channel",
                    url=f'https://discord.com/channels/{interaction.guild.id}/{channel.id}'
                )
                view.add_item(button)
                await interaction.response.send_message("Your ticket has been created.", view=view,ephemeral=True)
            else:
                embed = MessageBuilder.error(
                    self=MessageBuilder,
                    type=ErrorType.GENERIC,
                    vars=["Cannot Create Ticket:\nTicket category not found."]
                )
                await interaction.response.send_message(embed=embed)
        else:
            embed = MessageBuilder.error(
                self=MessageBuilder,
                type=ErrorType.GENERIC,
                vars=["Cannot Create Ticket:\nServer ID does not exist in dict tcconfig['servers'].\nFriendly Error: Cannot Create Ticket, server has not been set up correctly."]
            )
            await interaction.response.send_message(embed=embed)

    class TicketView(discord.ui.View):
     def __init__(self, bot):
         super().__init__(timeout=None) # timeout of the view must be set to None
         self.bot = bot
        
     @discord.ui.button(label="Make a Ticket", style=discord.ButtonStyle.blurple, emoji="📩", custom_id="maketicket")
     async def maketicket(self, button, interaction: discord.Interaction):
      server_id = str(interaction.guild.id)
      if (TicketUtils.isticketban(str(interaction.guild.id),interaction.user.id)):
          embed = MessageBuilder.error(
              self=MessageBuilder,
              type=ErrorType.USER_NO_PERMS,
              vars=["`Create Tickets`"]
          )
          await interaction.response.send_message(embed=embed,ephemeral=True);return
      await interaction.response.send_modal(Ticketing.TicketReasonModal(title="Create Ticket",bot=self.bot))
      
    class InsideTicketView(discord.ui.View):
        def __init__(self,bot):
            super().__init__(timeout=None)
            self.bot = bot
        @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒", custom_id="closeticket")
        async def closeticket(self, button, interaction):
            async for message in interaction.channel.history(limit=1):
                  firstmsg = message
                  break
            await interaction.response.send_message('Closing ticket...',ephemeral=True)
            membername = interaction.channel.name.replace('ticket-','')
            member = None
            from discord.utils import get
            async for m in interaction.guild.fetch_members(limit=None, after=None):
                logging.debug(m.name)
                logging.debug(membername[:6])
                logging.debug(member)
                logging.debug(membername)
                if (membername[:6] in m.name):
                    member = m
            
            if (member != None): 
             await member.send(embed=discord.Embed(color=discord.Color.embed_background('dark'),title="Ticket Closed",description=f"**Your ticket in {interaction.guild.name} got closed.**\n**Closed By**: `{interaction.user}`"))
            await interaction.channel.delete()
        @discord.ui.button(label="Silent Close",emoji="🔇",style=discord.ButtonStyle.gray,custom_id="silentclose")
        async def silentclose(self,button,interaction):
            await interaction.channel.delete()
        @discord.ui.button(label="Ticket Ban", style=discord.ButtonStyle.gray, emoji="🚫", custom_id="ticketban")
        async def ticketban(self, button, interaction):
         if interaction.user.guild_permissions.moderate_members:
              membername = interaction.channel.name.replace('ticket-','')
              member = None
              from discord.utils import get
              async for m in interaction.guild.fetch_members(limit=None, after=None):
                lookfor = m.name.replace('.','')
                lookfor = m.name.replace('_','')
                logging.debug(m.name)
                logging.debug(lookfor[:6])
                logging.debug(member)
                logging.debug(membername)
                if (membername[:6] in lookfor):
                    member = m
            
              if (member != None): 
               server_id = str(interaction.guild.id)
               user_id = str(interaction.user.id)
               with open('extensions/data/ticket_banned.json', 'r') as file:
                   data = json.load(file)
               if server_id not in data['servers']:
                   data['servers'][server_id] = []
               data['servers'][server_id].append(member.id)
               with open('extensions/data/ticket_banned.json', 'w') as file:
                   json.dump(data, file, indent=2)
               await interaction.response.send_message("User has been ticket banned. Closing ticket in 2 seconds...", ephemeral=True)
               await member.send(embed=discord.Embed(color=discord.Color.embed_background('dark'),title="Ticket Closed",description=f"**Your ticket in {interaction.guild.name} got closed.**\n**Closed By**: `{interaction.user}`"))
               await asyncio.sleep(2.1)
               await interaction.channel.delete()
              else:
                  await interaction.response.send_message(MessageBuilder.error(self=MessageBuilder,type=ErrorTypes.GENERIC,vars=["Member already left the server or cannot be found."]), ephemeral=True)
             
         else:
             await interaction.response.send_message(MessageBuilder.error(self=MessageBuilder,type=ErrorTypes.USER_NO_PERMS,vars=["`Moderate Members`"]), ephemeral=True)
    @commands.Cog.listener()
    async def on_ready(self):
     self.bot.add_view(self.TicketView(self.bot))
     self.bot.add_view(self.InsideTicketView(self.bot))
    @bridge.bridge_command(description="Set up the ticketing system.")
    async def setuptickets(self, ctx, channel_name: str, prompt: str, category_name: str, staff_role: discord.Role):
        if (not Utils.paramcheck(Utils,channel_name,prompt,category_name,staff_role)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["channel_name, prompt, category_name, staff_role"]),ephemeral=True);return
        await ctx.defer()
        with open(Path("extensions/data/ticketing_configuration.json"), "r") as config:
            if(ctx.guild.id in json.load(config)['servers']):
                MessageBuilder.error(self=MessageBuilder,type=ErrorTypes.GENERIC,vars=[""])
        guild = ctx.guild
        if not (ctx.author.guild_permissions.manage_channels and ctx.author.guild_permissions.manage_guild):
            embed = MessageBuilder.error(self=MessageBuilder,type=ErrorTypes.USER_NO_PERMS,vars=["`Manage Channels` and `Manage Server`"])
            await ctx.respond(embed=embed)
            return
        channel = discord.utils.get(guild.channels, name=channel_name.lower())
        if not channel:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            channel = await guild.create_text_channel(channel_name.lower(), overwrites=overwrites)
        category = discord.utils.get(guild.categories, name=category_name.lower())
        if not category:
            category = await guild.create_category(category_name.lower())
        description = f"{prompt}\n\n"
        embed = discord.Embed(color=discord.Color.og_blurple(), title=f"{guild.name} | Tickets", description=description)
        if guild.icon:
            embed.set_thumbnail(guild.icon.url)
        else:
            # f'logo-{Shared.buffer["env"]}.png'
            if Shared.buffer["env"] == "prod": url = "https://cdn.discordapp.com/attachments/1167491501643796594/1176577233368928329/logo-prod.png"
            else: url = "https://cdn.discordapp.com/attachments/1167491501643796594/1176577249462468658/logo-dev.png"
            embed.set_thumbnail(url=url)
        embed.set_footer(text="Powered by Atheno")
        await channel.send(embed=embed,view=self.TicketView(self.bot))
        ticketdat = {
            "cid": channel.id,
            "prompt": prompt,
            "catid": category.id,
            "roleid": staff_role.id
        }
        configp = Path("extensions/data/ticketing_configuration.json")
        if configp.exists():
            with open(configp, "r") as config:
                tfiledat = json.load(config)
        else:
            tiledat = {"servers": {}}
        srvid = str(ctx.guild.id)
        tfiledat["servers"][srvid] = ticketdat
        with open(configp, "w") as config:
            json.dump(tfiledat, config, indent=2)
        await ctx.respond(f"Ticket setup complete.")
    @bridge.bridge_command(
    name="ticketban",
    description="Ban a user from creating tickets.")
    async def ticketban(self, ctx, user: discord.User):
     if (not Utils.paramcheck(Utils,user)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["user"]),ephemeral=True);return
     if ctx.author.guild_permissions.moderate_members:
             server_id = str(ctx.guild.id)
             with open('extensions/data/ticket_banned.json', 'r') as file:
                 data = json.load(file)
 
             if server_id not in data['servers']:
                 data['servers'][server_id] = []
 
             data['servers'][server_id].append(user.id)
 
             with open('extensions/data/ticket_banned.json', 'w') as file:
                 json.dump(data, file, indent=2)
 
             await ctx.respond("User has been ticket banned.", ephemeral=True)
        
     else:
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.USER_NO_PERMS,
                                                vars=["`Moderate Members`"]), ephemeral=True)
    @bridge.bridge_command(
        name="ticketadd",
        description="Add someone to a ticket channel."
    )
    async def ticketadd(self, ctx, user: discord.User):
        if (not Utils.paramcheck(Utils,user)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["user"]),ephemeral=True);return
        if ctx.author.guild_permissions.manage_channels:
            channel_name = ctx.channel.name.lower()
            if channel_name.startswith("ticket"):
                overwrite = ctx.channel.overwrites_for(user)
                overwrite.read_messages = True
                await ctx.channel.set_permissions(user, overwrite=overwrite)

                await ctx.respond(f"Added user {user} to the current ticket.")
            else:
                await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.GENERIC,
                                                       vars=["This command can only be used in ticket channels."]),
                                  ephemeral=True)
        else:
            await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.USER_NO_PERMS,
                                                   vars=["`Manage Channels`"]), ephemeral=True)
    @bridge.bridge_command(
        name="ticketunban",
        description="Unban a user from creating tickets."
    )
    async def ticketunban(self, ctx, user: discord.User):
        if (not Utils.paramcheck(Utils,user)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["user"]),ephemeral=True);return
        if ctx.author.guild_permissions.moderate_members:
            server_id = str(ctx.guild.id)
            with open('extensions/data/ticket_banned.json', 'r') as file:
                data = json.load(file)
            if server_id in data['servers']:
                if user.id in data['servers'][server_id]:
                    data['servers'][server_id].remove(user.id)
                    with open('extensions/data/ticket_banned.json', 'w') as file:
                        json.dump(data, file, indent=2)

                    await ctx.respond(f"User {user.mention} has been unbanned from creating tickets.", ephemeral=True)
                else:
                    await ctx.respond("User is not ticket banned.", ephemeral=True)
            else:
                await ctx.respond("No ticket bans recorded for this server.", ephemeral=True)
        else:
            await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.USER_NO_PERMS,
                                                   vars=["`Moderate Members`"]), ephemeral=True)
    @bridge.bridge_command(
        name="ticketremove",
        description="Remove a user from a ticket"
    )
    async def ticketremove(self, ctx, user: discord.User):
        if (not Utils.paramcheck(Utils,user)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["user"]),ephemeral=True);return
        if ctx.author.guild_permissions.manage_channels:
            channel_name = ctx.channel.name.lower()
            if channel_name.startswith("ticket"):
                overwrite = ctx.channel.overwrites_for(user)
                overwrite.read_messages = False
                await ctx.channel.set_permissions(user, overwrite=overwrite)
                await ctx.respond(f"Removed user {user} from the current ticket.")
            else:
                await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.GENERIC,
                                                       vars=["This command can only be used in ticket channels."]),
                                  ephemeral=True)
        else:
            await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.USER_NO_PERMS,
                                                   vars=["`Manage Channels`"]), ephemeral=True)
    @bridge.bridge_command(description="Prompt the user to close their ticket.")
    async def alert(self,ctx,user: discord.Member):
        if (not Utils.paramcheck(Utils,user)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["user"]),ephemeral=True);return
        channel_name = ctx.channel.name.lower()
        if channel_name.startswith("ticket-"):
            await ctx.respond(embed=discord.Embed(color=discord.Color.green(),title="Ticket Finished",description=f"`{ctx.author}` is finished assisting you and wants you to close your ticket now.\n**Close your ticket by checking the pinned or scrolling up to the first message.**",
                                                  ),content=f"{user.mention}")
        else:
            await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.GENERIC,
                                                   vars=["This command can only be used in ticket channels."]),
                              ephemeral=True)

def setup(bot):
    bot.add_cog(Ticketing(bot))
