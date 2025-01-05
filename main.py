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

def getitems():
    with open("items.json", "r") as file:
        items = json.load(file)
    return items

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

@beg .error
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
    
@bot.tree.command(name="plunder", description="Plunder another pirates doubloons!")
async def plunder(interaction: discord.Interaction, user: discord.User):    
    uid = str(interaction.user.id)
    victimid = str(user.id)          
    success = random.randint(1,100)
    data = readdata()
    if "AntiPlunder" in data[victimid]["effects"]:
        loss = data[uid]["doubloons"] * (random.randint(1,15) / 100)
        data[uid]["doubloons"] -= loss
        writedata(data)

        return await interaction.response.send_message(f"Blimeys! <@{victimid}> had AntiPlunder™ active and you lost {loss} doubloons!")
    
    if success in range(1,15):
        data[victimid]["doubloos"] -= data[victimid]["doubloons"] * (20/100)
        multiplier = 1

        if "The Pirate's Blessing" in data[uid]["effects"]:
            blesscount = data[uid]["effects"].count("The Pirate's Blessing")
            
            for i in range(blesscount-1):
                data[uid]["effects"].remove("The Pirate's Blessing")
                multiplier = multiplier*(20/100)
        data[uid]["doubloons"] += data[victimid]["doubloons"] * (20/100) * multiplier
        writedata(data)
        if multiplier > 1:
            return await interaction.response.send_message(f"Success! You plundered <@{victimid}> for {data[victimid]["doubloons"] * (20/100) * multiplier} doubloons! The Pirate's Blessing gave you a multiplier of {multiplier}!")
        return await interaction.response.send_message(f"Success! You plundered <@{victimid}> for {data[victimid]["doubloons"] * (20/100)} doubloons!")
    
    loss = data[uid]["doubloons"] * (random.randint(1,15) / 100)
    data[uid]["doubloons"] -= loss
    writedata(data)

    await interaction.response.send_message(f"Shucks! You got caught and lost {loss} doubloons!")
    
@bot.tree.command(name="shop", description="Buy some items!")
async def shop(interaction: discord.Interaction):
    shopembed = discord.Embed(title="Super awesome Shop!")
    items = getitems()
    for i in items:
        shopembed.add_field(name=f"{i} ({items[i]["price"]}<:doubloon:1323064445370368182>)", value=items[i]["description"])
    await interaction.response.send_message(embed=shopembed, ephemeral=True)

@bot.tree.command(name="inventory", description="View all your items!")
async def inventory(interaction: discord.Interaction):
    data = readdata()
    desc = ""
    uid = str(interaction.user.id)
    used = []

    for i in data[uid]["inventory"]:
        if i not in used:
            used.append(i)
            desc += f"{i}: {data[uid]["inventory"].count(i)}x \n\n"
    await interaction.response.send_message(embed=discord.Embed(title="Yer Inventory", description=desc))


@bot.tree.command(name="purchase")
async def purchase(interaction: discord.Interaction, item: str):
    items = getitems()
    data = readdata()
    uid = str(interaction.user.id)
    if item not in items:
        return await interaction.response.send_message("This Item does not exist!", ephemeral=True)
    if data[uid]["doubloons"] >= items[item]["price"]:
        data[uid]["doubloons"] -= items[item]["price"]
        data[uid]["inventory"].append(item) 
        writedata(data)
        return await interaction.response.send_message(f"Bought {item} for {items[item]["price"]}<:doubloon:1323064445370368182>!", ephemeral=True)
    await interaction.response.send_message("You don't have enough doubloons!", ephemeral=True)

@purchase.autocomplete("item")
async def autoitem(
    interaction: discord.Interaction,
    item: str,
) -> list[app_commands.Choice[str]]:
    items = [i for i in getitems()]
    return [
        app_commands.Choice(name=item, value=item)
        for item in items
    ]

class MyView(discord.ui.View):
    def __init__(self, clicked_buttons=None, correctbtns=None):
        super().__init__()
        self.clicked_buttons = clicked_buttons or []
        self.correctbtns = correctbtns or [str(random.randint(1, 25)) for i in range(15)]
        for i in range(1, 26):
            label = "🏴‍☠️" if str(i) not in self.correctbtns and str(i) in self.clicked_buttons else "💰" if str(i) in self.correctbtns and str(i) in self.clicked_buttons else "‎ "
            btn = discord.ui.Button(label=label, style=discord.ButtonStyle.gray, custom_id=str(i))
            btn.disabled = str(i) in self.clicked_buttons
            btn.callback = self.button_callback
            self.add_item(btn)

    async def button_callback(self, interaction: discord.Interaction):
        button_id = interaction.data['custom_id']
         
        if button_id not in self.clicked_buttons:
            self.clicked_buttons.append(button_id)
        if len(self.clicked_buttons) >= 12:
            corrects = len([i for i in self.clicked_buttons if i in self.correctbtns])
            self.clicked_buttons = [str(i) for i in range(1,26)]
            view = MyView(clicked_buttons=self.clicked_buttons, correctbtns=self.correctbtns)
            data = readdata()
            data[str(interaction.user.id)]["doubloons"] += corrects*100
            writedata(data)
            await interaction.response.edit_message(view=view, content=f"You got {corrects*100} doubloons!")
        view = MyView(clicked_buttons=self.clicked_buttons, correctbtns=self.correctbtns)
        await interaction.response.edit_message(view=view, content=f"{12-len(self.clicked_buttons)} guess(es) left!")



@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        view = MyView()
        await view.button_callback(interaction)

@bot.tree.command(name="use")
async def use(interaction: discord.Interaction, item: str):
    data = readdata()
    uid = str(interaction.user.id)
    if item not in data[uid]["inventory"]:
        return await interaction.response.send_message("You don't own that item!")
    match item:
        case "AntiPlunder":
            if item in data[uid]["effects"]:
                return await interaction.response.send_message("This effect is already active!")
            
            data[uid]["effects"].append(item)
            data[uid]["inventory"].remove(item)
            writedata(data)
            await interaction.response.send_message(f"{item} activated!")

        case "The Pirate's Blessing":
            data[uid]["effects"].append(item)
            data[uid]["inventory"].remove(item)
            writedata(data)
            await interaction.response.send_message(f"{item} applied!")

        case "Treasure Map":
            await interaction.response.send_message(view=MyView(), content="Click a field for a chance for treasure!")

@use.autocomplete("item")
async def autouse(
    interaction: discord.Interaction,
    item: str,
) -> list[app_commands.Choice[str]]:
    used = []
    items = [used.append(f"{i}: {readdata()[str(interaction.user.id)]["inventory"].count(i)}x") for i in readdata()[str(interaction.user.id)]["inventory"] if f"{i}: {readdata()[str(interaction.user.id)]["inventory"].count(i)}x" not in used]
    
    return [
        app_commands.Choice(name=item, value=item.split(":")[0])
        for item in used
    ]



@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

bot.run(BOT_TOKEN)