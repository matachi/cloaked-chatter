README
======

Setup
-----

1. Install pip `sudo apt-get install python3-pip`

2. Install [PRAW](https://github.com/praw-dev/praw) `sudo pip-3.2 install praw`

3. Install [BeatuifulSoup](http://www.crummy.com/software/BeautifulSoup/) `sudo pip-3.2 install beautifulsoup4`

4. Install SQLite3 `sudo apt-get install sqlite3`

5. Create an SQLite database and a table Links with:

    1. `sqlite3 database.sqlite`

    2. Create table Links:

            CREATE TABLE Links (
                url VARCHAR(50) PRIMARY KEY,
                time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

    3. Exit with `.exit`

6. Update `bot.cfg` with your Reddit username and password
