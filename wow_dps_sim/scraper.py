from bs4 import BeautifulSoup
from bs4.element import NavigableString
from collections import defaultdict
import os
import requests

from wow_dps_sim.helpers import from_module_import_x
from wow_dps_sim.main_config import EXPANSION_MODULE
ScraperConfig = from_module_import_x(EXPANSION_MODULE + '.scraper_config', 'ScraperConfig')


class Scraper:
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
            for attr, regex in ScraperConfig.primary_stats_attr_regex_tuples:
                match = regex.search(navigable_string)
                if match is not None:
                    item['stats'][attr] = int(match.group('value'))
                    break

        if item_slot == 'main_hand' or item_slot == 'off_hand':
            for table in primary_stats_td.find_all('table', recursive=False):
                for td_th in table.find_all(['td', 'th']):
                    for attr, regex in ScraperConfig.weapon_stats_attr_regex_tuples:
                        match = regex.search(td_th.text)
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
            if ScraperConfig.equip_regex.match(span.text) is not None:
                for attr, regex in ScraperConfig.secondary_stats_attr_regex_tuples:
                    match = regex.search(span.text)
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
                                set_regex_match = ScraperConfig.set_regex.match(span_grandchild.text)
                                if set_regex_match is not None:
                                    a = span_grandchild.find('a')
                                    for attr, regex in ScraperConfig.primary_stats_attr_regex_tuples + ScraperConfig.secondary_stats_attr_regex_tuples:
                                        match = regex.search(a.text)
                                        if match is not None:
                                            item['set']['bonuses'][int(set_regex_match.group('n_set_pieces_for_bonus'))] = (attr, int(match.group('value')))
                                            break

        item['procs'] = set()
        if (item_slot == 'main_hand' or item_slot == 'off_hand') and item['name'] in ScraperConfig.weapon_proc_mapping:
            item['procs'].add(ScraperConfig.weapon_proc_mapping[item['name']][item_slot])
        elif item['name'] in ScraperConfig.proc_mapping:
            item['procs'].add(ScraperConfig.proc_mapping[item['name']])

        item['on_use_effects'] = set()
        if item['name'] in ScraperConfig.on_use_effect_mapping:
            item['on_use_effects'].add(ScraperConfig.on_use_effect_mapping[item['name']])

        return item
