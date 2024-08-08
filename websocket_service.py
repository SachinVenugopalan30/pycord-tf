import asyncio
import websockets
import json
from datetime import datetime
import sys
import time
import os
from dotenv import load_dotenv
import mariadb
import discord
import aiohttp
from discord import Webhook

class WebSocketService:
    def __init__(self):
        load_dotenv()
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_user = os.getenv('DB_USER', 'root')
        self.db_password = os.getenv('DB_PASSWORD', 'password')
        self.db_name = os.getenv('DB_NAME')
        self.db_table = os.getenv('DB_TABLE')
        self.socket_url = os.getenv('SOCKET_URL')
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    
    async def webhook_service(self, webhook_type, webhook_title, webhook_message) -> None:
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(self.webhook_url, session=session)
            if webhook_type == 'info':
                colour = 0x0187b7
            elif webhook_type == 'error':
                colour = 0xb70104
            else:
                colour = 0xf9ff00
            embed = discord.Embed(title=webhook_title, description=webhook_message, colour=colour)

            if webhook_type == 'error':
                await webhook.send(content='<@242688398475657216>', embed=embed, username='Websocket Service')
                return
            await webhook.send(embed=embed, username='Websocket Service')


    def killstreak_effects(self, itemPayload) -> None:
        '''
        For future use
        '''
        if 'Professional Kilstreak' in itemPayload['item']['name']:
            print(itemPayload['item']['killstreaker']['name'])
            print(itemPayload['item']['sheen']['name'])
            
        elif 'Specialized Killstreak' in itemPayload['item']['name']:
            print(itemPayload['item']['sheen']['name'])
    
    
    def is_painted(self, itemPayload) -> bool:
        '''
        Creates a function to track painted items, may not be relevant
        '''
        paint_cans = [
            5052, 5027, 5031, 5032, 5040, 5033, 5076, 5029, 5077, 5034, 5038, 5051, 5039, 5035, 
            5037, 5054, 5030, 5055, 5056, 5036, 5053, 5028, 5063, 5046, 5062, 5064, 5065, 5061, 5060
        ]
        if int(itemPayload['item']['defindex']) in paint_cans:
            return False
        try:
            if itemPayload['item']['paint']:
                return True
        except KeyError:
            return False


    def is_spelled(self, itemPayload) -> bool:
        '''
        Creates a flag for spelled items for future tracking
        '''
        try:
            if itemPayload['item']['spells']:
                return True
        except KeyError:
            return False


    def process_events(self, msg_json) -> list:
        '''
        Function is used to taken in only the relevant information from the websocket events
        It also adds some extra information for future use
        '''
        processed_events_list = []
        for event in msg_json:
            # listing data is stored within the 'payload' key of each event
            event_payload = event['payload']
            
            # creating some date and time stamps for easier tracking and processing
            listed_at_datetime = datetime.now()
            listed_at_time = listed_at_datetime.strftime('%H:%M:%S')
            listed_at_date = listed_at_datetime.date()
            
            # sometimes lower value items won't have a key price associated to them, so we need to handle that gracefully
            try:
                list_price_keys = event_payload['currencies']['keys']
            except KeyError:
                list_price_keys = 0
            # similarly, if there's no metal value, we need to handle that too
            try:
                list_price_metal = event_payload['currencies']['metal']
            except KeyError:
                list_price_metal = float(0)
                    
            # creating a dictionary to store the event information later on to the SQL database
            event_info = {
                'listing_id' : event_payload['id'],
                'item_name' : event_payload['item']['name'],
                'date' : listed_at_date,
                'time' : listed_at_time,
                'event_type' : event['event'],
                'event_intent' : event_payload['intent'], # this is either 'sell', 'buy'
                'steam_id' : event_payload['steamid'],
                'price_keys' : list_price_keys, # price in keys for the listing
                'price_metal' : float(list_price_metal), # price in metal for the listing
                'is_painted' : int(self.is_painted(event_payload)),
                'is_spelled' : int(self.is_spelled(event_payload)),
            }
            processed_events_list.append(event_info)
        return processed_events_list


    async def add_to_database(self, eventsList) -> bool:
        '''
        Function to add processed events to the database
        '''
        mydb_connection = mariadb.connect(
        host = self.db_host,
        user = self.db_user,
        password = self.db_password,
        database = self.db_name
        )
        mycursor = mydb_connection.cursor()
        mycursor.execute(f"USE {self.db_name};")
        columns = eventsList[0].keys()
        try:
            query = f"INSERT INTO {self.db_table} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
            values = [tuple(d.values()) for d in eventsList]
            mycursor.executemany(query, values)
            mydb_connection.commit()
            return(True)
        except Exception as e:
            await self.webhook_service("error", "Error!!", f"Error dumping into database! {e}")
            print(f'Exception occured when trying to insert element {e}')
            return(False)
        

    async def main_service(self):
        '''
        Driver function to start the everything, connect to the websocket, process events, and dump events to the database
        '''
        url = self.socket_url
        while True:
            try:
                async with websockets.connect(url, max_size=30*100000) as ws:
                    await self.webhook_service("info", "Information", "Connection established with the websocket!")
                    print('Connection established to websocket!')
                    while True:
                        msg = await ws.recv()
                        msg_json = json.loads(msg)
                        processed_event_list = self.process_events(msg_json)
                        res = await self.add_to_database(processed_event_list)
                        if res:
                            print(f"Successfully logged {len(processed_event_list)} events into database")
                        else:
                            print("Failed to input into database")
            except websockets.exceptions.ConnectionClosedError:
                await self.webhook_service("default", "Information", "Connection closed, restarting...")
                print("Connection to websocket closed, restarting...")
                continue


if __name__ == '__main__':
    try:
        ws_service = WebSocketService()
        asyncio.run(ws_service.main_service())
    except KeyboardInterrupt:
        print('Keybord Interrupted, exiting.')
        time.sleep(0.3)
        sys.exit(1)