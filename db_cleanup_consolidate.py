import mariadb
import datetime

def cleanup_listings():
    # Connect to the MariaDB database
    cnx = mariadb.connect(user='your_username', password='your_password',
                          host='your_host', database='your_database')
    cursor = cnx.cursor()

    # Get the current date and time
    current_datetime = datetime.datetime.now()
    current_date = current_datetime.date()

    # Get the latest listing for each minute of the day
    query = ("SELECT listing_id, MAX(listed_at_datetime) AS latest_timestamp, event_type "
             "FROM your_table "
             "WHERE listed_at_date = %s "
             "GROUP BY listing_id, MINUTE(listed_at_datetime)")
    values = (current_date,)
    cursor.execute(query, values)
    latest_listings = cursor.fetchall()

    # Remove duplicate listings for each minute of the day
    delete_query = ("DELETE FROM your_table "
                    "WHERE listing_id = %s AND listed_at_datetime < %s")
    for listing in latest_listings:
        listing_id, latest_timestamp, event_type = listing
        if event_type == 'listing_delete':
            # Remove the listing if it's a delete event
            cursor.execute(delete_query, (listing_id, latest_timestamp))
        else:
            # Remove duplicate listings for each minute of the day
            cursor.execute(delete_query, (listing_id, latest_timestamp))

    # Commit the changes and close the connection
    cnx.commit()
    cursor.close()
    cnx.close()

# Run the cleanup script
cleanup_listings()