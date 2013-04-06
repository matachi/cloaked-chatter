# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Author: Daniel Jonsson

import urllib.request
import re
import warnings

from bs4 import BeautifulSoup

class News():
    """This class handles getting the news items.
    """

    def get_news_items(self, level):
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
            item_content_link_node = entry.div \
                                     .find('div', class_='item_content').h3.a
            if not self._valid_site(entry):
                continue
            url = "http://techhe.at" + item_content_link_node["href"]
            # Remove \t and trim the string.
            title = item_content_link_node.text.replace('\t', '').strip()
            # If it doesn't have a title, continue to the next entry.
            if not self._valid_title(title):
                continue
            # Get the next div where the degree is. Grab the degree with regex.
            degree = re.match(degree_regex, entry.div.next_sibling \
                                            .next_sibling.h2.text).group(1)
            news_items.append((url, title, degree))
        return news_items

    def _valid_site(self, item_entry):
        non_valid_sites = ('Mashable', 'Cnet', 'Gizmodo')
        return not self._get_site(item_entry) in non_valid_sites

    def _valid_title(self, title):
        """Check if it's a valid news item based on its title.

        Args:
            title: The title of the news item.

        Returns:
            A boolean value.
        """
        valid = True
        if re.search('^The Engadget Show', title) or \
           re.search('^Engadget Podcast \d{2,3}: ', title) or \
           re.search('^Distro Issue \d{2,3}: ', title) or \
           re.search('^This Week On The TechCrunch Gadgets Podcast: ', title) or \
           re.search("^Editor's Letter: ", title) or \
           re.search('^Gillmor Gang ', title) or \
           re.search('^Poll Technica: ', title) or \
           re.search('^The Daily Roundup for', title) or \
           re.search('^Backed Or Whacked: ', title) or \
           re.search('^Ask Engadget: ', title) or \
           re.search('^From idea to science: ', title) or \
           re.search('^CrunchWeek: ', title) or \
           re.search('^The Weekly Good: ', title) or \
           re.search('^Engadget Giveaway: ', title) or \
           title == 'Titel for this article is currently missing':
            valid = False
        return valid

    def _get_site(self, item_entry):
        return item_entry.find('div', class_='item_meta').a.next_sibling \
               .next_sibling.span.text.strip()
