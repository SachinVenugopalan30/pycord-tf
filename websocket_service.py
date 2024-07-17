import asyncio
import websockets
import json
from datetime import datetime
import sys
import time
import os
from dotenv import load_dotenv
import mariadb
from create_db import table_exist

def is_painted(itemPayload) -> bool:
    paint_cans = [
        5052, 5027, 5031, 5032, 5040, 5033, 5076, 5029, 5077, 5034, 5038, 5051, 5039, 5035, 5037, 5054,
        5030, 5055, 5056, 5036, 5053, 5028, 5063, 5046, 5062, 5064, 5065, 5061, 5060
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


def is_spelled(itemPayload) -> bool:
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


# update the database using listing ID, or add to the database if ID doesn't exist
async def process_events(eventsList) -> bool:
    mydb_connection = mariadb.connect(
    host = 'localhost',
    user = 'listings_worker',
    password = 'helloworld',
    database = 'ListingsDB'
    )
    print(os.getenv("DB_HOST"))
    print(os.getenv("DB_NAME"))
    print(os.getenv("DB_TABLE"))
    mycursor = mydb_connection.cursor()
    tableExist = table_exist(mycursor)
    if tableExist:
        print(tableExist)
        return True
    print("Does not exist")
    return False
    # columns = eventsList[0].keys()
    # try:
    #     # cols_comm_separated = ', '.join(columns)
    #     # binds_comm_separated = ', '.join(['%(' + item + ')' for item in columns])
    #     query = f"INSERT INTO {os.getenv("DB_TABLE")} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    #     values = [tuple(d.values()) for d in eventsList]
    #     mycursor.executemany(query, values)
    #     return(True)
    # except Exception as e:
    #     print(f'Exception occured when trying to insert element {e}')
    #     return(False)
    



async def start_service():
    url = 'wss://ws.backpack.tf/events'
    async with websockets.connect(url, max_size=30*100000) as ws:
        print('Connection established to websocket!')
        while True:
            msg = await ws.recv()
            msg_json = json.loads(msg)
            processed_event_list = []
            listing_delete_count = 0
            listing_update_count = 0
            for event in msg_json:
                if event['event'] == 'listing-update':
                    listing_update_count+=1
                else:
                    listing_delete_count+=1
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
                    list_price_metal = 0
                        
                # creating a dictionary to store the event information later on to the SQL database
                event_info = {
                    'listing_id' : event_payload['id'],
                    'item_name' : event_payload['item']['name'],
                    'date' : listed_at_date,
                    'time' : listed_at_time,
                    'listing_event_type' : event['event'],
                    'listing_intent' : event_payload['intent'], # this is either 'sell', 'buy'
                    'steam_id' : event_payload['steamid'],
                    'list_price_keys' : list_price_keys, # price in keys for the listing
                    'list_price_metal' : list_price_metal, # price in metal for the listing
                    'is_painted' : is_painted(event_payload),
                    'is_spelled' : is_spelled(event_payload),
                }
                # print(event_info)
                processed_event_list.append(event_info)
            # print(processed_event_list)
            res = await process_events(processed_event_list)
            # print(f'Listing update count {listing_update_count}')
            # print(f'Listing delete count {listing_delete_count}')
            # print('-----------')
            break


if __name__ == '__main__':
    load_dotenv()
    try:
        asyncio.run(start_service())
    except KeyboardInterrupt:
        print('Keybord Interrupted, exiting.')
        time.sleep(0.3)
        sys.exit(1)