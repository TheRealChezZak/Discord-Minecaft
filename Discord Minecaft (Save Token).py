import discord
import requests
import base64
import os
from discord.ext import commands

import os.path
from os import path

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='c!', intents=intents)

@bot.event
async def on_ready():
    print(f'Login as {bot.user.name} --> ID: ({bot.user.id})')
    print('-----------------------------------------------------------')

token_file = os.path.join(os.path.expanduser("~"), "token.txt")
if path.exists(token_file):
    with open(token_file, "r") as f:
        token = f.read().strip()
else:
    token = input("Please enter your Discord bot token: ")
    with open(token_file, "w") as f:
        f.write(token)

@bot.command()
async def mcjavaserver(ctx, server_address: str = None):
    if server_address is None:
        await ctx.send("Please provide a server address")
        return
    url = f"https://api.mcstatus.io/v2/status/java/{server_address}"
    response = requests.get(url)

    if response.status_code != 200:
        await ctx.send(f"Failed to get server info. Status code: {response.status_code}")
    else:
        server_info = response.json()
        if not server_info["online"]:
            await ctx.send("That server is offline!")
        elif "server is offline" in server_info.get("motd", {}).get("raw", "").lower():
            await ctx.send("That server is offline!")
        else:
            icon_data = server_info.get("icon")
            if icon_data:
                icon_bytes = base64.b64decode(icon_data.split(",")[1])
                with open("server_icon.png", "wb") as f:
                    f.write(icon_bytes)
                file = discord.File("server_icon.png")
                embed = discord.Embed(title=f"{server_address} Server Info", color=0x00ff00)
                embed.set_thumbnail(url="attachment://server_icon.png")
            else:
                embed = discord.Embed(title=f"{server_address} Server Info", color=0x00ff00)

            embed.add_field(name="Status", value="Online", inline=False)
            embed.add_field(name="Host", value=server_info["host"], inline=False)
            embed.add_field(name="Port", value=server_info["port"], inline=False)
            embed.add_field(name="Players online", value=server_info["players"]["online"], inline=False)
            embed.add_field(name="Max players", value=server_info["players"]["max"], inline=False)
            embed.add_field(name="MOTD", value=server_info["motd"]["raw"], inline=False)
            embed.add_field(name="Version", value=server_info["version"]["name_raw"], inline=False)
            await ctx.send(file=file, embed=embed)
            if icon_data:
                os.remove("server_icon.png")

bot.run(token)
