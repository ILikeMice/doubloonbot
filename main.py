import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import dotenv

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


@bot.tree.command(name="pay", description="Pay someone!")
async def pay(interaction: discord.Interaction, user: str, amount: str):
    data = readdata()
    user1id = interaction.message.author.id
    user2id = user.replace(">","").replace("@","").replace("<","")

    await interaction.response.send_message(user2id)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

bot.run(BOT_TOKEN)