import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
import mariadb
from src.item_similarity import match_item

load_dotenv()

# Setting up the bot client
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)


def main() -> None:
    bot.run(os.getenv('BOT_TOKEN'))    


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    try:
        synced_commands = await tree.sync()
        print(f'Synced {len(synced_commands)} commands.')
    except Exception as e:
        print(f'Error syncing, {e}')


@tree.command(name='hello', description='Just says hello')
async def hello(ctx: discord.interactions.Interaction):
    await ctx.response.send_message(content=f'Hello, {ctx.user.mention}')


@tree.command(name='fetch_snapshot', description='Fetches the last known snapshot for an item')
@app_commands.describe(item_name="Name of the item")
async def fetch_last_snapshot(ctx: discord.interactions.Interaction, item_name: str):

    # db_host = os.getenv('DB_HOST', 'localhost')
    # db_user = os.getenv('DB_USER', 'root')
    # db_password = os.getenv('DB_PASSWORD', 'password')
    # db_name = os.getenv('DB_NAME')
    # db_table = os.getenv('DB_TABLE')
    
    matched_item_name = match_item(item_name)
    if matched_item_name is None:
        await ctx.response.send_message(content=f'Invalid item name, please try again.')    
    else:
        await ctx.response.send_message(content=f'You asked for {matched_item_name[0]}')


main()