import asyncio
import websockets
import json
from datetime import datetime
import sys
import time
import os
from dotenv import load_dotenv
import mariadb

class WebSocketService:
    def __init__(self):
        load_dotenv()
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_user = os.getenv('DB_USER', 'root')
        self.db_password = os.getenv('DB_PASSWORD', 'password')
        self.db_name = os.getenv('DB_NAME')
        self.db_table = os.getenv('DB_TABLE')
        self.socket_url = os.getenv('SOCKET_URL')
    
    
    def is_painted(self, itemPayload) -> bool:
        '''
        Creates a function to track painted items, may not be relevant
        '''
        paint_cans = [
            5052, 5027, 5031, 5032, 5040, 5033, 5076, 5029, 5077, 5034, 5038, 5051, 5039, 5035, 
            5037, 5054, 5030, 5055, 5056, 5036, 5053, 5028, 5063, 5046, 5062, 5064, 5065, 5061, 5060
        ]
        
        if itemPayload['item']['defindex'] in paint_cans:
            return False
        try:
            itemAttributes = itemPayload['item']['attributes']
            try:
                if itemAttributes['defindex'] == 142:
                    return True
            except TypeError:
                # comes in here for items like the Duck Journal
                print(itemAttributes)
                return False
        except KeyError:
            return False
        print("No paint found")
        return False


    def is_spelled(self, itemPayload) -> bool:
        '''
        Creates a flag for spelled items for future tracking
        '''
        try:
            itemAttributes = itemPayload['item']['attributes']
            try:
                if itemAttributes['defindex'] in [1004, 1005, 1006, 1007, 1008, 1009]:
                    return True
            except TypeError:
                # comes in here for items like the Duck Journal
                return False
        except KeyError:
            return False
        print("No Spell found")
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
            print(f'Exception occured when trying to insert element {e}')
            return(False)
        

    async def main_service(self):
        '''
        Driver function to start the everything, connect to the websocket, process events, and dump events to the database
        '''
        url = self.socket_url
        async with websockets.connect(url, max_size=30*100000) as ws:
            print('Connection established to websocket!')
            while True:
                try:
                    msg = await ws.recv()
                    msg_json = json.loads(msg)
                    processed_event_list = self.process_events(msg_json)
                    res = await self.add_to_database(processed_event_list)
                    if res:
                        print(f"Sucessfully dumped {len(processed_event_list)} events into database")
                    else:
                        print("Failed to input into database")
                except websockets.exceptions.ConnectionClosedError:
                    print("Connection to websocket closed, restarting...")
                    time.sleep(0.2)
                    continue


if __name__ == '__main__':
    try:
        ws_service = WebSocketService()
        asyncio.run(ws_service.main_service())
    except KeyboardInterrupt:
        print('Keybord Interrupted, exiting.')
        time.sleep(0.3)
        sys.exit(1)