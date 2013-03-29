# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Author: Daniel Jonsson

import logging
import warnings

import praw

LOGGER = 'cloaked_chatter'

class Reddit():
    """Handles communication with Reddit.
    """

    def __init__(self, username, password, user_agent, dry_run=False):
        """Create a Reddit class.

        Args:
            username: The Reddit username.
            password: The account's password.
            user_agent: The user agent of the the program.
            dry_run: If changes shouldn't be commited.
        """
        warnings.simplefilter('ignore', category=DeprecationWarning)
        self._reddit = praw.Reddit(user_agent=user_agent)
        self._reddit.login(username, password)
        warnings.simplefilter('always')
        self._dry_run = dry_run

    def post_link(self, url, title):
        """Post a link to reddit.

        Args:
            reddit: A Reddit object.
            url: URL to submit.
            title: Title of the link.
        """
        logger = logging.getLogger(LOGGER)
        posted = False
        try:
            if not self._dry_run:
                self._reddit.submit('technology', title, url=url)
                pass
            posted = True
            logger.info('Successfully posted `{0}` `{1}`'.format(title, url))
        except praw.errors.AlreadySubmitted as e:
            logger.info('Already been posted `{0}` `{1}`'.format(title, url))
        except:
            logger.exception('Crashed posting `{0}` `{1}`'.format(title, url))
            sys.exit(0)
        return posted
