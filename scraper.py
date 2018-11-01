from bs4 import BeautifulSoup
from bs4.element import NavigableString
from collections import defaultdict
import os
import re
import requests

from enums import Proc


class Scraper:
    primary_stats_attr_regex_tuples = [
        ('armor', re.compile(r'\s*(?P<value>\d+) Armor')),
        ('agi', re.compile(r'\s*\+(?P<value>\d+) Agility')),
        ('int', re.compile(r'\s*\+(?P<value>\d+) Intellect')),
        ('spi', re.compile(r'\s*\+(?P<value>\d+) Spirit')),
        ('sta', re.compile(r'\s*\+(?P<value>\d+) Stamina')),
        ('str', re.compile(r'\s*\+(?P<value>\d+) Strength')),
    ]
    weapon_stats_attr_regex_tuples = [
        ('speed', re.compile(r'\s*Speed (?P<value>[\d.]+)')),
        ('damage_range', re.compile(r'\s*(?P<value_min>\d+) - (?P<value_max>\d+)\s+Damage')),
        ('weapon_type', re.compile(r'\s*(?P<value>Axe|Dagger|Fist Weapon|Mace|Sword)')),
    ]
    secondary_stats_attr_regex_tuples = [
        ('ap', re.compile(r'\s*\+(?P<value>\d+) Attack Power')),
        ('crit', re.compile(r'\s*Improves your chance to get a critical strike by (?P<value>\d+)%')),
        ('hit', re.compile(r'\s*Improves your chance to hit by (?P<value>\d+)%')),
        ('dodge', re.compile(r'\s*Increases your chance to dodge an attack by (?P<value>\d+)%')),
        ('Axe', re.compile(r'\s*Increased Axes \+(?P<value>\d+)')),
        ('Dagger', re.compile(r'\s*Increased Daggers \+(?P<value>\d+)')),
        ('Mace', re.compile(r'\s*Increased Maces \+(?P<value>\d+)')),
        ('Sword', re.compile(r'\s*Increased Swords \+(?P<value>\d+)')),
        ('def', re.compile(r'\s*Increased Defense \+(?P<value>\d+)')),
    ]
    equip_regex = re.compile(r'\s*Equip:')
    set_regex = re.compile(r'\s*\((?P<n_set_pieces_for_bonus>\d+)\) Set:')

    proc_mapping = {
        'Hand of Justice': Proc.HAND_OF_JUSTICE,
    }
    weapon_proc_mapping = {
        'Thrash Blade': {
            'main_hand': Proc.THRASH_BLADE_MAIN,
            'off_hand': Proc.THRASH_BLADE_OFF
        },
        'Ironfoe': {
            'main_hand': Proc.IRONFOE
        },
    }

    def __init__(self, url_prefix, use_cache=True, path_to_cache='cache/items'):
        self.url_prefix = url_prefix
        self.use_cache = use_cache
        self.path_to_cache = path_to_cache

    def scrape_item(self, item_slot, item_id):
        path_to_item = os.path.join(self.path_to_cache, f'{item_id}.html')
        if self.use_cache and os.path.isfile(path_to_item):
            with open(path_to_item, encoding='utf-8') as f:
                text = f.read()
        else:
            response = requests.get(f'{self.url_prefix}{item_id}')
            text = response.text
            if self.use_cache:
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

        if item_slot == 'main_hand' or item_slot == 'off_hand':
            for table in primary_stats_td.find_all('table', recursive=False):
                for td_th in table.find_all(['td', 'th']):
                    for attr, regex in self.weapon_stats_attr_regex_tuples:
                        match = regex.match(td_th.text)
                        if match is not None:
                            attr_key = attr + '_' + item_slot
                            if attr == 'speed':
                                item['stats'][attr_key] = float(match.group('value'))
                            elif attr == 'damage_range':
                                item['stats'][attr_key] = (int(match.group('value_min')), int(match.group('value_max')))
                            elif attr == 'weapon_type':
                                item['stats'][attr_key] = match.group('value')
                            else:
                                raise ValueError(f'Unknown attr {attr}')
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

        item['procs'] = set()
        if (item_slot == 'main_hand' or item_slot == 'off_hand') and item['name'] in self.weapon_proc_mapping:
            item['procs'].add(self.weapon_proc_mapping[item['name']][item_slot])
        elif item['name'] in self.proc_mapping:
            item['procs'].add(self.proc_mapping[item['name']])

        return item


# print(Scraper('https://vanillawowdb.com/?item=', use_cache=False).scrape_item('main_hand', '14555'))
# print(Scraper('https://vanillawowdb.com/?item=', use_cache=False).scrape_item('head', '12640'))
# print(Scraper('https://vanillawowdb.com/?item=', use_cache=False).scrape_item('legs', '15062'))

# print(Scraper('https://classicdb.ch/?item=', use_cache=False).scrape_item('main_hand', '14555'))
# print(Scraper('https://classicdb.ch/?item=', use_cache=False).scrape_item('head', '12640'))
# print(Scraper('https://classicdb.ch/?item=', use_cache=False).scrape_item('legs', '15062'))

# print(Scraper('https://vanillawowdb.com/?item=').scrape_item('main_hand', '17705'))
