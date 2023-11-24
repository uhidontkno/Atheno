import json
import discord
from discord.ext import commands, bridge
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter
import logging
import numpy as np
import math
from lib.cooldown import Cooldown
import requests
from lib.builder import *
import random
import aiohttp
import os
import aiohttp
import json
import time
from discord import File
import asyncio
import sys
import datetime
from lib.ai import AI
from datetime import datetime
from lib.utils import Utils
class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.cooldown = Cooldown(15) # Set cooldown to 15 seconds per user by default

    @bridge.bridge_command(name="crunch-pfp", description="Make your profile picture even funnier.")
    async def crunch_pfp(self, ctx, user: discord.Member = None, crunch: int = 1):
        await ctx.defer()
        cooldown = self.cooldown.get_cooldown(ctx.author.id)
        if cooldown > 0:
            c_minutes = math.floor(cooldown // 60)
            c_seconds = math.floor(cooldown % 60)
            await ctx.respond(f"❌ | You're on a cooldown. Try again in {c_minutes} minutes and {c_seconds} seconds.", ephemeral=True) # respond with error message
            return
        
        if user is None:
            user = ctx.author
        if crunch is None:
            crunch = 1
        if crunch > 50:
            await ctx.respond("⚠ | Crunchiness amount must be lower or equal to 50. Setting it to 50.")
            crunch = 50
        if crunch < -10:
            await ctx.respond("⚠ | Crunchiness amount must be higher or equal to -10. Setting it to -10.")
            crunch = -10
        pfp = user.avatar.with_size(512)
        pfp_bytes = await pfp.read()
        image = Image.open(BytesIO(pfp_bytes))
        image = image.convert("RGB")
        width, height = image.size
        new_width = math.floor(222)
        new_size = (new_width, math.floor(222/2))
        image = image.resize(new_size)
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(math.floor(6.0 + (crunch*2)))
        for i in range(math.floor(6 * ((crunch/2)+1))):
            image = image.filter(ImageFilter.SHARPEN)
        red = Image.new("RGBA", image.size, (255, 0, 0, 255))
        red = red.convert("RGB")
        blended = Image.blend(image, red, 0.32)
        image = blended
        image = image.resize((512 * 2, 512),Image.Resampling.NEAREST)
        with BytesIO() as image_binary:
            image.save(image_binary, 'JPEG', quality=math.floor(16 - (crunch/2)))
            image_binary.seek(0)
            file = discord.File(image_binary, filename='crunch_pfp.jpg')
            await ctx.respond(file=file)

    @bridge.bridge_command(name="insult", description="Let me ruin your day.")
    async def insult(self, ctx):
        await ctx.defer()
        # Check if user is on cooldown
        cooldown = self.cooldown.get_cooldown(ctx.author.id)
        if cooldown > 0:
            c_minutes = math.floor(cooldown // 60)
            c_seconds = math.floor(cooldown % 60)
            await ctx.respond(f"❌ | You're on a cooldown. Try again in {c_minutes} minutes and {c_seconds} seconds.", ephemeral=True) # respond with error message
            return
        self.cooldown.set_cooldown(ctx.author.id)
        response = requests.get("https://insult.mattbas.org/api/insult.txt")
        insult = response.text.strip()
        await ctx.respond(f"💩 | {insult}", ephemeral=False)
    @bridge.bridge_command(name="joke", description="Get a random joke!")
    async def joke(self, ctx):
            await ctx.defer()
            # Check if user is on cooldown
            cooldown = self.cooldown.get_cooldown(ctx.author.id)
            if cooldown > 0:
                c_minutes = math.floor(cooldown // 60)
                c_seconds = math.floor(cooldown % 60)
                await ctx.respond(f"❌ | You're on a cooldown. Try again in {c_minutes} minutes and {c_seconds} seconds.", ephemeral=True) # respond with error message 
                return
    
            self.cooldown.set_cooldown(ctx.author.id)
    
            response = requests.get("https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,racist,sexist&format=txt")
            joke = response.text.strip()
    
            
            await ctx.respond(f"😂 | {joke}", ephemeral=False)
    @bridge.bridge_command(name="cat", description="Get a random cat image or video!")
    async def cat(self, ctx):
        await ctx.defer()
                # Check if user is on cooldown
        cooldown = self.cooldown.get_cooldown(ctx.author.id)
        if cooldown > 0:
            c_minutes = math.floor(cooldown // 60)
            c_seconds = math.floor(cooldown % 60)
            await ctx.respond(f"❌ | You're on a cooldown. Try again in {c_minutes} minutes and {c_seconds} seconds.", ephemeral=True) # respond with error message
            return
        response = requests.get("https://api.thecatapi.com/v1/images/search")
        json_data = json.loads(response.text)
        image_url = json_data[0]['url']

        embed = discord.Embed(title="🐱 Meow!", color=discord.Color.blue())
        embed.set_image(url=image_url)
        await ctx.respond(embed=embed)

    @bridge.bridge_command(name="dog", description="Get a random dog image or video!")
    async def dog(self, ctx):
        await ctx.defer()
                # Check if user is on cooldown
        cooldown = self.cooldown.get_cooldown(ctx.author.id)
        if cooldown > 0:
            c_minutes = math.floor(cooldown // 60)
            c_seconds = math.floor(cooldown % 60)
            await ctx.respond(f"❌ | You're on a cooldown. Try again in {c_minutes} minutes and {c_seconds} seconds.", ephemeral=True) # respond with error message
            return
        response = requests.get("https://api.thedogapi.com/v1/images/search")
        json_data = json.loads(response.text)
        image_url = json_data[0]['url']

        embed = discord.Embed(title="🐶 Woof!", color=discord.Color.blue())
        embed.set_image(url=image_url)
        await ctx.respond(embed=embed)
    @bridge.bridge_command(name="gayrate", description="how gay are you fr fr")
    async def gayrate(self, ctx):
        await ctx.defer()
        cooldown = self.cooldown.get_cooldown(ctx.author.id)
        if cooldown > 0:
            c_minutes = math.floor(cooldown // 60)
            c_seconds = math.floor(cooldown % 60)
            await ctx.respond(f"❌ | You're on a cooldown. Try again in {c_minutes} minutes and {c_seconds} seconds.", ephemeral=True) # respond with error message
            return
        precents = [-1,0,1,2,5,10,12,17,24,37,50,69,99,100,420,666,999,42069,69420]
        await ctx.respond(embed=discord.Embed(title="Gay Rate fr",color=discord.Color.dark_blue(),description=f"you are {random.choice(precents)}% gay fr 😳"), ephemeral=False)
    @bridge.bridge_command(name="rizzrate", description="how much rizz do you have 😈")
    async def rizzrate(self, ctx):
        await ctx.defer()
        cooldown = self.cooldown.get_cooldown(ctx.author.id)
        if cooldown > 0:
            c_minutes = math.floor(cooldown // 60)
            c_seconds = math.floor(cooldown % 60)
            await ctx.respond(f"❌ | You're on a cooldown. Try again in {c_minutes} minutes and {c_seconds} seconds.", ephemeral=True) # respond with error message
            return
        precents = [-10,-3,-2,-1,0,0,1,2,5,10,12,17,24,37,50,69,99,100,420,666,999,42069,69420]
        await ctx.respond(embed=discord.Embed(title="Rizz Rate fr",color=discord.Color.dark_blue(),description=f"you have {random.choice(precents)}% rizz 😈😮‍💨"), ephemeral=False)
    @bridge.bridge_command(name="racistrate", description="how racist are you? 💀")
    async def racistrate(self, ctx):
        await ctx.defer()
        cooldown = self.cooldown.get_cooldown(ctx.author.id)
        if cooldown > 0:
            c_minutes = math.floor(cooldown // 60)
            c_seconds = math.floor(cooldown % 60)
            await ctx.respond(f"❌ | You're on a cooldown. Try again in {c_minutes} minutes and {c_seconds} seconds.", ephemeral=True) # respond with error message
            return
        precents = [-1,0,1,2,5,10,12,17,24,37,50,69,99,100,420,666,999,42069,69420]
        await ctx.respond(embed=discord.Embed(title="Racist Rate fr",color=discord.Color.dark_blue(),description=f"you are {random.choice(precents)}% racist 💀"), ephemeral=False)
    @bridge.bridge_command(name="annoyrate", description="how annoying are you?")
    async def annoyrate(self, ctx):
        
        precents = [-420,-69,-35,-14,-2,-1,0,1,8,16,32,64,99,100,169,251,269,420,9999]
        await ctx.respond(embed=discord.Embed(title="Annoy Rate fr",color=discord.Color.dark_blue(),description=f"you are {random.choice(precents)}% annoying 💀"), ephemeral=False)
    @bridge.bridge_command(name="girls-rate", description="how many bitches do you have?")
    async def girlsrate(self, ctx):
       
        precents = ["",sys.maxsize * -1,"fatass","fatass","can't use tinder 💀","can't use tinder 💀","can't use tinder 💀",-1000,-877,-767,-444,-6767,-999,-696,-444,-333,-69,0,0,0,0,0,0,0,0,1,1,1,1,1,1,2,2,2,2,4,8,7,6,19,44,358,462,694,42069,69420]
        await ctx.respond(embed=discord.Embed(title="Bitches Rate fr",color=discord.Color.dark_blue(),description=f"you have {random.choice(precents)} bitches"), ephemeral=False)
    @bridge.bridge_command(name="menrate", description="ayo what the")
    async def menrate(self, ctx):
        await ctx.respond(embed=discord.Embed(title="Men Rate fr",color=discord.Color.dark_blue(),description=f"ay yo what the fuc- no. i'm not doing this"), ephemeral=False)
   
    @bridge.bridge_command(
        name="rps",
        description="Play a game of rock paper scissors",
        options=[
            discord.Option(
                name="option",
                type=3,
                required=True,
                choices=[
                    discord.OptionChoice(value="1", name="Rock"),
                    discord.OptionChoice(value="2", name="Paper"),
                    discord.OptionChoice(value="3", name="Scissors")
                ],
            )
        ],
    )
    async def rps(self, ctx: commands.Context, option: str):
        await ctx.defer()
        if (not Utils.paramcheck(Utils,option)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["option"]),ephemeral=True);return
        option = int(option)
        await ctx.respond(content=f"Starting a game of rock paper scissors.",ephemeral=True)
        desc = ["Rock...","Rock... Paper...","Rock... Paper... Scissors...","Rock... Paper... Scissors... shoe?"]
        option_lang = ["Rock :rock:","Paper :scroll:","Scissors :scissors:"]
        rpsmsg = await ctx.send(embed=discord.Embed(title="Rock Paper Scissors",description="Starting game...",color=discord.Color.green()),content=f"{ctx.author.mention}")
        user_choice = option
        for i in range(4):
         bot_choice = random.randrange(1,3)
         await asyncio.sleep(0.5)
         await rpsmsg.edit(embed=discord.Embed(title="Rock Paper Scissors: Bot is picking...",description=f"{desc[i]} \n{option_lang[(bot_choice + 4 % 3) - 1]}?",color=discord.Color.green()),content=f"{ctx.author.mention}")
        if user_choice == bot_choice:
            result = "It's a tie!"
        elif (user_choice == 1 and bot_choice == 3) or (user_choice == 2 and bot_choice == 1) or (user_choice == 3 and bot_choice == 2):
            result = "You win!"
        else:
            result = "You lose!"

        await asyncio.sleep(2)
        await rpsmsg.edit(embed=discord.Embed(title="Rock Paper Scissors ",description=f"## {result} \n You chose {option_lang[option - 1]}\nI chose {option_lang[bot_choice - 1]}.\n\nDon't get mad over RNG!",color=discord.Color.og_blurple()),content=f"{ctx.author.mention}")
    @bridge.bridge_command(name="howmanycrimes", description="Are the police after you?")
    async def crimery(self, ctx, guilty: bool = True): 
        await ctx.defer()
        emcolor = None
        emtitle = None
        emdescription = None
        crimes = [random.randrange(0,200),random.randrange(0,4),random.randrange(0,17),random.randrange(0,473)]
        if (crimes[0] == 0 and crimes[1] == 0 and crimes[2] == 0 and crimes[3] == 0):
            emcolor = discord.Color.green()
            emtitle = "Woah! Nobody is after you!"
            emfooter = "Congratulations!"
        else:
            emcolor = discord.Color.red()
            emtitle = "Uh Oh."
            emfooter = "Don't worry, there is a **1/694.20 (0.00144%)** chance of being a good boy!"
        emdescription = f'''
Are you a criminal 🤔? Let's find this out!
**You committed**
* Arson {crimes[0]} times
* 🔪 {crimes[1]} times
* Car theft {crimes[2]} times
* Tax Evasion {crimes[3]} times

{emfooter} In total you committed {crimes[0] + crimes[1] + crimes[2] + crimes[3]} crimes.
        '''
        await ctx.respond(embed=discord.Embed(color=emcolor, title=emtitle, description=emdescription))
    @bridge.bridge_command(name="howmuchbrokeass", description="how much broke ass are you?")
    async def brokerate(self, ctx, user: discord.User = None):
        await ctx.defer()
        if not user: user = ctx.author 
        start = -0.5
        end = 1.5
        step = 0.05

        values = []
        current = start
        while current < end:
         values.append(current)
         current += step

        brokepercent = random.choice(values)
        if user != ctx.author:
            directed = f"is {user} a"
            display = f"{user.mention} is"
            md = f"{user.mention} has"
            usrm = f"their"
        else:
            directed = f"are you a"
            display = f"you are"
            md = f"you have"
            usrm = "your"
        await ctx.respond(embed=discord.Embed(title=f"How much {directed} broke ass?",color=discord.Color.dark_blue(),description=f"{display} **{'{:.2f}'.format(brokepercent * -363)}%** broke\n{md} **${'{:.2f}'.format(69420 * brokepercent)}** in {usrm} bank account fr"), ephemeral=False)
    @bridge.bridge_command(name="ben", description="Talking Ben")
    async def ben(self, ctx, question: str):
        await ctx.defer()
        responses = ["Ho Ho Ho!","No.","Yes!","Ugh."]
        file = None
        response = random.choice(responses)
        if "love god" in question.lower():
            response = "Ho Ho Ho... No."
        fp = os.path.join(os.getcwd(), "categories", "assets", "backrooms.mp4")
        backrooms = File(fp)
        fp = os.path.join(os.getcwd(), "categories", "assets", "lean.mp4")
        lean = File(fp)
        if "make lean" in question.lower() :
            file = lean
            response = "..."
        
        elif "backrooms" in question.lower():
            file = backrooms
            response = "..."
        await ctx.respond(content="Starting conversation...",ephemeral=True)
        cem = discord.Embed(color=discord.Color.greyple(), description=f"### Started by {ctx.author.mention}")
        benmsg = await ctx.send(content='''
> **Call started with Talking Ben** 
        ''',embed=cem)
        await asyncio.sleep(2)
        await benmsg.edit(content='''
> **Call started with Talking Ben** 
> Talking Ben: Ben?
        ''',embed=cem)
        await  asyncio.sleep(2)
        await benmsg.edit(content=f'''
> **Call started with Talking Ben** 
> Talking Ben: Ben?
> You: {question}
        ''',embed=cem)
        await asyncio.sleep(2)
        await benmsg.edit(content=f'''
> **Call started with Talking Ben** 
> Talking Ben: Ben?
> You: {question}
> Talking Ben: {response}
> Talking Ben: \*hangs up\*
        ''',embed=cem)
        if file:
         await ctx.respond(file=file)
    @bridge.bridge_command(name="ask-gpt", description="Ask a question to GPT-3.")
    async def chatgpt(self, ctx, *question: str):
        await ctx.defer()
        if (not Utils.paramcheck(Utils,question)):
         await ctx.respond(MessageBuilder.error(self=MessageBuilder, type=ErrorTypes.INVALID_PARAMS,vars=["question"]),ephemeral=True);return
        if (len(question) > 1250): 
            await ctx.respond(embed=discord.Embed(color=discord.Color.red(),title="Error",description=f"GPT request error:\nMessage: Prompt too long, shorten it to be under 1250 bytes."))
            return
        question = f'''{question}\n----------
Discord User Info:
Member: {ctx.author}
User ID: {ctx.author.id}
Proper Mention: <@{ctx.author.id}>
Unix Epoch: {time.time()}
----------
Current Server Info:
Name: {ctx.guild.name}
ID: {ctx.guild.id}'''
        await ctx.defer()
        try:
            response = await AI.query(AI,question)
            await ctx.respond(embed=discord.Embed(description=response,color=discord.Color.og_blurple()))
        except Exception as e:
            logging.exception(e)
            await ctx.respond(embed=MessageBuilder.error(MessageBuilder,ErrorTypes.GENERIC,vars=[f"A Python Exception has occurred, and AI cannot respond.\n\nUnexpected {e=}, {type(e)=}"]))
       
    @bridge.bridge_command(name="apod", description="Get the Astronomy Picture of the Day")
    async def apod(self, ctx: commands.Context, date: str = ""):
        await ctx.defer()
        try:
            if date:
                try:
                    specific_date = datetime.strptime(date, "%m/%d/%Y").date()
                    specific_date_str = specific_date.strftime("%Y-%m-%d")
                except ValueError:
                    await ctx.respond("Invalid date format. Please use 'MM/DD/YYYY'.", ephemeral=True)
                    return
            else:
                specific_date_str = ""
    
            async with aiohttp.ClientSession() as session:
                url = f"https://api.nasa.gov/planetary/apod?api_key=GBbZhUoGsWm5uFvLSDJMccaXImK2uRHdsskTZbwb&date={specific_date_str}"
                async with session.get(url) as response:
                    if response.status == 200:
                        if response.content_type == "application/json":
                            data = await response.json()
                            image_url = data["url"]
                            explanation = data["explanation"]
    
                            embed = discord.Embed(title="Astronomy Picture of the Day", description=explanation, color=discord.Color.blue())
                            embed.set_image(url=image_url)
    
                            await ctx.respond(embed=embed, ephemeral=False)
                        else:
                            await ctx.respond("Failed to fetch Astronomy Picture of the Day: Unexpected response format.", ephemeral=True)
                    else:
                        await ctx.respond("Failed to fetch Astronomy Picture of the Day.", ephemeral=True)
        except aiohttp.ContentTypeError as e:
            await ctx.respond(f"Failed to fetch Astronomy Picture of the Day: Unexpected response format. \nDebug: {str(e)}", ephemeral=True)
        except Exception as e:
            await ctx.respond(f"An error occurred: {str(e)}", ephemeral=True)

def setup(client):
    client.add_cog(Fun(client))