#!/usr/bin/python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Author: Daniel Jonsson
"""Script that posts a hot tech news item to /r/technology on Reddit.
"""

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
import sqlite3 as lite

DATABASE = 'database.sqlite'
LOGGER = 'cloaked_chatter'

def main():
    config = configparser.ConfigParser()
    config.read('configs/bot.ini')
    warnings.simplefilter("ignore", category=DeprecationWarning)
    reddit = praw.Reddit(user_agent=config['Reddit']['useragent'])
    reddit.login(config['Reddit']['username'], config['Reddit']['password'])
    warnings.simplefilter("always")

    loggingConf = open('configs/logging.yml', 'r')
    logging.config.dictConfig(yaml.load(loggingConf))
    loggingConf.close()
    logger = logging.getLogger(LOGGER)

    logger.info('Program started')

    news_items = get_news_items()
    for item in news_items:
        url = item[0]
        title = item[1]
        degree = item[2]
        if not has_link_been_posted(url):
            post_link(reddit, get_redirect_url(url), title)
            add_link_as_posted(url)
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

def post_link(reddit, url, title):
    """Post a link to reddit.

    Args:
        reddit: A Reddit object.
        url: URL to submit.
        title: Title of the link.
    """
    logger = logging.getLogger(LOGGER)
    try:
        reddit.submit('technology', title, url=url)
        logger.info('Successfully posted `{0}` `{1}`'.format(title, url))
    except:
        logger.exception('Crashed posting `{0}` `{1}`'.format(title, url))
        sys.exit(0)

def get_news_items():
    """Get news items.

    Returns:
        A list containing tupels of url, title and degree.
    """
    warnings.simplefilter("ignore", category=ResourceWarning)
    page = urllib.request.urlopen('http://techhe.at/hour')
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
        if title == 'Titel for this article is currently missing':
            continue
        # Get the next div where the degree is. Grab the degree with regex.
        degree = re.match(degree_regex,
                          entry.div.next_sibling.next_sibling.h2.text).group(1)
        news_items.append((url, title, degree))
    return news_items

def valid_site(item_entry):
    return get_site(item_entry) != 'Mashable'

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
    con = lite.connect(DATABASE)
    with con:
        cur = con.cursor()
        sql = "SELECT COUNT() FROM Links WHERE url=?"
        cur.execute(sql, [url])
        con.commit()
        been_posted = cur.fetchone()[0] > 0
        return been_posted

def add_link_as_posted(url):
    """Store that the link has been posted.

    Args:
        url: The URL to be stored.

    Returns:
        A boolean value.
    """
    con = lite.connect(DATABASE)
    with con:
        cur = con.cursor()
        sql = "INSERT INTO Links (url) VALUES (?)"
        cur.execute(sql, [url])
        con.commit()
        logger = logging.getLogger(LOGGER)
        logger.info(sql[:-2] + "'" + url + "')")

if __name__ == "__main__":
    main()
