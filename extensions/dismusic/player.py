import asyncio
import os

import async_timeout
import discord
from discord.ext import commands
from wavelink import Player
import aiohttp
from bs4 import BeautifulSoup
from ._classes import Loop
from .errors import InvalidLoopMode, NotEnoughSong, NothingIsPlaying
from lib.builder import *

class DisPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = asyncio.Queue()
        self.loop = Loop.NONE  # CURRENT, PLAYLIST
        self.bound_channel = None
        self.track_provider = "yt"

    async def destroy(self) -> None:
        self.queue = None

        await super().stop()
        await super().disconnect()

    async def do_next(self) -> None:
        if self.is_playing():
            return

        timeout = int(os.getenv("DISMUSIC_TIMEOUT", 300))

        try:
            with async_timeout.timeout(timeout):
                track = await self.queue.get()
        except asyncio.TimeoutError:
            if not self.is_playing():
                await self.destroy()

            return

        self._source = track
        await self.play(track)
        self.client.dispatch("dismusic_track_start", self, track)
        await self.invoke_player()

    async def set_loop(self, loop_type: str) -> None:
        if not self.is_playing():
            raise NothingIsPlaying("Player is not playing any track. Can't loop")

        if not loop_type:
            if Loop.TYPES.index(self.loop) >= 2:
                loop_type = "NONE"
            else:
                loop_type = Loop.TYPES[Loop.TYPES.index(self.loop) + 1]

            if loop_type == "PLAYLIST" and len(self.queue._queue) < 1:
                loop_type = "NONE"

        if loop_type.upper() == "PLAYLIST" and len(self.queue._queue) < 1:
            raise NotEnoughSong(
                "There must be 2 songs in the queue in order to use the PLAYLIST loop"
            )

        if loop_type.upper() not in Loop.TYPES:
            raise InvalidLoopMode("Loop type must be `NONE`, `CURRENT` or `PLAYLIST`.")

        self.loop = loop_type.upper()

        return self.loop

    async def getytavatar(self, youtube_handle):
        url = f"https://apttutorials.com/yt-test.php?loc=&n1=&usern={youtube_handle}&ran=150"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as response:
                    if response.status == 200 and response.content_type == 'text/html':
                        html_content = await response.text()

                        # Parse HTML using BeautifulSoup
                        soup = BeautifulSoup(html_content, 'html.parser')

                        # Find the first <img> element and get its 'src' attribute
                        img_element = soup.find('img')
                        if img_element and 'src' in img_element.attrs:
                            return img_element['src']
        except aiohttp.ClientError:
            pass  # Handle timeout or other client errors here

        # Return default avatar if there's an error or no image source found
        return self.client.user.display_avatar.url
    async def invoke_player(self, ctx: commands.Context = None) -> None:
        track = self.source

        if not track:
            raise NothingIsPlaying("Player is not playing anything.")

        embed = discord.Embed(
            title=track.title, url=track.uri, color=discord.Color.dark_blue()
        )
        embed.set_author(
            name=track.author,
            url=track.uri
        )
        try:
            embed.set_thumbnail(url=track.thumb)
        except AttributeError:
            pass
        embed.add_field(
            name="Length",
            value=f"{int(track.length // 60)}:{int(track.length % 60)}",
        )
        embed.add_field(name="Looping", value=self.loop)
        embed.add_field(name="Volume", value=self.volume)

        next_song = ""

        if self.loop == "CURRENT":
            next_song = self.source.title
        else:
            if len(self.queue._queue) > 0:
                next_song = self.queue._queue[0].title

        if next_song:
            embed.add_field(name="Next Song", value=next_song, inline=False)

        if not ctx:
            return await self.bound_channel.send(embed=embed)

        await ctx.send(embed=embed)
