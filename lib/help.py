import discord
import logging
from discord.ext import commands, bridge
from lib.descriptions import CommandDescriptions
class AthenoHelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        logging.debug(type(command))
        if type(command) is not discord.ext.bridge.core.BridgeSlashCommand:
            return
        logging.debug(command)
        return '%s (-help %s)' % (command.qualified_name, command.qualified_name)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Atheno Help", color=discord.Color.og_blurple())
        for cog, commands in mapping.items():
            
            if command_signatures := [
             self.get_command_signature(c) for c in commands if isinstance(c, bridge.core.BridgeSlashCommand)
            ]:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=True)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=command.qualified_name , color=discord.Color.og_blurple())
        try: 
         embed.description = CommandDescriptions.get(command.qualified_name)
        except Exception as e:
         logging.exception(e)
         embed.description = command.description
        if alias := command.aliases:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=True)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_help_embed(self, title, description, commands): # a helper function to add commands to an embed
        embed = discord.Embed(title=title, description=description or "No help found...",color=discord.Color.og_blurple())

        if commands:
            for command in commands:
                logging.debug(type(command))
                if type(command) is not discord.ext.bridge.core.BridgeSlashCommand:
                    pass
                else:
                 embed.add_field(name=self.get_command_signature(command), value=command.help or "No help found...",inline=True)
        embed.descripton = '''Atheno listens using Discord's built-in slash (`/`) commands, or traditional prefix commands.
The prefix that Atheno uses is **`-`**.
'''
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        title = self.get_command_signature(group)
        await self.send_help_embed(title, group.help, group.commands)

    async def send_cog_help(self, cog):
        title = cog.qualified_name or "No"
        await self.send_help_embed(f'{title} Category', cog.description, cog.get_commands())