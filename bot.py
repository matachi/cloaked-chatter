#!/usr/bin/python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Author: Daniel Jonsson
"""Script that posts a hot tech news item to /r/technology on Reddit.
"""

import os
import sys
import re
import urllib.request
from datetime import datetime
import traceback
import configparser
import warnings
import logging
import logging.config
import yaml

import praw
from bs4 import BeautifulSoup
import sqlite3 as sqlite

DATABASE = 'database.sqlite'
LOGGER = 'cloaked_chatter'

def main():
    path = os.path.dirname(os.path.realpath(__file__))

    config = configparser.ConfigParser()
    config.read('{0}/configs/bot.ini'.format(path))
    warnings.simplefilter("ignore", category=DeprecationWarning)
    reddit = praw.Reddit(user_agent=config['Reddit']['useragent'])
    reddit.login(config['Reddit']['username'], config['Reddit']['password'])
    warnings.simplefilter("always")

    dry_run = config['Bot'].getboolean('dry-run')

    loggingConf = open('{0}/configs/logging.yml'.format(path), 'r')
    logging.config.dictConfig(yaml.load(loggingConf))
    loggingConf.close()
    logger = logging.getLogger(LOGGER)

    logger.info('Program started')

    if dry_run:
        logger.info('Running in dry run mode. Nothing will be commited')

    news_items = get_news_items(int(config['Bot']['level']))
    for item in news_items:
        url = item[0]
        title = item[1]
        degree = item[2]
        if not has_link_been_posted(url):
            add_link_as_posted(url, dry_run)
            if not post_link(reddit, get_redirect_url(url), title, dry_run):
                continue
            break

    logger.info('Program done')

def get_redirect_url(url):
    """Get the URL that the given URL points to.

    Args:
        url: The start URL.

    Returns:
        The appointed URL.
    """
    warnings.simplefilter("ignore", category=ResourceWarning)
    res = urllib.request.urlopen(url)
    warnings.simplefilter("always")
    return res.geturl()

def post_link(reddit, url, title, dry_run):
    """Post a link to reddit.

    Args:
        reddit: A Reddit object.
        url: URL to submit.
        title: Title of the link.
        dry_run: If changes should be commited.
    """
    logger = logging.getLogger(LOGGER)
    posted = False
    try:
        if not dry_run:
            reddit.submit('technology', title, url=url)
            pass
        posted = True
        logger.info('Successfully posted `{0}` `{1}`'.format(title, url))
    except praw.errors.AlreadySubmitted as e:
        logger.info('Already been posted `{0}` `{1}`'.format(title, url))
    except:
        logger.exception('Crashed posting `{0}` `{1}`'.format(title, url))
        sys.exit(0)
    return posted

def get_news_items(level):
    """Get news items.

    Args:
        level: Specify the freshness of the news items. See bot.ini.

    Returns:
        A list containing tupels of url, title and degree.
    """
    levels = {1: 'hour', 2: '6hours', 3: '', 4: '3days', 5: 'week'}
    warnings.simplefilter("ignore", category=ResourceWarning)
    page = urllib.request.urlopen('http://techhe.at/{0}' \
                                  .format(levels.get(level)))
    warnings.simplefilter("always")
    soup = BeautifulSoup(page)
    page.close()
    news_items = []
    # Compile regex for getting the degree.
    degree_regex = re.compile('^\s*([.\d]+).*')
    # Go through all news items.
    for entry in soup.find_all("div", class_="item"):
        # Find the node containing the url and title.
        item_content_link_node = entry.div.find('div', class_='item_content') \
                                 .h3.a
        if not valid_site(entry):
            continue
        url = "http://techhe.at" + item_content_link_node["href"]
        # Remove \t and trim the string.
        title = item_content_link_node.text.replace('\t', '').strip()
        # If it doesn't have a title, continue to the next entry.
        if not valid_title(title):
            continue
        # Get the next div where the degree is. Grab the degree with regex.
        degree = re.match(degree_regex,
                          entry.div.next_sibling.next_sibling.h2.text).group(1)
        news_items.append((url, title, degree))
    return news_items

def valid_site(item_entry):
    non_valid_sites = ('Mashable', 'Cnet', 'Gizmodo')
    return not get_site(item_entry) in non_valid_sites

def valid_title(title):
    """Check if it's a valid news item based on its title.

    Args:
        title: The title of the news item.

    Returns:
        A boolean value.
    """
    valid = True
    if re.search('^The Engadget Show', title) or \
       title == 'Titel for this article is currently missing':
        valid = False
    return valid

def get_site(item_entry):
    return item_entry.find('div', class_='item_meta').a.next_sibling \
           .next_sibling.span.text.strip()

def has_link_been_posted(url):
    """Check if the link has already been posted.

    Args:
        url: The URL to be checked.

    Returns:
        A boolean value.
    """
    path = os.path.dirname(os.path.realpath(__file__))
    con = sqlite.connect('{0}/{1}'.format(path, DATABASE))
    with con:
        cur = con.cursor()
        sql = "SELECT COUNT() FROM Links WHERE url=?"
        try:
            cur.execute(sql, [url])
        except sqlite.OperationalError:
            create_table()
            cur.execute(sql, [url])
        con.commit()
        been_posted = cur.fetchone()[0] > 0
        return been_posted

def create_table():
    path = os.path.dirname(os.path.realpath(__file__))
    con = sqlite.connect('{0}/{1}'.format(path, DATABASE))
    cur = con.cursor()
    sql = "CREATE TABLE Links ( \
               url VARCHAR(50) PRIMARY KEY, \
               time TIMESTAMP DEFAULT CURRENT_TIMESTAMP \
           )"
    cur.execute(sql)
    con.commit()
    logger = logging.getLogger(LOGGER)
    logger.info('Created table Links')

def add_link_as_posted(url, dry_run):
    """Store that the link has been posted.

    Args:
        url: The URL to be stored.
        dry_run: If changes should be commited.

    Returns:
        A boolean value.
    """
    path = os.path.dirname(os.path.realpath(__file__))
    con = sqlite.connect('{0}/{1}'.format(path, DATABASE))
    with con:
        sql = "INSERT INTO Links (url) VALUES (?)"
        if not dry_run:
            cur = con.cursor()
            cur.execute(sql, [url])
            con.commit()
        logger = logging.getLogger(LOGGER)
        logger.info(sql[:-2] + "'" + url + "')")

if __name__ == "__main__":
    main()
