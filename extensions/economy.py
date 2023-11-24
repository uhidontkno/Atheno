from typing import Union
import discord
from discord.ext import commands, bridge
from discord.ui import View, Select, Button
import os
import json
import asyncio
import json
import random
import math
import time
async def load_data(sid):
    try:
        with open(f"extensions/economy/servers/{sid}.json", "r") as file:
            return json.load(file)
    except FileNotFoundError as e:
        print(e)
        return None

async def save_data(sid, data):
    with open(f"extensions/economy/servers/{sid}.json", "w") as file:
        json.dump(data, file)

async def add_money(sid, uid, amount):
    sid = int(sid)
    uid = int(uid)
    amount = int(amount)
    server_data = await load_data(sid)
    if server_data is None or server_data[str(uid)] is None:
        print(f"Failed to get data. {server_data}")
        return 1 
    
    server_data[str(uid)]["balance"][0] += amount
    await save_data(sid, server_data)
    return 0

async def get_money(sid, uid):
    sid = int(sid)
    uid = int(uid)
    server_data = await load_data(sid)
    if server_data is None or server_data[str(uid)] is None:
        print(f"Failed to get data. {server_data}")
        return 1 
    return server_data[str(uid)]["balance"]
async def remove_money(sid, uid, amount):
    sid = int(sid)
    uid = int(uid)
    amount = int(amount)
    server_data = await load_data(sid)
    if server_data is None or server_data[str(uid)] is None:
        print(f"Failed to get data. {server_data}")
        return 1  
    
    server_data[str(uid)]["balance"][0] -= amount
    await save_data(sid, server_data)
    return 0

async def add_item(sid, uid, item_name):
    sid = int(sid)
    uid = int(uid)
    server_data = await load_data(sid)
    if server_data is None or server_data[str(uid)] is None:
        print(f"Failed to get data. {server_data}")
        return 1  
    server_data[str(uid)]["inventory"].append(item_name)
    await save_data(sid, server_data)
    return 0
async def remove_item(sid, uid, item_name):
    sid = int(sid)
    uid = int(uid)
    server_data = await load_data(sid)
    if server_data is None or server_data[str(uid)] is None:
        print(f"Failed to get data. {server_data}")
        return 1  
    inventory = server_data[str(uid)]["inventory"]
    if item_name in inventory:
        inventory.remove(item_name)
    
    await save_data(sid, server_data)
    return 0
async def move_bank_to_wallet(sid, uid, amount):
    sid = int(sid)
    uid = int(uid)
    amount = int(amount)
    server_data = await load_data(sid)
    if server_data is None or str(uid) not in server_data:
        return 1  
    
    balance = server_data[str(uid)]["balance"]
    if balance[1] < amount:
        return 1  
    
    balance[1] -= amount
    balance[0] += amount
    await save_data(sid, server_data)
    return 0
async def move_wallet_to_bank(sid, uid, amount):
    sid = int(sid)
    uid = int(uid)
    amount = int(amount)
    server_data = await load_data(sid)
    if server_data is None or str(uid) not in server_data:
        return 1  
    
    balance = server_data[str(uid)]["balance"]
    if balance[0] < amount:
        return 1  
    
    balance[0] -= amount
    balance[1] += amount
    await save_data(sid, server_data)
    return 0

def check_json(server_id, user_id):
    server_file = f"{server_id}.json"
    server_path = os.path.join("extensions/economy/servers", server_file)

    if os.path.isfile(server_path):
        with open(server_path, "r") as file:
            server_data = json.load(file)
            if user_id in server_data:
                return True
    else:
        return False

    return False

async def sync_save(current_server_id, user_id):
    user_id = str(user_id)
    current_server_data = await load_data(current_server_id)
    print(current_server_data)
    if user_id in current_server_data:
        user_save_data = current_server_data[user_id]
        print(user_save_data)
    else:
        return  
    for filename in os.listdir("servers"):
        if filename.endswith(".json") and filename != str(current_server_id) + ".json":
            server_id = filename.split(".")[0]
            server_data = await load_data(server_id)
            print(server_data)

            if user_id in server_data:
                server_data[user_id] = user_save_data
                await save_data(server_id, server_data)
    return True




with open('extensions/economy/items.json','r') as dat:
    items = json.load(dat)
WORK_COOLDOWN = 30
last_work_command = {}
last_rob_command = {}
last_beg_command = {}
last_fish_command = {}
last_hunt_command = {}
class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    @bridge.bridge_command(name="bal", description="Check your balance.")
    async def bal(self,ctx):
     await ctx.defer()
     guild_id = str(ctx.guild.id)
     user_id = str(ctx.author.id)
     guild_file_path = f'extensions/economy/servers/{guild_id}.json'
     if not os.path.exists(guild_file_path):
         guild_data = {
             "name": ctx.guild.name,
             user_id: {
                 "balance": [0, 0],
                 "inventory": []
             }
         }
         with open(guild_file_path, 'w') as guild_file:
             json.dump(guild_data, guild_file)
         gdc = await ctx.send(embed=discord.Embed(description="Creating server data...",color=discord.Color.og_blurple()))
         await asyncio.sleep(0.3)
         await gdc.delete()
     with open(guild_file_path, 'r') as guild_file:
         guild_data = json.load(guild_file)
     if user_id not in guild_data:
         guild_data[user_id] = {
             "balance": [0, 0],
             "inventory": []
         }
         with open(guild_file_path, 'w') as guild_file:
             json.dump(guild_data, guild_file)
         udm = await ctx.send(embed=discord.Embed(description="Creating user data...",color=discord.Color.og_blurple()))
         await asyncio.sleep(0.3)
         await udm.delete()

     user_data = guild_data[user_id]
     balance = user_data["balance"]
     inventory = user_data["inventory"]
     embed = discord.Embed(title=f"{ctx.author}'s inventory",
                           color=discord.Color.og_blurple())
     embed.add_field(name="Wallet",value=f"${balance[0]}",inline=True)
     embed.add_field(name="Bank",value=f"${balance[1]}",inline=True)
     embed.add_field(name="Items:",value=f"```\n{', '.join(inventory)}```",inline=False)
     await ctx.respond(embed=embed,ephemeral=True)
     return 0
    @bridge.bridge_command(description="Work at Phantom's Bistro")
    async def work(self, ctx):
        await ctx.defer()
        user_id = str(ctx.author.id)
        if not check_json(str(ctx.guild.id), str(ctx.author.id)):
            await ctx.respond(f"❌ | You don't exist on {ctx.guild.name}. Please generate your data by doing `-bal` or `/bal`")
            return
        if user_id in last_work_command:
             current_time = time.time()
             last_execution_time = last_work_command[user_id]
        
             if current_time - last_execution_time < WORK_COOLDOWN:
                 cooldown_remaining = WORK_COOLDOWN - (current_time - last_execution_time)
                 await ctx.respond(f"❌ | You're on a cooldown. Please wait {cooldown_remaining:.2f} seconds before working again.")
                 return
        last_work_command[user_id] = time.time()
        await ctx.respond(embed=discord.Embed(title="Working...",description="You are right now working at Phantom's Bistro...",color=discord.Color.og_blurple()))
        print(ctx.author)
        user_id = ctx.author.id
        earnings = random.randint(5, 25)
        earnings = math.floor(earnings)
        result = random.choices(
            ["success", "mess_up_order", "late_arrival", "extra_work"],
            weights=[70, 15, 15, 20],
            k=1
        )[0]
        sid = str(ctx.guild.id)
        server_data = await load_data(sid)
        inventory = server_data[str(ctx.author.id)].get("inventory", [])
        if "Alarm" in inventory:
            earnings = random.randint(9, 32)
            result = random.choices(
            ["success", "mess_up_order", "late_arrival", "extra_work"],
            weights=[83, 2, 5, 30],
            k=1
        )[0]
        resultmsg = "N/A"
        color = discord.Color.og_blurple()
        if result == "success":
            amr = await add_money(str(ctx.guild.id), str(user_id), str(earnings))
            
            resultmsg = f"You worked at Phantom's Bistro and earned ${earnings}!"
            if amr == 1:
                resultmsg = resultmsg + " But you failed to get the money (internal error)"
            color = discord.Color.green()
        elif result == "mess_up_order":
            earnings = 0
            resultmsg = "Oops! You messed up someone's order and didn't get paid. Your boss yelled at you and lectured you."
            color = discord.Color.red()
        elif result == "late_arrival":
            earnings *= 0.4  
            if "Alarm" in inventory:
              earnings *= 0.55
            earnings = math.floor(earnings)
            amr = await add_money(str(ctx.guild.id), str(user_id), str(earnings))
            resultmsg = f"You arrived late but still earned ${earnings}. Your boss yelled at you." 
            if amr == 1:
                resultmsg = resultmsg + " But you failed to get the money (internal error)"
            color = discord.Color.orange()
        elif result == "extra_work":
            earnings *= 2 
            earnings += 5
            earnings = math.floor(earnings)
            amr = await add_money(str(ctx.guild.id), str(user_id), str(earnings))
            resultmsg = f"You worked for an extra {random.randrange(1,3)} hours and {random.randrange(10,59)} and earned ${earnings}! Your boss appreciates it!"
            if amr == 1:
                resultmsg = resultmsg + " But you failed to get the money (internal error)"
            color = discord.Color.green()
        if "Alarm" in inventory:
            resultmsg = resultmsg + "\nYou woke up on-time with the ⏰ Alarm which made you arrive on-time more!"
        
        await asyncio.sleep(2.5)
        await ctx.respond(embed=discord.Embed(title="Work result:",description=resultmsg,color=color))
        
    @bridge.bridge_command(description="View items availiable in the shop")    
    async def shop(self, ctx):
        embed = discord.Embed(title="Shop", description="Welcome to the shop! Here are the available items:",color=discord.Color.og_blurple())
        embed.set_footer(text="Run -buy <item> or /buy <item> to buy the item!")
        for item in items:
            if item["shop"]:
             embed.add_field(name=item["name"], value=f"Price: ${item['price']}")
        await ctx.respond(embed=embed)
    
    @bridge.bridge_command(description="Buy an item from the shop.")
    async def buy(self, ctx, item_name):
        await ctx.defer()
        item_name = item_name.lower()
        if not check_json(str(ctx.guild.id), str(ctx.author.id)):
            await ctx.respond(f"❌ | You don't exist on {ctx.guild.name}. Please generate your data by doing `-bal` or `/bal`")
            return
        item = next((i for i in items if i["name"].lower() == item_name), None)
        if item is None:
            embed = discord.Embed(title="Error",description=f"Failed to buy {item['name']}. Item does not exist. You have not been charged.")
            await ctx.respond(embed=embed)
            return
        if not item["shop"]:
           embed = discord.Embed(title="Error",description=f"Failed to buy {item['name']}. You cannot buy this item.")
           await ctx.respond(embed=embed)
           return
        money = await get_money(str(ctx.guild.id), str(ctx.author.id))
        if money[0] <= item['price']:
           embed = discord.Embed(title="Error",description=f"Failed to buy {item['name']}. You do not have enough money.")
           await ctx.respond(embed=embed)
           return
        resultbuy = await remove_money(str(ctx.guild.id), str(ctx.author.id), item["price"])
        resultgive = await add_item(str(ctx.guild.id), str(ctx.author.id), item["name"])
        if resultbuy == 0:
            embed = discord.Embed(title="Success",description=f"You have successfully bought {item['name']}")
        else:
            embed = discord.Embed(title="Error",description=f"Failed to buy {item['name']}. An error has occurred.")
        await ctx.respond(embed=embed)
    @bridge.bridge_command(description="Sell items to the shop for money.")
    async def sell(self, ctx, item_name):
     await ctx.defer()
     if not check_json(str(ctx.guild.id), str(ctx.author.id)):
           await ctx.respond(f"❌ | You don't exist on {ctx.guild.name}. Please generate your data by doing `-bal` or `/bal`")
           return
     sid = str(ctx.guild.id)
     server_data = await load_data(sid)
     if server_data is None or server_data.get(str(ctx.author.id)) is None:
         embed = discord.Embed(title="Error", description="Failed to sell item. User data not found.")
         await ctx.respond(embed=embed)
         return
     inventory = server_data[str(ctx.author.id)].get("inventory", [])
     if item_name not in inventory:
         embed = discord.Embed(title="Error", description=f"Failed to sell {item_name}. Item does not exist in your inventory. \nReminder: Item names are **case-sensitive**")
         await ctx.respond(embed=embed)
     item = next((i for i in items if i["name"] == item_name), None)
     if item is None:
         embed = discord.Embed(title="Error", description=f"Failed to sell {item_name}. Item details not found.")
         await ctx.respond(embed=embed)
         return
     sell_price = math.floor(item["price"] * 0.9)
     result = await add_money(str(ctx.guild.id), str(ctx.author.id), sell_price)
     if result == 0:
         result = await remove_item(str(ctx.guild.id), str(ctx.author.id), item_name)
         if result == 0:
             embed = discord.Embed(title="Success", description=f"You have successfully sold {item_name} for ${sell_price}.")
         else:
             embed = discord.Embed(title="Error", description=f"Failed to sell {item_name}. An error has occurred.")
     else:
         embed = discord.Embed(title="Error", description=f"Failed to sell {item_name}. An error has occurred.")
     await ctx.respond(embed=embed)

    @bridge.bridge_command(description="Rob someone or something for a chance of money... or a fine.")
    async def rob(self, ctx):
        await ctx.defer()
        if not check_json(str(ctx.guild.id), str(ctx.author.id)):
            await ctx.respond(f"❌ | You don't exist on {ctx.guild.name}. Please generate your data by doing `-bal` or `/bal`")
            return
        user_id = str(ctx.author.id)
        current_time = time.time()
        if user_id in last_rob_command:
            last_execution_time = last_rob_command[user_id]
            if current_time - last_execution_time < 60:
                cooldown_remaining = 60 - (current_time - last_execution_time)
                await ctx.respond(f"❌ | You're on a cooldown. Please wait {cooldown_remaining:.2f} seconds before robbing again.")
                return
        last_rob_command[user_id] = current_time
        server_data = await load_data(ctx.guild.id)
        user_inventory = server_data[str(ctx.author.id)]["inventory"]
        if "Gun" not in user_inventory and "Knife" not in user_inventory:
            embed = discord.Embed(title="Robbery Failed", description="You need a Gun or a Knive in your inventory to rob... how tf do you rob without a weapon?")
            embed.color = discord.Color.red()
            await ctx.send(embed=embed)
            return
        robbery_locations = ["house", "car", "person", "Phantom's Bistro", "thin air?!?!???","the bank","yourself??!?","poor grandma","Ice Spice"]
        robbery_location = random.choice(robbery_locations)
        success = random.random() < 0.67
        if "Cloak" in user_inventory:
            success = random.random() < 0.82
        if success:
            reward = random.randint(1, 36)
            await add_money(ctx.guild.id, str(ctx.author.id), reward)
            embed = discord.Embed(title="Robbery Success", description=f"You successfully robbed {robbery_location} and obtained ${reward}.", color=discord.Color.green())
        else:
            fine = random.randint(10, 75)
            await remove_money(ctx.guild.id, str(ctx.author.id), fine)
            embed = discord.Embed(title="Robbery Failed", description=f"You were caught attempting to rob {robbery_location} and fined ${fine}.\n\n **Protip**: Get a Cloak to reduce your chances of getting fined!", color=discord.Color.red())
        await ctx.respond(embed=embed)

    @bridge.bridge_command(description="Deposit money into the bank. (0% interest)")
    async def deposit(self, ctx, amount: str):
     await ctx.defer()
     if not check_json(str(ctx.guild.id), str(ctx.author.id)):
            await ctx.respond(f"❌ | You don't exist on {ctx.guild.name}. Please generate your data by doing `-bal` or `/bal`")
            return
     if amount.endswith("%"):
         amount_percentage = amount.rstrip("%")
         if not amount_percentage.isdigit():
             embed = discord.Embed(title="Deposit Failed", description="Invalid percentage value.")
             embed.color = discord.Color.red()
             await ctx.respond(embed=embed)
             return
 
         money = await get_money(str(ctx.guild.id), str(ctx.author.id))
         print(amount_percentage)
         amount = math.floor(money[0] * int(amount_percentage) / 100)

     amount = str(amount).lower()
     if amount == "max":
         money = await get_money(str(ctx.guild.id), str(ctx.author.id))
         amount = money[0]
     elif amount == "all":
         money = await get_money(str(ctx.guild.id), str(ctx.author.id))
         amount = money[0]
 
     amount = int(math.floor(float(amount)))
 
     if amount < 1:
         embed = discord.Embed(title="Deposit Failed", description="You must deposit at least $1.")
         embed.color = discord.Color.red()
         await ctx.respond(embed=embed)
         return
 
     money = await get_money(str(ctx.guild.id), str(ctx.author.id))
     if money[0] < amount:
         embed = discord.Embed(title="Deposit Failed", description="You do not have enough money to deposit.")
         embed.color = discord.Color.red()
         await ctx.respond(embed=embed)
         return
 
     await move_wallet_to_bank(str(ctx.guild.id), str(ctx.author.id), amount)
 
     embed = discord.Embed(title="Deposit Success", description=f"You have successfully deposited ${amount} into your bank.")
     embed.color = discord.Color.green()
     await ctx.respond(embed=embed)

    @bridge.bridge_command(description="Withdraw money out of the bank.")
    async def withdraw(self, ctx, amount: str):
        await ctx.defer()
        if not check_json(str(ctx.guild.id), str(ctx.author.id)):
            await ctx.respond(f"❌ | You don't exist on {ctx.guild.name}. Please generate your data by doing `-bal` or `/bal`")
            return
        if amount.endswith("%"):
         amount_percentage = amount.rstrip("%")
         if not amount_percentage.isdigit():
             embed = discord.Embed(title="Withdrawal Failed", description="Invalid percentage value.")
             embed.color = discord.Color.red()
             await ctx.respond(embed=embed)
             return
 
         money = await get_money(str(ctx.guild.id), str(ctx.author.id))
         print(amount_percentage)
         amount = math.floor(money[1] * int(amount_percentage) / 100)

        amount = str(amount).lower()
        if amount == "max":
            money = await get_money(str(ctx.guild.id), str(ctx.author.id))
            amount = money[1]
        elif amount == "all":
            money = await get_money(str(ctx.guild.id), str(ctx.author.id))
            amount = money[1]
 
     
        amount = int(math.floor(float(amount)))
    
        if amount < 1:
            embed = discord.Embed(title="Withdrawal Failed", description=f"You must withdraw at least $1, not {amount}")
            embed.color = discord.Color.red()
            await ctx.respond(embed=embed)
            return
    
        money = await get_money(str(ctx.guild.id), str(ctx.author.id))
        if money[1] < amount:
            embed = discord.Embed(title="Withdrawal Failed", description="You do not have enough money in your bank to withdraw.")
            embed.color = discord.Color.red()
            await ctx.respond(embed=embed)
            return
    
        await move_bank_to_wallet(str(ctx.guild.id), str(ctx.author.id), amount)
    
        embed = discord.Embed(title="Withdrawal Success", description=f"You have successfully withdrawn ${amount} from your bank.")
        embed.color = discord.Color.green()
        await ctx.respond(embed=embed)

    @bridge.bridge_command(description="Sync your data across all servers")
    async def sync(self, ctx, confirm: str = "0"):
     await ctx.defer()
     if not check_json(str(ctx.guild.id), str(ctx.author.id)):
            await ctx.respond(f"❌ | You don't exist on {ctx.guild.name}. Please generate your data by doing `-bal` or `/bal`")
            return
     current_server_id = ctx.guild.id
     user_id = ctx.author.id
 
     if confirm.lower() in ["no", "false", "0","n"]:
         await ctx.respond("❓ | Are you sure you want to sync your save data? This action cannot be undone. \n Please use `-sync yes` or `/sync confirm:yes` to confirm."
                        )
     elif confirm.lower() in ["yes", "true", "1","y"]:
         success = await sync_save(current_server_id, user_id)
         if success:
             await ctx.respond("✔ | Your save data has been successfully synced across all servers.")
         else:
             await ctx.respond("❌ | An error occurred while syncing your save data.")
     else:
         await ctx.respond("❌ | Invalid confirmation option. Please use `-sync yes` or `/sync confirm:yes` to confirm or `-sync no` or `/sync confirm:no` to cancel.")
    @bridge.bridge_command(description="Beg on the streets for a CHANCE of money.")
    async def beg(self,ctx):
        await ctx.defer()
        user_id = str(ctx.author.id)
        current_time = time.time()
        if not check_json(str(ctx.guild.id), str(ctx.author.id)):
            await ctx.respond(f"❌ | You don't exist on {ctx.guild.name}. Please generate your data by doing `-bal` or `/bal`")
            return
        if user_id in last_beg_command:
            last_execution_time = last_beg_command[user_id]
            if current_time - last_execution_time < 20:
                cooldown_remaining = 20 - (current_time - last_execution_time)
                await ctx.respond(f"❌ | Don't be a baby. Please wait {cooldown_remaining:.2f} seconds before begging again.")
                return
        last_beg_command[user_id] = current_time
        outcomes = [
            ("money", 0.4),
            ("items", 0.01),
            ("nothing", 0.5),
            ("fine", 0.09)
        ]
        outcome, probability = random.choices(outcomes, weights=[p for _, p in outcomes])[0]
        msg = "N/A"
        if outcome == "money":
            msg = await self.beg_for_money(ctx, probability)
        elif outcome == "items":
            msg = await self.beg_for_items(ctx, probability)
        elif outcome == "nothing":
            msg = await self.beg_for_nothing(ctx)
        elif outcome == "fine":
            msg = await self.beg_for_fine(ctx, probability)
        embed = discord.Embed(color=discord.Color.blue(),title="Beg Result",description=f"{msg}")
        await ctx.respond(embed=embed)
    
    async def beg_for_money(self, ctx, probability):
        amount = random.randint(1, 11)
        amount = amount * 2 if probability == 0.02 else amount
    
        person = random.choice(["grandpa", "grandma", "a stranger", "a rich person", "someone", "a nice person", "Mr. Clean","MrBeast","PewDiePie","DanTDM","Elon Mask","The Cum Monster","E.T","Spoiled Brat","Rich kid","Rich parent","Dumbass","Financial Dumbass","Green Day","Katie Parry","Scrub Daddy"])
        messages = [
            f"You found ${amount} on the streets!",
            f"You asked your {person} for money and they gave you ${amount}",
            f"{person.capitalize()} gave you ${amount}",
            f"A stranger donated ${amount} to you!",
            f"A nice person gave you ${amount}!",
            f"{person.capitalize()}: sure, take ${amount}.",
            f"You found ${amount} from... thin air?",
            f"You decided to go work and got ${amount}.",
            f"{person.capitalize()}: ok take ${amount}",
            f"{person.capitalize()} left ${amount} for you.",
            f"You got desperate and found ${amount}."
        ]
        await add_money(ctx.guild.id, ctx.author.id, amount)  
        message = random.choice(messages)
        return message
    
    async def beg_for_items(self, ctx, probability):
        item = random.choice(["Alarm", "Gun", "Cake", "Ice Cream"])
        person = random.choice(["someone", "a nice person", "a stranger","thing","E.T","MrBeast","DanTDM","Pewdiepie","My pet goldfish","Mr. Clean"])
        message = f"{person.capitalize()} didn't leave any money but left a {item} for you!"
        await add_item(ctx.guild.id, ctx.author.id, item)  
        return message
    
    async def beg_for_nothing(self, ctx):
        person = random.choice(["grandpa", "grandma", "a stranger", "a rich person", "someone", "a nice person", "Mr. Clean","Charli' Dmailo","MrBeetroot","Megacorp","minecraft villager","DanTDM", "A homeless man","A homeless woman","A baby","A child","The Cum Monster","Green Day","Scrub Daddy","Shark Tank", "Spongebob","Patrick","Squidwerd"])
        messages = [
            "Someone asked you to get a job",
            f"{person.capitalize()}: no lol.",
            f"{person.capitalize()}: stop begging",
            "You got ignored.",
            f"{person.capitalize()} just walked right past you and left nothing.",
            f"{person.capitalize()}: no",
            "You started a GoFunMe and you got $0.",
            "The sun went against you and you didn't get anything.",
            f"{person.capitalize()}: I'd recommend you to get a job.",
            f"{person.capitalize()}: I already gave money to someone else.",
            f"{person.capitalize()}: I would, but i'm broke too."
        ]
        
        message = random.choice(messages)
        return message
    
    async def beg_for_fine(self, ctx, probability):
        chance = random.randint(5,10) % 2
        if (chance == 0):
         amount = random.randint(1, 100)
         amount = amount * 2 if probability == 0.18 else amount
         person = random.choice(["a car", "someone", "Elon Mush","Elon Musk","Microshit","grandma","grandpa","Mr. Clean","a cat","a dog","Charli Demailo","TikTonk","E.T","The police","a scammer","a rich person","a bank","thin air (???!?)"])
         message = f"You got desperate and tried robbing {person} but instead got fined ${amount}."
         await remove_money(ctx.guild.id, ctx.author.id, amount)
        if (chance == 1):
         amount = random.randint(341,3479)
         amount = amount * 2 if probability == 0.18 else amount
         message = f"You quite literally toasted yourself so you had to go to the hospital and pay {amount} to get untoasted."
         await remove_money(ctx.guild.id, ctx.author.id, amount)
        return message
    @bridge.bridge_command(description="Go out to the nearby pond and go fishing for a chance of fish.")
    async def fish(self,ctx):
     if not check_json(str(ctx.guild.id), str(ctx.author.id)):
            await ctx.respond(f"❌ | You don't exist on {ctx.guild.name}. Please generate your data by doing `-bal` or `/bal`")
            return
     user_id = str(ctx.author.id)
     current_time = time.time()
     
     if user_id in last_fish_command:
                 last_execution_time = last_fish_command[user_id]
                 if current_time - last_execution_time < 45:
                     cooldown_remaining = 45 - (current_time - last_execution_time)
                     await ctx.respond(f"❌ | There are no fish in the pond right now! Please check back in {cooldown_remaining:.2f} seconds.")
                     return
     
     last_fish_command[user_id] = current_time
     server_data = await load_data(ctx.guild.id)
     user_inventory = server_data[str(ctx.author.id)]["inventory"]
     if "FishingRod" not in user_inventory:
         embed = discord.Embed(title="Fishing Failed", description="You need a Fishing Rod in your inventory to fish! how tf do you fish without a rod? do you like tactical fish and like catch it with your bare hands or smth?")
         embed.color = discord.Color.red()
         await ctx.respond(embed=embed)
         return
     with open('extensions/economy/fish.json','r') as fishfile:
         fish_list = json.load(fishfile)
     result = random.choices(
         population=[None, *fish_list],
         weights=[0.25] + [prob for _, prob in fish_list]
     )[0]
     
     if result is None:
         messages = [
             "You reeled in, but there were no fish that bit the bait.",
             "You reeled in, but the fish were sleeping.",
             "You reeled in, but all the fish didn't care.",
             "You reeled in, but the fish were taking a walk.",
             "You reeled in, but there were no fish."
         ]
         message = random.choice(messages)
         embed = discord.Embed(title="Fishing Result", description=message)
         embed.color = discord.Color.green()
         await ctx.respond(embed=embed)
     else:
         fish_name = result[0]
         await add_item(ctx.guild.id, ctx.author.id, fish_name)
         embed = discord.Embed(title="Fishing Result", description=f"You caught a {fish_name} ({math.floor(result[1] * 100)}%) !\n Go ahead and sell it for a profit!")
         embed.color = discord.Color.green()
         await ctx.respond(embed=embed)
    @bridge.bridge_command(description="Go out into the forest to hunt for some animals.")
    async def hunt(self,ctx):
     if not check_json(str(ctx.guild.id), str(ctx.author.id)):
            await ctx.respond(f"❌ | You don't exist on {ctx.guild.name}. Please generate your data by doing `-bal` or `/bal`")
            return
    
     server_data = await load_data(ctx.guild.id)
     user_inventory = server_data[str(ctx.author.id)]["inventory"]
    
     if "Gun" not in user_inventory:
         embed = discord.Embed(title="Hunting Failed", description="You need a Gun in your inventory to go hunting!")
         embed.color = discord.Color.red()
         await ctx.respond(embed=embed)
         return
    
     
     if "HuntingLicense" in user_inventory:
         has_license = True
         fine_chance = 0
     else:
         has_license = False
         fine_chance = 0.75
    
    
    
     user_id = str(ctx.author.id)
     current_time = time.time()

     if user_id in last_hunt_command:
             last_execution_time = last_hunt_command[user_id]
             if current_time - last_execution_time < 90:
                 cooldown_remaining = 90 - (current_time - last_execution_time)
                 await ctx.respond(f"❌ | There are no animals in the forest! Please check back in {cooldown_remaining:.2f} seconds.")
                 return

     last_hunt_command[user_id] = current_time
    
    
     if random.random() < fine_chance:
         
         await remove_money(ctx.guild.id, ctx.author.id, 100)
         embed = discord.Embed(title="Hunting Failed", description="You hunted without a Hunting License and got fined $100!")
         embed.color = discord.Color.red()
         await ctx.respond(embed=embed)
         return
     else:
        if random.random() < 0.35:
            
            embed = discord.Embed(title="Hunting Result", description="You went hunting, but didn't catch anything!")
            embed.color = discord.Color.orange()
            await ctx.respond(embed=embed)
        else:
            
            with open('extensions/economy/hunting_loot.json','r') as hunting:
                loot = json.load(hunting)
            animal = loot[random.randint(0,len(loot))]
            await add_item(ctx.guild.id, ctx.author.id, animal[0])
            
            embed = discord.Embed(title="Hunting Result", description=f"You went hunting and caught a {animal[0]} ({math.floor(animal[1] * 100)}%)!")
            embed.color = discord.Color.green()
            await ctx.respond(embed=embed)

def setup(client):
    client.add_cog(Economy(client))