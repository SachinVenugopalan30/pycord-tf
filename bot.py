import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands

load_dotenv()

# Setting up the bot client
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)


def main() -> None:
    bot.run(os.getenv('BOT_TOKEN'))


# # Fetch information from the TF2 server
# async def get_server_info():
#     source = Source(host=os.getenv('SERVER_IP'), port=27015)
#     server_info = await source.get_info()
#     return server_info


# # Check if the server info channel is empty
# # If it is empty, the bot will send a new embed and continue updating that one
# # Else it'll update the pre-existing one
# async def check_empty_channel():
#     channel = bot.get_channel(os.getenv('SERVER_INFO_CHANNEL'))
#     if channel is None:
#         return True
#     return channel


# async def update_server_info(bot, ctx: discord.interactions.Interaction) -> str:
#     if check_empty_channel(bot):
#         embed = discord.Embed(title="Server Info",
#                               color='9b0000')  # Green color
#         server_info = await get_server_info()
#         embed.add_field(name="Server Name", value=server_info.name,
#                         inline=False)  # Not inline
#         embed.add_field(name="Player Count",
#                         value=f'{server_info.players}/{server_info.max_players}', inline=True)  # Inline field
#         embed.add_field(name="Current Map", value=server_info.map,
#                         inline=True)  # Inline field
#         channel = bot.get_channel(os.getenv('SERVER_INFO_CHANNEL'))
#         sent_message = await channel.send(content=None, embed=embed)
#         new_message_id = sent_message.id
#         print(new_message_id)
#         return str(new_message_id)
#     else:
#         return "Channel is not empty, no server info update."


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    try:
        await tree.sync()
    except Exception as e:
        print(f'Error syncing, {e}')


@tree.command(name='hello', description='Just says hello')
async def hello(ctx: discord.interactions.Interaction):
    await ctx.response.send_message(content=f'Hello, {ctx.user.mention}')


# @tree.command(name='plinfo', description='Gives you the current status of the payload server')
# async def plinfo(ctx: discord.interactions.Interaction):

#     if ctx.channel_id != os.getenv('SPECIFIC_CHANNEL_ID'):
#         return

#     embed = discord.Embed(title="Server Info", color='9b0000')  # Green color
#     server_info = await get_server_info()
#     embed.add_field(name="Server Name", value=server_info.name,
#                     inline=False)  # Not inline
#     embed.add_field(name="Player Count",
#                     value=f'{server_info.players}/{server_info.max_players}', inline=True)  # Inline field
#     embed.add_field(name="Current Map", value=server_info.map,
#                     inline=True)  # Inline field
#     await ctx.response.send_message(content=None, embed=embed)

main()
