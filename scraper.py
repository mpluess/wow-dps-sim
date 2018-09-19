from bs4 import BeautifulSoup
from bs4.element import NavigableString
from collections import defaultdict
import os
import re
import requests


class Scraper:
    def __init__(self, use_cache=True, path_to_cache='cache/items'):
        self.use_cache = use_cache
        self.path_to_cache = path_to_cache

        self.primary_stats_attr_regex_tuples = [
            ('armor', re.compile(r'\s*(?P<value>\d+) Armor')),
            ('agi', re.compile(r'\s*\+(?P<value>\d+) Agility')),
            ('int', re.compile(r'\s*\+(?P<value>\d+) Intellect')),
            ('spi', re.compile(r'\s*\+(?P<value>\d+) Spirit')),
            ('sta', re.compile(r'\s*\+(?P<value>\d+) Stamina')),
            ('str', re.compile(r'\s*\+(?P<value>\d+) Strength')),
        ]
        self.secondary_stats_attr_regex_tuples = [
            ('ap', re.compile(r'\s*\+(?P<value>\d+) Attack Power')),
            ('crit', re.compile(r'\s*Improves your chance to get a critical strike by (?P<value>\d+)%')),
            ('hit', re.compile(r'\s*Improves your chance to hit by (?P<value>\d+)%')),
            ('dodge', re.compile(r'\s*Increases your chance to dodge an attack by (?P<value>\d+)%')),
            ('axes', re.compile(r'\s*Increased Axes \+(?P<value>\d+)')),
            ('daggers', re.compile(r'\s*Increased Daggers \+(?P<value>\d+)')),
            ('swords', re.compile(r'\s*Increased Swords \+(?P<value>\d+)')),
            ('def', re.compile(r'\s*Increased Defense \+(?P<value>\d+)')),
        ]
        self.equip_regex = re.compile(r'\s*Equip:')
        self.set_regex = re.compile(r'\s*\((?P<n_set_pieces_for_bonus>\d+)\) Set:')

    def scrape_item(self, item_id):
        path_to_item = os.path.join(self.path_to_cache, f'{item_id}.html')
        if self.use_cache and os.path.isfile(path_to_item):
            with open(path_to_item, encoding='utf-8') as f:
                text = f.read()
        else:
            response = requests.get(f'https://vanillawowdb.com/?item={item_id}')
            text = response.text
            with open(path_to_item, 'w', encoding='utf-8') as f:
                f.write(text)

        document = BeautifulSoup(text, 'html.parser')
        tooltip = document.find('div', class_='tooltip')

        stats_tables = tooltip.find('table').find('td').find_all('table', recursive=False)
        primary_stats_td = stats_tables[0].find('td')
        secondary_stats_td = stats_tables[1].find('td')

        item = dict()
        item['name'] = primary_stats_td.find('b').text
        item['stats'] = defaultdict(int)
        item['set'] = dict()
        item['set']['name'] = None
        item['set']['bonuses'] = dict()

        for navigable_string in [el for el in primary_stats_td.children if isinstance(el, NavigableString)]:
            for attr, regex in self.primary_stats_attr_regex_tuples:
                match = regex.match(navigable_string)
                if match is not None:
                    item['stats'][attr] = int(match.group('value'))
                    break

        for span in secondary_stats_td.find_all('span', recursive=False):
            if self.equip_regex.match(span.text) is not None:
                a = span.find('a')
                for attr, regex in self.secondary_stats_attr_regex_tuples:
                    match = regex.match(a.text)
                    if match is not None:
                        item['stats'][attr] = int(match.group('value'))
                        break
            else:
                a = span.find('a')
                if a is not None and 'itemset' in a['href']:
                    item['set']['name'] = a.text
                else:
                    span_child = span.find('span')
                    if span_child is not None:
                        span_grandchildren = span_child.find_all('span')
                        if len(span_grandchildren) > 0:
                            for span_grandchild in span_grandchildren:
                                set_regex_match = self.set_regex.match(span_grandchild.text)
                                if set_regex_match is not None:
                                    a = span_grandchild.find('a')
                                    for attr, regex in self.primary_stats_attr_regex_tuples + self.secondary_stats_attr_regex_tuples:
                                        match = regex.match(a.text)
                                        if match is not None:
                                            item['set']['bonuses'][int(set_regex_match.group('n_set_pieces_for_bonus'))] = (attr, int(match.group('value')))
                                            break

        return item


print(Scraper().scrape_item('15062'))
