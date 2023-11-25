import discord
from discord.ext import commands, bridge
import time
import math
import random
import datetime
import re
import asyncio
from lib.utils import Utils
from lib.builder import *
from discord.ext.commands import MissingPermissions
strings = ['haha','lmao','very much a sped user',
               'cope harder','okay shrek','i dont like you',
               'ooooooooooh he got caught','i hate you','don\'t do it again',
               'heheheha','bum ahh','meep meep','stoobid','Every 60 seconds, a minute passes in Africa.']
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @bridge.bridge_command(name="warn",
                            description="Warn a user with a reason",
                            options=[ discord.Option(name="user", description="The user to warn"),
                                      discord.Option(name="reason", description="The reason for the warning")])
    async def warn(self, ctx: commands.Context, user: str, reason: str = "No reason specified."):
        await ctx.defer()
        user = user.strip()
        if (not Utils.paramcheck(Utils,user)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["user"]),ephemeral=True);return
        if not ctx.author.guild_permissions.kick_members:
            emb = MessageBuilder.error(MessageBuilder,ErrorTypes.USER_NO_PERMS,['Kick Members'])
            await ctx.respond(embed=emb, ephemeral=True)
            return

        user = discord.utils.get(ctx.guild.members, mention=user)
        if not user:
            emb = MessageBuilder.error(MessageBuilder,ErrorTypes.GENERIC,['No such user.'])
            await ctx.respond(embed=emb, ephemeral=True)
            return
        if user.bot:
            emb = MessageBuilder.error(MessageBuilder,ErrorTypes.GENERIC,['Cannot warn a bot.'])
            await ctx.respond(embed=emb, ephemeral=True)
            return

        try:
            embed = discord.Embed(title="⚠ | WARNING", description=f"You have been warned in **{ctx.guild.name}**!\nReason given: **{reason}**", color=discord.Color.green())
            embed.add_field(name="\u200b", value=f"{strings[random.randrange(len(strings))]} | At: <t:{math.floor(time.time())}:f> | By: {ctx.author} ({ctx.author.mention})", inline=True)
            await user.send(embed=embed)
            sucemb = MessageBuilder.message(MessageBuilder,MessageTypes.SUCCESS)
            sucemb.description = f"{user.mention} has been warned. Reason: {reason}"
            await ctx.respond(embed = sucemb, ephemeral=True)

        except discord.Forbidden:
            sucemb = MessageBuilder.message(MessageBuilder,MessageTypes.SUCCESS)
            sucemb.description = f"{user.mention} has been warned. Reason: {reason}"
            await ctx.respond(embed = sucemb, ephemeral=True)
            emb = MessageBuilder.error(MessageBuilder,ErrorTypes.GENERIC,['Unable to send DM to user.'])
            await ctx.respond(embed=emb, ephemeral=True)

    @bridge.bridge_command(
        name="kick",
        description="Kick a user with a reason",
        options=[
            discord.Option(name="user",description="The user to kick (username, username#discriminator, user ID, or mention)",type=3),
            discord.Option(name="reason",description="The reason for the kick",type=3)]
    )
    async def kick(self, ctx: commands.Context, user: str, reason: str = "No reason specified."):
        await ctx.defer()
        user = user.strip()
        if not ctx.author.guild_permissions.kick_members:
            emb = MessageBuilder.error(MessageBuilder,ErrorTypes.USER_NO_PERMS,['Kick Members'])
            await ctx.respond(embed=emb, ephemeral=True)
            return
        try:
            member = await commands.MemberConverter().convert(ctx, user)
        except commands.errors.BadArgument:
            member = None
        if not member:
            emb = MessageBuilder.error(MessageBuilder,ErrorTypes.GENERIC,[f"❌ | Invalid user. (User Param {user})"])
            await ctx.respond(embed=emb, ephemeral=True)
            return
        user = await self.bot.fetch_user(member.id)
        if not user:
            emb = MessageBuilder.error(MessageBuilder,ErrorTypes.GENERIC,[f"❌ | Could not find user. (ID: {member.id}, User Param {user})"])
            await ctx.respond(embed=emb, ephemeral=True)
            return
        embed = discord.Embed(title="👢 | KICKED", description=f"You have been kicked in **{ctx.guild.name}**!\nReason given: **{reason}**", color=discord.Color.dark_orange())
        embed.add_field(name="\u200b", value=f"{strings[random.randrange(len(strings))]} | At: <t:{math.floor(time.time())}:f> | By: {ctx.author} ({ctx.author.mention})", inline=True)
        await user.send(embed=embed)
        await member.kick(reason=reason)
        sucemb = MessageBuilder.message(MessageBuilder,MessageTypes.SUCCESS)
        sucemb.description = f"User {member.mention} has been kicked. Reason: {reason}"
        await ctx.respond(embed = sucemb, ephemeral=True)
    @bridge.bridge_command(
        name="ban",
        description="Ban a user with a reason",
        options=[
            discord.Option(
                name="user",
                description="The user to ban (username, username#discriminator, user ID, or mention)",
                required=True
            ),
            discord.Option(
                name="reason",
                description="The reason for the ban",
                required=False
            )
        ]
    )
    async def ban(self, ctx: commands.Context, user: str, reason: str = "No reason specified."):
        await ctx.defer()
        user = user.strip()
        if (not Utils.paramcheck(Utils,user)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["user"]),ephemeral=True);return
        if not ctx.author.guild_permissions.ban_members:
            await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.USER_NO_PERMS,vars=["Ban Members"]), ephemeral=True)
            return
    

        try:
            member = await commands.MemberConverter().convert(ctx, user)
        except commands.errors.BadArgument:
            member = None
    
        if not member:
            emb = MessageBuilder.error(MessageBuilder,ErrorTypes.GENERIC,[f"❌ | Invalid user. (User Param {user})"])
            await ctx.respond(embed=emb, ephemeral=True)
            return
            
        user = await self.bot.fetch_user(member.id)
        if not user:
            emb = MessageBuilder.error(MessageBuilder,ErrorTypes.GENERIC,[f"❌ | Could not find user. (ID: {member.id}, User Param {user})"])
            await ctx.respond(embed=emb, ephemeral=True)
            return
    
        embed = discord.Embed(
            title="🔨 | BANNED",
            description=f"You have been banned in **{ctx.guild.name}**!\nReason given: **{reason}**",
            color=discord.Color.red()
        )
        embed.add_field(name="\u200b", value=f"{strings[random.randrange(len(strings))]} | At: <t:{math.floor(time.time())}:f> | By: {ctx.author} ({ctx.author.mention})", inline=True)
        await user.send(embed=embed)
    
        await member.ban(reason=reason)
        sucemb = MessageBuilder.message(MessageBuilder,MessageTypes.SUCCESS)
        sucemb.description = f"User {member.mention} has been banned. Reason: {reason}"
        await ctx.respond(embed = sucemb, ephemeral=True)
    @bridge.bridge_command(
        name="purge",
        description="Purge a specific number of messages",
        options=[
            discord.Option(
                name="messages",
                description="The number of messages to purge (default: 10, max: 100)",
                required=False
            )
        ]
    )
    async def purge(self, ctx: commands.Context, messages: int = 10):
        await ctx.defer()
        if not ctx.author.guild_permissions.manage_messages:
            emb = MessageBuilder.error(MessageBuilder,ErrorTypes.USER_NO_PERMS,[f"Manage Messages"])
            await ctx.respond(embed=emb, ephemeral=True)
            return
        try:
            messages_num = int(messages)
        except:
            waremb = MessageBuilder.message(MessageBuilder,MessageTypes.WARNING)
            waremb.description = f"Amount of messages to clear cannot be turned into a number, or is not provided. Defaulting to 10."
            await ctx.respond(embed = waremb, ephemeral=True)
            messages_num = 10
        if messages_num < 1:
            messages_num = 1
        elif messages_num > 100:
            messages_num = 100
        deleted_messages = await ctx.channel.purge(limit=messages_num)
        sucemb = MessageBuilder.message(MessageBuilder,MessageTypes.SUCCESS)
        sucemb.description = f"Purged {len(deleted_messages)} messages!"
        await ctx.respond(embed = sucemb, ephemeral=True)
    @bridge.bridge_command(
        name="mute",
        description="Mute a user",
        options=[
            discord.Option(
                name="user",
                description="The user to mute (username, username#discriminator, user ID, or mention)",
                required=True
            ),
            discord.Option(
                name="length",
                description="The length of the mute (format: [number][s/m/h/d/w], e.g. 1s, 2m, 3h, 4d, 5w)",
                required=True
            ),
            discord.Option(
                name="reason",
                description="The reason for the mute",
                required=False
            )
        ]
    )
    async def mute(self, ctx: commands.Context, user: str, length: str, reason: str = "No reason specified."):
        await ctx.defer()
        if (not Utils.paramcheck(Utils,user, length)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["user, length"]),ephemeral=True);return
        if not ctx.author.guild_permissions.moderate_members:
            
            await ctx.respond(await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.USER_NO_PERMS,vars=["Moderate Members"]), ephemeral=True), ephemeral=True)
            return
    
        duration_units = {
            "s": 1,
            "m": 60,
            "h": 3600,
            "d": 86400,
            "w": 604800
        }
        try:
            duration = int(length[:-1]) * duration_units[length[-1]]
        except KeyError:
            await ctx.respond(f"❌ | Invalid length format. The format should be in the form of [number][s/m/h/d/w].", ephemeral=True)
            return
        if duration < 60 or duration > 2419200:
            emb = MessageBuilder.error(MessageBuilder,ErrorTypes.GENERIC,[f"The length of the mute must be between 60 seconds and 28 days."])
            await ctx.respond(embed=emb, ephemeral=True)
            return
        try:
            member = await commands.MemberConverter().convert(ctx, user)
        except commands.errors.BadArgument:
            member = None
        if not member:
            emb = MessageBuilder.error(MessageBuilder,ErrorTypes.GENERIC,[f"Invalid user. (User Param {user})"])
            await ctx.respond(embed=emb, ephemeral=True)
            return
        user_obj = await self.bot.fetch_user(member.id)
        if not user_obj:
            emb = MessageBuilder.error(MessageBuilder,ErrorTypes.GENERIC,[f"Could not find user. (ID: {member.id}, User Param {user})"])
            await ctx.respond(embed=emb, ephemeral=True)
            return
    
        embed = discord.Embed(
            title="🔇 | MUTED",
            description=f"You have been muted in **{ctx.guild.name}** for {length}. Reason given: **{reason}**",
            color=discord.Color.gold()
        )
        embed.add_field(name="\u200b", value=f"{strings[random.randrange(len(strings))]} | At: <t:{math.floor(time.time())}:f> | By: {ctx.author} ({ctx.author.mention})", inline=True)
        embed.set_footer(text="This mute will automatically expire when the time is up.")
        await user_obj.send(embed=embed)
        await member.timeout_for(datetime.timedelta(seconds=duration))
        sucemb = MessageBuilder.message(MessageBuilder,MessageTypes.SUCCESS)
        sucemb.description = f"User {member.mention} has been muted for {length}. Reason: {reason}"
        await ctx.respond(embed = sucemb, ephemeral=True)
    @bridge.bridge_command(
        name="unmute",
        description="Unmute a user.",
        options=[
            discord.Option(
                name="user",
                description="The user to unmute (username, username#discriminator, user ID, or mention)",
                required=True
            ),
            discord.Option(
                name="reason",
                description="The reason for the mute",
                required=False
            )
        ]
    )
    async def unmute(self, ctx: commands.Context, user: str, reason: str = "No reason specified."):
        await ctx.defer()
        if (not Utils.paramcheck(Utils,user)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["user"]),ephemeral=True);return
        if not ctx.author.guild_permissions.moderate_members:
            emb = MessageBuilder.error(MessageBuilder,ErrorTypes.USER_NO_PERMS,["Moderate Members"])
            await ctx.respond(embed=emb, ephemeral=True)
            return
        try:
            member = await commands.MemberConverter().convert(ctx, user)
        except commands.errors.BadArgument:
            member = None
        if not member:
            emb = MessageBuilder.error(MessageBuilder,ErrorTypes.GENERIC,[f"Invalid user. (User Param {user})"])
            await ctx.respond(embed=emb, ephemeral=True)
            return
        user_obj = await self.bot.fetch_user(member.id)
        if not user_obj:
            emb = MessageBuilder.error(MessageBuilder,ErrorTypes.GENERIC,[f"Could not find user. (ID: {member.id}, User Param {user})"])
            await ctx.respond(embed=emb, ephemeral=True)
            return
    
        embed = discord.Embed(
            title="🔉 | UNMUTED",
            description=f"You have been unmuted in **{ctx.guild.name}**! Reason given: **{reason}**",
            color=discord.Color.green()
            
        )
        embed.add_field(name="\u200b", value=f"yippee! | At: <t:{math.floor(time.time())}:f> | By: {ctx.author} ({ctx.author.mention})", inline=True)  
        await user_obj.send(embed=embed)
        await member.remove_timeout()
        sucemb = MessageBuilder.message(MessageBuilder,MessageTypes.SUCCESS)
        sucemb.description = f"User {member.mention} has been unmuted."
        await ctx.respond(embed = sucemb, ephemeral=True)
    @bridge.bridge_command(
        name="unban",
        description="Unban a user from the server",
        options=[
            discord.Option(
                name="user",
                description="The user to unban (username, username#discriminator, user ID, or mention)",
                required=True
            ),
            discord.Option(
                name="reason",
                description="The reason for the unban",
                required=False,
                default="No reason specified."
            )
        ]
    )
    async def unban(self, ctx: commands.Context, user: str, reason: str = "No reason specified."):
        await ctx.defer()
        if (not Utils.paramcheck(Utils,user)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["user"]),ephemeral=True);return
        if not ctx.author.guild_permissions.ban_members:
            emb = MessageBuilder.error(MessageBuilder,ErrorTypes.USER_NO_PERMS,["Ban Members"])
            await ctx.respond(embed=emb, ephemeral=True)
            return
        try:
            user_obj = await commands.UserConverter().convert(ctx, user)
        except commands.errors.BadArgument:
            await ctx.respond(f"❌ | Invalid user. (User Param {user})", ephemeral=True)
            return
    
        await ctx.guild.unban(user_obj, reason=reason)
        try:
            embed = discord.Embed(
                title="✅ | You've been unbanned",
                description=f"You have been unbanned in **{ctx.guild.name}**!\nReason given: **{reason}**",
                color=discord.Color.green()
            )
            await user_obj.send(embed=embed)
        except discord.errors.Forbidden:
            pass
        
        if reason:
         sucemb = MessageBuilder.message(MessageBuilder,MessageTypes.SUCCESS)
         sucemb.description = f"✅ | User {user_obj.mention} has been unbanned. Reason: {reason}"
         await ctx.respond(embed = sucemb, ephemeral=True)
        else:
         sucemb = MessageBuilder.message(MessageBuilder,MessageTypes.SUCCESS)
         sucemb.description = f"✅ | User {user_obj.mention} has been unbanned."
         await ctx.respond(embed = sucemb, ephemeral=True)
    @bridge.bridge_command(
        name="slowmode",
        description="Set the slow mode for the current channel",
        options=[
            discord.Option(
                name="time",
                description="The slow mode time (0 to 6h, e.g. 3m30s)",
                required=True
            )
        ]
    )
    async def slowmode(self, ctx: commands.Context, time: str):
        await ctx.defer()
        if (not Utils.paramcheck(Utils,time)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["time"]),ephemeral=True);return
        if not ctx.channel.permissions_for(ctx.author).manage_channels or not ctx.channel.permissions_for(self.bot).manage_channels:
                await ctx.respond("Both you and the bot must have the 'Manage Channels' permission to use this command.", ephemeral=True)
                return
        min_time = 0
        max_time = 6 * 60 * 60
        regex = re.compile(r"(\d+)(s|m|h)?")
        segments = regex.findall(time)
        seconds = sum(int(num) * {"s": 1, "m": 60, "h": 60 * 60}.get(unit, 1) for num, unit in segments)
        if seconds == min_time:
            await ctx.channel.edit(slowmode_delay=0)
        elif seconds < min_time or seconds > max_time:
            await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.GENERIC,vars=["Slowmode time must be from 0 seconds to 6 hours"]), ephemeral=True)
            return
        else:
            await ctx.channel.edit(slowmode_delay=seconds)
        if seconds == min_time:
            sucemb = MessageBuilder.message(MessageBuilder,MessageTypes.SUCCESS)
            sucemb.description = f"Successfully disabled slowmode."
            await ctx.respond(embed = sucemb, ephemeral=True)
        else:
            sucemb = MessageBuilder.message(MessageBuilder,MessageTypes.SUCCESS)
            sucemb.description = f"Successfully set the slowmode to {time}."
            await ctx.respond(embed = sucemb, ephemeral=True)
   
    @bridge.bridge_command(name="lock", description="Lock the channel")
    async def lock(self, ctx: commands.Context, reason: str = "No reason specified."):
        channel = ctx.channel
        bot = ctx.guild.me
        await ctx.defer()
        try:
            if not channel.permissions_for(ctx.author).manage_channels or not channel.permissions_for(bot).manage_channels:
                await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.GENERIC,vars=["Bot / Member may not have the Manage Channels permission."]), ephemeral=True)
                return
            await channel.set_permissions(ctx.guild.default_role, send_messages=False, send_messages_in_threads=False)
            embed = discord.Embed(title="🔒 | Channel Lockdown", description=f"{channel.mention} has been locked. \n **Reason**: \n{reason}", color=discord.Color.red())
            await ctx.respond(embed=embed, ephemeral=False)
    
        except Exception as e:
            await ctx.respond(f"You / bot may be missing {e.missing_perms} permission(s) to run this command.", ephemeral=True)
    
    @bridge.bridge_command(name="unlock", description="Unlock the channel")
    async def unlock(self, ctx: commands.Context, reason: str = "No reason specified."):
        channel = ctx.channel
        bot = ctx.guild.me
        await ctx.defer()
        try:
            if not channel.permissions_for(ctx.author).manage_channels or not channel.permissions_for(bot).manage_channels:
                await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.GENERIC,vars=["Bot / Member may not have the Manage Channels permission."]), ephemeral=True)
                return
            await channel.set_permissions(ctx.guild.default_role, send_messages=True, send_messages_in_threads=True)
            embed = discord.Embed(title="🔓 | Channel Unlock", description=f"{channel.mention} has been unlocked. \n **Reason**: \n{reason}", color=discord.Color.green())
            await ctx.respond(embed=embed, ephemeral=False)
    
        except Exception as e:
            await ctx.respond(f"You / bot may be missing {e.missing_perms} permission(s) to run this command.", ephemeral=True)
    

def setup(bot):
    bot.add_cog(Moderation(bot))