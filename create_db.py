import os
from dotenv import load_dotenv
import mariadb
import sys

def db_exist(mycursor) -> bool:
    mycursor.execute("SHOW DATABASES")
    for x in mycursor:
        if os.getenv("DB_NAME") in x:
            return True
    return False

def table_exist(mycursor) -> bool:
    sql = "SHOW TABLES FROM " + os.getenv("DB_NAME") + ";"
    mycursor.execute(sql)
    for x in mycursor:
        if os.getenv("DB_TABLE") in x:
            return True
    return False


def db_create(mycursor) -> bool:
    check_db_exist = db_exist(mycursor)
    if not check_db_exist:
        sql = "CREATE DATABASE " + os.getenv("DB_NAME")
        try:
            mycursor.execute(sql)
            print("Created Database")
        except Exception as e:
            print(f"Error creating database, error was {e}")
            return False
        
    if not table_exist(mycursor):
        db = mariadb.connect(host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME"))
        cursor = db.cursor(buffered=True)
        # Creating the actual table that will be used to store listings as they come in
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS listing_snapshots (
            listing_id VARCHAR(300) NOT NULL,
            item_name VARCHAR(300) NOT NULL,
            date DATE NOT NULL,
            time TIME NOT NULL,
            event_type VARCHAR(50) NOT NULL,
            event_intent VARCHAR(10) NOT NULL,
            steam_id BIGINT NOT NULL,
            price_keys INT NOT NULL,
            price_metal FLOAT NOT NULL,
            is_painted TINYINT(1),
            is_spelled TINYINT(1)
        );
        '''
        try:
            cursor.execute(create_table_query)
            print("Created Table")
        except Exception as e:
            print(f"Error creating table, error was {e}")
            return False
        return True

        
if __name__ == "__main__":
    load_dotenv()

    mydb = mariadb.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
    )

    mycursor = mydb.cursor(buffered=True)
    
    res = db_create(mycursor)
    
    print(res)
    sys.exit(1)