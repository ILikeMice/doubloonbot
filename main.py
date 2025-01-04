import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import dotenv
import random
import math

dotenv.load_dotenv()

BOT_TOKEN = str(os.environ.get("BOT_TOKEN"))

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

def readdata():
    with open("data.json", "r") as infile:
        data = json.load(infile)
    return data

def writedata(data):
    with open("data.json", "w") as outfile:
        json.dump(data, outfile, indent=3)

def register(uid):
    data = readdata()
    if not uid in data:
        data[uid] = {}
        data[uid]["doubloons"] = 0
        data[uid]["bank"] = 0
        writedata(data)

@bot.tree.command(name="pay", description="Pay someone!")
async def pay(interaction: discord.Interaction, user: str, amount: int):
    data = readdata()
    user1id = str(interaction.user.id)
    user2id = user.replace(">","").replace("@","").replace("<","")

    register(user1id)
    register(user2id)
        
    if data[user1id]["doubloons"] >= amount:
        data[user1id]["doubloons"] -= amount
        data[user2id]["doubloons"] += amount
        writedata(data)
        return await interaction.response.send_message(f"Paid user {user} {amount} doubloons!", ephemeral=True)


    await interaction.response.send_message("You don't have enough doubloons!")

@bot.tree.command(name="deposit", description="Deposit your doubloons into a safe bank!")
async def deposit(interaction: discord.Interaction, amount: float):
    uid = str(interaction.user.id)
    data = readdata()

    if data[uid]["doubloons"] >= amount:

        data[uid]["doubloons"] -= amount
        data[uid]["bank"] += amount

        writedata(data)

        return await interaction.response.send_message(f"Deposited {amount} doubloons to your bank!", ephemeral=True)
    
    await interaction.response.send_message("You don't have enough doubloons!")


@bot.tree.command(name="withdraw", description="Withdraw doubloons from your bank!")
async def withdraw(interaction: discord.Interaction, amount: float):
    uid = str(interaction.user.id)
    data = readdata()

    if data[uid]["bank"] >= amount:
        data[uid]["doubloons"] += amount
        data[uid]["bank"] -= amount
        writedata(data)

        return await interaction.response.send_message(f"Withdrew {amount} doubloons from your bank!", ephemeral=True)

    await interaction.response.send_message("Not enough doubloons in your bank!")

@bot.tree.command(name="balance", description="View your own or someone elses doubloons!")
@app_commands.describe(
    user="The User whose balance you wish to see, leave empty to get your balance."
)
async def balance(interaction: discord.Interaction, user: str = None):
    if user:
        uid = user.replace(">","").replace("@","").replace("<","")
    else:
        uid = str(interaction.user.id)
    register(uid)
    data = readdata()

    embed = discord.Embed(description=f"### <@{uid}> 's balance \n Bank: {data[uid]["bank"]}<:doubloon:1323064445370368182> \n Pocket: {data[uid]["doubloons"]}<:doubloon:1323064445370368182> \n Net Worth: {data[uid]["doubloons"] + data[uid]["bank"]}<:doubloon:1323064445370368182>")
    await interaction.response.send_message(embed=embed, ephemeral=True)  

@bot.tree.command(name="beg", description="Beg for doubloons!")
@discord.app_commands.checks.cooldown(1, 300)
async def beg(interaction: discord.Interaction):
    amount = float(random.randint(0,100))/10
    data = readdata()
    data[str(interaction.user.id)]["doubloons"] += amount
    writedata(data)
    await interaction.response.send_message(f"You got {amount}<:doubloon:1323064445370368182>!", ephemeral=True)

@beg.error
async def begerror(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(str(error), ephemeral=True)

@bot.tree.command(name="leaderboard", description="Show the top doubloon owners!")
async def leaderboard(interaction: discord.Interaction, page: int):
    data = readdata()
    sorteddata = sorted(data.items(), key=lambda x: x[1]["doubloons"] + x[1]["bank"], reverse=True)
    pageamnt = math.ceil(len(data)/10)
    print(pageamnt)
    if pageamnt < page: return await interaction.response.send_message("Please enter a lower page number!")

    start = 1 + (page-1)*10
    if len(sorteddata) >= 10+(page-1)*10:
        end = 10+(page-1)*10
    else:
        end = len(sorteddata)
    desc = ""

    for i in range(start-1, end-1):
        print(i)
        desc += f"{i}. <@{sorteddata[i][0]}>: {sorteddata[i][1]["doubloons"] + sorteddata[i][1]["bank"]} \n"

    embed = discord.Embed(title=f"Leaderboard Page {page}/{pageamnt}", description=desc)
    print(sorteddata)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="guess", description="Guess a number between 1 and 10, get 10x of your bet amount!")
async def guess(interaction: discord.Interaction, number: int, amount: float):
    if number not in range(1,10):
        return await interaction.response.send_message("Number must be between 1 and 10!", ephemeral=True)
    correctnum = random.randint(1,10)
    data = readdata()
    uid = str(interaction.user.id)

    if data[uid]["doubloons"] < amount:
        return await interaction.response.send_message("You don't have enough doubloons!", ephemeral=True)

    data[uid]["doubloons"] -= amount

    if number == correctnum:
        data[uid]["doubloons"] += amount*10
        writedata(data)
        return await interaction.response.send_message(f"You won {amount*9} doubloons!", ephemeral=True)

    writedata(data)
    await interaction.response.send_message(f"You lost! Correct number was {correctnum}!", ephemeral=True)
    
          


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

bot.run(BOT_TOKEN)