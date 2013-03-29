README
======

About
-----

This program posts links to news items on /r/technology on Reddit. The links
are gathered from [TechHeat](http://techhe.at/). The project is licensed under
Mozilla Public License 2.0.

Author: Daniel 'MaTachi' Jonsson, [http://danielj.se](http://danielj.se)

Setup
-----

1. Install pip `sudo apt-get install python3-pip`

2. Install [PRAW](https://github.com/praw-dev/praw) `sudo pip-3.2 install praw`

3. Install [BeatuifulSoup](http://www.crummy.com/software/BeautifulSoup/) `sudo pip-3.2 install beautifulsoup4`

4. Install SQLite3 `sudo apt-get install sqlite3`

5. Install YAML `sudo apt-get install python3-yaml`

6. Configure with your Reddit username and password:

    1. Make a copy of bot-sample.ini named bot.ini:
       `cd configs ; cp bot-sample.ini bot.ini`

    2. Add your Reddit username and password to bot.ini: `vim bot.ini`

Launching
---------

1. Add permission to launch the program `chmod u+x bot.py`.

2. Launch with `./bot.py` or `python3 bot.py`.

Note, the log file will be created in the directory that the program is
launched from.

Schedule automatic posting
--------------------------

Automatic posting can be achieved by schedule launching bot.py with cron. Add a
cronjob with `crontab -e`. List cronjobs with `crontab -l`.

Cronjob to launch the script every hour:

    0 * * * * cd /home/pi/cloaked-chatter && ./bot.py

Or to launch it every second hour:

    0 1-23/2 * * * cd /home/pi/cloaked-chatter && ./bot.py

As the Linux username `pi` suggests, in this case it's running on a Raspberry
Pi with Raspbian "wheezy". A Raspberry Pi is perfect for this type of project
considering its low energy consumption and that very little computing power is
needed.

