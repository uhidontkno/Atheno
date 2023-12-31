import asyncio
from lib.builder import *
import async_timeout
import wavelink
from discord import ClientException
from discord.ext import commands, bridge
from wavelink import (LavalinkException, LoadTrackError, SoundCloudTrack,
                      YouTubeMusicTrack, YouTubePlaylist, YouTubeTrack)
from wavelink.ext import spotify
from wavelink.ext.spotify import SpotifyTrack
from ._classes import Provider
from .checks import voice_channel_player, voice_connected
from .errors import MustBeSameChannel
from .paginator import Paginator
from .player import DisPlayer


class Music(commands.Cog):
    """Music commands"""

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.bot.loop.create_task(self.start_nodes())

    def get_nodes(self):
        return sorted(wavelink.NodePool._nodes.values(), key=lambda n: len(n.players))

    async def play_track(self, ctx: commands.Context, query: str, provider=None):
        await ctx.defer()
        player: DisPlayer = ctx.voice_client

        if ctx.author.voice.channel.id != player.channel.id:
            em = MessageBuilder.error(MessageBuilder, type=ErrorTypes.GENERIC,vars=["You must be in the same voice channel as the bot in order to use this command."])
            await ctx.respond(embed=em)

        track_providers = {
            "yt": YouTubeTrack,
            "ytpl": YouTubePlaylist,
            "ytmusic": YouTubeMusicTrack,
            "soundcloud": SoundCloudTrack,
            "spotify": SpotifyTrack,
        }

        query = query.strip("<>")
        msg = await ctx.send(f"Searching for `{query}` :mag_right:")

        track_provider = provider if provider else player.track_provider

        if track_provider == "yt" and "playlist" in query:
            provider = "ytpl"

        provider: Provider = (
            track_providers.get(provider)
            if provider
            else track_providers.get(player.track_provider)
        )

        nodes = self.get_nodes()
        tracks = list()

        for node in nodes:
            try:
                with async_timeout.timeout(30):
                    tracks = await provider.search(query, node=node)
                    break
            except asyncio.TimeoutError:
                self.bot.dispatch("dismusic_node_fail", node)
                wavelink.NodePool._nodes.pop(node.identifier)
                continue
            except (LavalinkException, LoadTrackError):
                continue

        if not tracks:
            return await msg.edit("No song/track found with given query.")

        if isinstance(tracks, YouTubePlaylist):
            tracks = tracks.tracks
            for track in tracks:
                await player.queue.put(track)

            await ctx.respond(content=f"Added `{len(tracks)}` songs to queue. ")
        else:
            track = tracks[0]

            await ctx.respond(content=f"Added `{track.title}` to queue. ")
            await player.queue.put(track)

        if not player.is_playing():
            await player.do_next()

    async def start_nodes(self):
        await self.bot.wait_until_ready()
        spotify_credential = getattr(
            self.bot, "spotify_credentials", {"client_id": "", "client_secret": ""}
        )

        for config in self.bot.lavalink_nodes:
            try:
                node: wavelink.Node = await wavelink.NodePool.create_node(
                    bot=self.bot,
                    **config,
                    spotify_client=spotify.SpotifyClient(**spotify_credential),
                )
                print(f"[dismusic] INFO - Created node: {node.identifier}")
            except Exception:
                print(
                    f"[dismusic] ERROR - Failed to create node {config['host']}:{config['port']}"
                )

    @bridge.bridge_command(aliases=["con","c"])
    @voice_connected()
    async def connect(self, ctx: commands.Context):
        """Connect the player"""
        if ctx.voice_client:
            return

        try:
            player: DisPlayer = await ctx.author.voice.channel.connect(cls=DisPlayer)
            self.bot.dispatch("dismusic_player_connect", player)
        except (asyncio.TimeoutError, ClientException):
            return ctx.respond(embed=MessageBuilder.error(type=ErrorTypes.GENERIC,vars=["Failed to connect to VC."]))
            

        player.bound_channel = ctx.channel
        player.bot = self.bot

        await ctx.respond(f"Connected to **`{ctx.author.voice.channel}`**")
    
    async def forceconnect(self,ctx):
        if ctx.voice_client:
            return

        try:
            player: DisPlayer = await ctx.author.voice.channel.connect(cls=DisPlayer)
            self.bot.dispatch("dismusic_player_connect", player)
        except (asyncio.TimeoutError, ClientException):
            return ctx.send(embed=MessageBuilder.error(type=ErrorTypes.GENERIC,vars=["Failed to connect to VC."]))
            

        player.bound_channel = ctx.channel
        player.bot = self.bot


    @bridge.bridge_command(aliases=["p","ply"], invoke_without_command=True)
    async def play(self, ctx: commands.Context, service = "ytmusic", query:str = None):
        """Play or add song to queue (Defaults to YouTube)"""
        if ctx.author.voice is None:
            await ctx.respond(embed=MessageBuilder.error(type=ErrorTypes.GENERIC,vars=[f"You are not connected to VC."]))
        if ctx.voice_client is None:
            await ctx.send(embed=MessageBuilder.message(self=MessageBuilder,type=MessageTypes.INFO,vars=[f"Bot is not connected to any VC. Automatically trying to connect."]))
            await self.forceconnect(ctx)
        if query == None:
            await ctx.respond("You must specify a query.");return
        try:
         await self.play_track(ctx, query, service)
        except Exception as e:
            await ctx.respond(embed=MessageBuilder.error(type=ErrorTypes.GENERIC,vars=[f"Failed to search for {query} on {service}.\n```\n{e}\n```"]))
    '''
    @play.command(aliases=["yt"])
    @voice_connected()
    async def youtube(self, ctx: commands.Context, *, query: str):
        """Play a YouTube track"""
        await ctx.invoke(self.connect)
        await self.play_track(ctx, query, "yt")

    @play.command(aliases=["ytmusic"])
    @voice_connected()
    async def youtubemusic(self, ctx: commands.Context, *, query: str):
        """Play a YouTubeMusic track"""
        await ctx.invoke(self.connect)
        await self.play_track(ctx, query, "ytmusic")

    @play.command(aliases=["sc"])
    @voice_connected()
    async def soundcloud(self, ctx: commands.Context, *, query: str):
        """Play a SoundCloud track"""
        await ctx.invoke(self.connect)
        await self.play_track(ctx, query, "soundcloud")

    @play.command(aliases=["sp"])
    @voice_connected()
    async def spotify(self, ctx: commands.Context, *, query: str):
        """play a spotify track"""
        await ctx.invoke(self.connect)
        await self.play_track(ctx, query, "spotify")
'''
    @bridge.bridge_command(aliases=["vol"])
    @voice_channel_player()
    async def volume(self, ctx: commands.Context, vol: int, forced=False):
        """Set volume"""
        player: DisPlayer = ctx.voice_client

        if vol < 0:
            return await ctx.respond("Volume can't be less than 0")

        if vol > 100 and not forced:
            return await ctx.respond("Volume can't greater than 100")

        await player.set_volume(vol)
        await ctx.respond(f"Volume set to {vol} :loud_sound:")

    @bridge.bridge_command(aliases=["disconnect", "dc"])
    @voice_channel_player()
    async def stop(self, ctx: commands.Context):
        """Stop the player"""
        player: DisPlayer = ctx.voice_client

        await player.destroy()
        await ctx.respond("Stopped the player :stop_button: ")
        self.bot.dispatch("dismusic_player_stop", player)

    @bridge.bridge_command(aliases=["pau"])
    @voice_channel_player()
    async def pause(self, ctx: commands.Context):
        """Pause the player"""
        player: DisPlayer = ctx.voice_client

        if player.is_playing():
            if player.is_paused():
                return await ctx.respond("Player is already paused.")

            await player.set_pause(pause=True)
            self.bot.dispatch("dismusic_player_pause", player)
            return await ctx.respond("Paused :pause_button: ")

        await ctx.respond("Player is not playing anything.")

    @bridge.bridge_command()
    @voice_channel_player()
    async def resume(self, ctx: commands.Context):
        """Resume the player"""
        player: DisPlayer = ctx.voice_client

        if player.is_playing():
            if not player.is_paused():
                return await ctx.respond("Player is already playing.")

            await player.set_pause(pause=False)
            self.bot.dispatch("dismusic_player_resume", player)
            return await ctx.respond("Resumed :musical_note: ")

        await ctx.respond("Player is not playing anything.")

    @bridge.bridge_command()
    @voice_channel_player()
    async def skip(self, ctx: commands.Context):
        """Skip to next song in the queue."""
        player: DisPlayer = ctx.voice_client

        if player.loop == "CURRENT":
            player.loop = "NONE"

        await player.stop()

        self.bot.dispatch("dismusic_track_skip", player)
        await ctx.respond("Skipped :track_next:")

    @bridge.bridge_command()
    @voice_channel_player()
    async def seek(self, ctx: commands.Context, seconds: int):
        """Seek the player backward or forward"""
        player: DisPlayer = ctx.voice_client

        if player.is_playing():
            old_position = player.position
            position = old_position + seconds
            if position > player.source.length:
                return await ctx.respond("Can't seek past the end of the track.")

            if position < 0:
                position = 0

            await player.seek(position * 1000)
            self.bot.dispatch("dismusic_player_seek", player, old_position, position)
            return await ctx.respond(f"Seeked {seconds} seconds :fast_forward: ")

        await ctx.respond("Player is not playing anything.")

    @bridge.bridge_command()
    @voice_channel_player()
    async def loop(self, ctx: commands.Context, loop_type: str = None):
        """Set loop to `NONE`, `CURRENT` or `PLAYLIST`"""
        player: DisPlayer = ctx.voice_client

        result = await player.set_loop(loop_type)
        await ctx.respond(f"Loop has been set to {result} :repeat: ")

    @bridge.bridge_command(aliases=["q"])
    @voice_channel_player()
    async def queue(self, ctx: commands.Context):
        """Player queue"""
        player: DisPlayer = ctx.voice_client

        if len(player.queue._queue) < 1:
            return await ctx.respond("Nothing is in the queue.")

        paginator = Paginator(ctx, player)
        await paginator.start()

    @bridge.bridge_command(aliases=["np"])
    @voice_channel_player()
    async def nowplaying(self, ctx: commands.Context):
        """Currently playing song information"""
        player: DisPlayer = ctx.voice_client
        await player.invoke_player(ctx)
