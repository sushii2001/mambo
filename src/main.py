#!/usr/bin/env python3

import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import logging

# Define project paths
PROJ_SRC_PATH = os.path.dirname(os.path.abspath(__file__))
PROJ_ROOT_PATH = f"{PROJ_SRC_PATH}/../"
PROJ_LOG_PATH = f"{PROJ_ROOT_PATH}/logs"
DISCORD_LOG_PATH = f"{PROJ_LOG_PATH}/discord.log"

# Load project envs
load_dotenv()
DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]
DEBUG_SERVER_ID = os.environ.get("DEBUG_SERVER_ID", "")

# Initialization
log_handler = logging.FileHandler(filename=DISCORD_LOG_PATH, encoding="utf-8", mode="w")
logger = logging.getLogger("discord_logger")
logger.addHandler(log_handler)
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Local develop configuration
EN_DEBUG = True
DUMMY_ROLE = "Dummy"
logger.setLevel(logging.INFO)

# Events
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Connected to {len(bot.guilds)} guilds')
    print('Syncing commands...')
    await bot.tree.sync()
    print('Commands synced!')
    print(f"We are ready to go in, {bot.user.name}!")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")

@bot.event
async def on_message(message):
    # skip message from bot itsef
    if message.author == bot.user:
        return

    # profanity check
    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} - That's not very sigma. 🙂")

    logger.debug(f"Message received: {message.content}")
    # discord original handling
    await bot.process_commands(message)

# Custom Bot interactions:
@bot.tree.command(name="test123", description="Testing 123")
async def test123(interaction: discord.Interaction):
    await interaction.response.send_message(f"Testing 123 ... from {interaction.user.mention}!")

# Custom Bot commands:
@bot.command(name="hello", description="Says hello back!")
async def hello(ctx):
    # !hello
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=DUMMY_ROLE)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} is now assigned to {role} role!")
    else:
        await ctx.send(f"Role {role} doesn't exist")

@bot.command()
async def remove_role(ctx):
    role = discord.utils.get(ctx.guild.roles, name=DUMMY_ROLE)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention}'s {role} role is now removed!")
    else:
        await ctx.send(f"Role {role} doesn't exist")

@bot.command()
@commands.has_role(DUMMY_ROLE)
async def secret(ctx):
    await ctx.send(f"Welcome to the {DUMMY_ROLE} club 🤡")

@secret.error
async def secret_err(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"You're not part of the hood little bro 🗿")

@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"Message from {ctx.author}:\n {msg}")

@bot.command()
async def reply(ctx):
    await ctx.reply("This is a reply to your message!")

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question)
    poll_msg = await ctx.send(embed=embed)
    await poll_msg.add_reaction("👍")
    await poll_msg.add_reaction("👎")

def main():
    try:
        bot.run(DISCORD_TOKEN, log_handler=log_handler, log_level=logging.DEBUG)
    except KeyboardInterrupt:
        logger.debug(f"Bot stopped manually.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()