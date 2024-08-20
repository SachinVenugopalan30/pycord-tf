import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands
import mariadb
from src.item_similarity import match_item
from table2ascii import table2ascii, Merge
import logging
from logging.handlers import TimedRotatingFileHandler

load_dotenv()

# Setting up the bot client
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# Set up logging
log_dir = 'logs/bot_logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'bot.log')
logger = logging.getLogger('bot')
logger.setLevel(logging.INFO)

# Create a handler that writes log messages to a file, rotating daily
handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1)
handler.suffix = "%Y-%m-%d"  # File suffix will be the date
handler.setLevel(logging.INFO)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)


def run_bot() -> None:
    logger.info("Starting bot...")
    bot.run(os.getenv('BOT_TOKEN'))    

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}!')
    try:
        synced_commands = await tree.sync()
        logger.info(f'Synced {len(synced_commands)} commands.')
    except Exception as e:
        logger.error(f'Error syncing, {e}')
        exit(1)

async def fetch_buy_snapshots(item_name: str):
    """
    Fetches and formats the buy snapshots for a given item.

    Parameters:
    item_name (str): The name of the item to fetch buy snapshots for.

    Returns:
    str: A formatted string representing the buy snapshots for the given item.
    """
    db = mariadb.connect(host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME"))
    cursor = db.cursor(buffered=True) 

    query_for_buy_orders = '''
        SELECT listing_id, steam_id, price_keys, price_metal, date, time, is_painted, is_spelled FROM listing_snapshots
        WHERE item_name = ?
        AND event_intent=\'buy\'
        AND event_type = \'listing-update\'
        ORDER BY date DESC, time DESC
        LIMIT 5
        '''

    cursor.execute(query_for_buy_orders, (item_name,))
    # Fetch all rows
    rows = cursor.fetchall()
    ls_rows = [list(tup) for tup in rows]

    buy_table_output_for_discord = table2ascii(
        header=['Listing_ID','SteamID', 'Keys', 'Metal', 'Date', 'Time', 'Painted?', 'Spelled?'],
        body = ls_rows,
        footer=['BUY ORDERS', Merge.LEFT, Merge.LEFT, Merge.LEFT, Merge.LEFT, Merge.LEFT, Merge.LEFT, Merge.LEFT],
        first_col_heading=True
    )

    return buy_table_output_for_discord

async def fetch_sell_snapshots(item_name: str):

    """
    Fetches and formats the sell snapshots for a given item.

    Parameters:
    item_name (str): The name of the item to fetch sell snapshots for.

    Returns:
    str: A formatted string representing the sell snapshots for the given item.
    """
    
    db = mariadb.connect(host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME"))
    cursor = db.cursor(buffered=True) 

    query_for_buy_orders = '''
        SELECT listing_id, steam_id, price_keys, price_metal, date, time, is_painted, is_spelled FROM listing_snapshots
        WHERE item_name = ?
        AND event_intent=\'sell\'
        AND event_type = \'listing-update\'
        ORDER BY date DESC, time DESC
        LIMIT 5
        '''

    cursor.execute(query_for_buy_orders, (item_name,))
    # Fetch all rows
    rows = cursor.fetchall()
    ls_rows = [list(tup) for tup in rows]

    sell_table_output_for_discord = table2ascii(
        header=['Listing_ID','SteamID', 'Keys', 'Metal', 'Date', 'Time', 'Painted?', 'Spelled?'],
        body = ls_rows,
        footer=['SELL ORDERS', Merge.LEFT, Merge.LEFT, Merge.LEFT, Merge.LEFT, Merge.LEFT, Merge.LEFT, Merge.LEFT],
        first_col_heading=True
    )

    return sell_table_output_for_discord



@tree.command(name='hello', description='Just says hello')
async def hello(ctx: discord.interactions.Interaction):
    logger.info(f'Hello command executed by {ctx.user.name}')
    await ctx.response.send_message(content=f'Hello, {ctx.user.mention}')


@tree.command(name='fetch_snapshot', description='Fetches the top 5 latest snapshots')
@app_commands.describe(item_name="Name of the item")
async def fetch_last_snapshot(ctx: discord.interactions.Interaction, item_name: str):   
    """
    Fetches the top 5 latest snapshots for a given item.

    Args:
        ctx (discord.interactions.Interaction): The interaction context.
        item_name (str): The name of the item to fetch snapshots for.

    Returns:
        None: If the item name is invalid.
        None: If the snapshots are successfully fetched and sent as follow-up messages.
    """

    matched_item_name = match_item(item_name)
    if matched_item_name is None:
        await ctx.response.send_message(content=f'Invalid item name, please try again.')
        logger.warning(f'Invalid item name provided: {item_name}')    
    else:
        await ctx.response.send_message(content=f'Listings for {matched_item_name[0]}')
        logger.info(f'Fetching listings for {matched_item_name[0]}')
        matched_item_name = matched_item_name[0]
        buy_table_output_for_discord = await fetch_buy_snapshots(matched_item_name)
        await ctx.followup.send(content=f'`{buy_table_output_for_discord}`')

        sell_table_output_for_discord = await fetch_sell_snapshots(matched_item_name)
        await ctx.followup.send(content=f'`{sell_table_output_for_discord}`')

if __name__ == '__main__':
    run_bot()