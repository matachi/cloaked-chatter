# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Author: Daniel Jonsson

import logging
import sqlite3 as sqlite

LOGGER = 'cloaked_chatter'

class History():
    """This class keeps track of posted links.
    """

    def __init__(self, database_path):
        """Create a history class.

        Args:
            database_path: Path to the database file.
        """
        self._database_path = database_path

    def has_link_been_posted(self, url):
        """Check if the link has already been posted.

        Args:
            url: The URL to be checked.

        Returns:
            A boolean value.
        """
        con = sqlite.connect('{0}'.format(self._database_path))
        with con:
            cur = con.cursor()
            sql = 'SELECT COUNT() FROM Links WHERE url=?'
            try:
                cur.execute(sql, [url])
            except sqlite.OperationalError:
                self._create_table()
                cur.execute(sql, [url])
            con.commit()
            been_posted = cur.fetchone()[0] > 0
            return been_posted

    def _create_table(self):
        """Create the database table Links.
        """
        con = sqlite.connect('{0}'.format(self._database_path))
        cur = con.cursor()
        sql = 'CREATE TABLE Links ( \
                   url VARCHAR(50) PRIMARY KEY, \
                   time TIMESTAMP DEFAULT CURRENT_TIMESTAMP \
               )'
        cur.execute(sql)
        con.commit()
        logger = logging.getLogger(LOGGER)
        logger.info('Created table Links')

    def add_link_as_posted(self, url, dry_run):
        """Store that the link has been posted.

        Args:
            url: The URL to be stored.
            dry_run: If changes should be commited.

        Returns:
            A boolean value.
        """
        con = sqlite.connect('{0}'.format(self._database_path))
        with con:
            sql = 'INSERT INTO Links (url) VALUES (?)'
            if not dry_run:
                cur = con.cursor()
                cur.execute(sql, [url])
                con.commit()
            logger = logging.getLogger(LOGGER)
            logger.info(sql[:-2] + "'" + url + "')")
