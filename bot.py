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
import configparser
import warnings
import logging
import logging.config
import yaml

from history import History
from news import News
from reddit import Reddit

DATABASE = 'database.sqlite'
LOGGER = 'cloaked_chatter'

def main():
    path = os.path.dirname(os.path.realpath(__file__))

    loggingConf = open('{0}/configs/logging.yml'.format(path), 'r')
    logging.config.dictConfig(yaml.load(loggingConf))
    loggingConf.close()
    logger = logging.getLogger(LOGGER)

    logger.info('Program started')

    config = configparser.ConfigParser()
    config.read('{0}/configs/bot.ini'.format(path))

    username = config['Reddit']['username']
    password = config['Reddit']['password']
    user_agent = config['Reddit']['user-agent']
    dry_run = config['Bot'].getboolean('dry-run')

    if dry_run:
        logger.info('Running in dry run mode. Nothing will be commited')

    reddit = Reddit(username, password, user_agent, dry_run)
    history = History('{0}/{1}'.format(path, DATABASE))
    news = News()
    news_items = news.get_news_items(int(config['Bot']['level']))
    for item in news_items:
        url = item[0]
        title = item[1]
        degree = item[2]
        if not history.has_link_been_posted(url):
            history.add_link_as_posted(url, dry_run)
            if not reddit.post_link(get_redirect_url(url), title):
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

if __name__ == "__main__":
    main()
