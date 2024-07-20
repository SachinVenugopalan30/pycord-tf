
# PyCord-TF

A Discord bot built to easily fetch listings for certain items and check the buy orders and sell orders as seen on backpack.tf as they progress over the last year.

## Features (Stuff is bound to be removed and added)

- Automatically fetches listings from [backpack.tf's websocket](https://next.backpack.tf/developer/websocket).
- Uses [MariaDB](https://mariadb.org/) to store the listings to a MySQL Database.
- When a request is made to an item, the bot should fetch all the listings for that item for the last year, average out the prices to a day level, create a graph to show the trend of buy orders and sell orders and send a picture of the graph to the user via DM (may change it to public chat but we'll see that when we get there)
- Automatic cleanup of data from the database to delete year-old data for efficient storage.
- More to come, I hope.

## Prerequisites
-  Python Version 3.10 or above is required
- Python-Poetry is used for dependancy and environment management, please see how to install it for your system at their [website](https://python-poetry.org/docs/#installation).
- Install MariaDB - Installation may depend on which Operating System you use.
    - I currently built and tested this project on Ubuntu, and I installed MariabDB following this [tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-mariadb-on-ubuntu-20-04).
    - For Windows users, [click here](https://mariadb.com/kb/en/installing-mariadb-msi-packages-on-windows/)
    - For MacOS users, [click here](https://mariadb.com/kb/en/installing-mariadb-on-macos-using-homebrew/)
- Create a Discord server for yourself (duh), or use the one you already own!
- Obtaining a Bot Token for Discord: Follow the instructions [here](https://discordpy.readthedocs.io/en/stable/discord.html) to create a bot and add it to your server.

## When installing the dependancies on poetry, you might encounter some errors. Try installing the following packages manually:

- `sudo apt-get install libsqlite3-dev`
- `sudo apt-get install python3.x-dev` (depends on your Python version, for example if you are using Python 3.10 then use `python3.10-dev`)
- `sudo apt install libmariadb3 libmariadb-dev`
