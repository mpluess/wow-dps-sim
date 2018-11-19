# import heapq
#
#
# class Event:
#     def __init__(self, time, count, event_type):
#         self.time = time
#         self.count = count
#         self.event_type = event_type
#
#     def __lt__(self, other):
#         # Comparing float equality here is not really optimal, but the actual game code probably does the same.
#         # Best option would probably be to discretize time and use ints.
#         if self.time != other.time:
#             return self.time < other.time
#         elif self.count != other.count:
#             return self.count < other.count
#         else:
#             raise ValueError(f'__lt__: compared objects have the same time and count')
#
#     def __repr__(self):
#         return f'time={self.time}, count={self.count}, event_type={self.event_type}'
#
#
# # print(Event(0.0, 0, 0) < Event(1.0, 0, 0))
# # print(Event(0.0, 0, 0) < Event(0.0, 1, 0))
# # print(Event(0.0, 0, 0) < Event(0.0, 0, 1))
#
# # event_queue = []
# # heapq.heappush(event_queue, Event(0.0, 1, 0))
# # heapq.heappush(event_queue, Event(1.0, 0, 0))
# # heapq.heappush(event_queue, Event(0.0, 0, 0))
# # print(heapq.heappop(event_queue))
# # print(heapq.heappop(event_queue))
# # print(heapq.heappop(event_queue))
#
# # event_queue = []
# # heapq.heappush(event_queue, Event(1.0, 1, 0))
# # heapq.heappush(event_queue, Event(0.0, 0, 0))
# # heapq.heappush(event_queue, Event(1.1, 2, 0))
# # print(heapq.heappop(event_queue))
# # print(heapq.heappop(event_queue))
# # print(heapq.heappop(event_queue))
#
# # Due to what I consider a coincidence, in this simple example, the order comes out right even without calling sort.
# # event_queue = []
# # heapq.heappush(event_queue, Event(1.0, 1, 0))
# # heapq.heappush(event_queue, Event(0.0, 0, 0))
# # event = Event(1.1, 2, 0)
# # heapq.heappush(event_queue, event)
# # event.time = 0.9
# # event_queue.sort()
# # print(heapq.heappop(event_queue))
# # print(heapq.heappop(event_queue))
# # print(heapq.heappop(event_queue))
#
# # In this example, there is no coincidence like above and the sort call is mandatory.
# event_queue = []
# event_1 = Event(1.0, 1, 0)
# heapq.heappush(event_queue, event_1)
# event_2 = Event(0.0, 0, 0)
# heapq.heappush(event_queue, event_2)
# event_3 = Event(1.1, 2, 0)
# heapq.heappush(event_queue, event_3)
# event_1.time = 0.8
# event_2.time = 1.0
# event_3.time = 0.9
# event_queue.sort()
# print(heapq.heappop(event_queue))
# print(heapq.heappop(event_queue))
# print(heapq.heappop(event_queue))


# from collections import defaultdict
#
# stats = defaultdict(int, {'agi': 10})
# print(stats['agi'])
# print(stats['str'])


# from wow_dps_sim.scraper import Scraper
#
# # print(Scraper('https://vanillawowdb.com/?item=', use_cache=False).scrape_item('main_hand', '14555'))
# # print(Scraper('https://classicdb.ch/?item=', path_to_cache='cache/items/classicdb.ch').scrape_item('legs', '21495'))
# # print(Scraper('https://tbc-twinhead.twinstar.cz/?item=', use_cache=False).scrape_item('head', '28224'))
# # print(Scraper('http://tbc.cavernoftime.com/item=', use_cache=False).scrape_item('head', '28224'))
# # print(Scraper('http://tbc.cavernoftime.com/item=', use_cache=False).scrape_item('main_hand', '28437'))
#
# print(Scraper('http://tbc.cavernoftime.com/item=', path_to_cache='cache/items/tbc.cavernoftime.com').scrape_item('', '28224'))
# print(Scraper('http://tbc.cavernoftime.com/item=', path_to_cache='cache/items/tbc.cavernoftime.com').scrape_item('', '29381'))
# print(Scraper('http://tbc.cavernoftime.com/item=', path_to_cache='cache/items/tbc.cavernoftime.com').scrape_item('', '33173'))
# print(Scraper('http://tbc.cavernoftime.com/item=', path_to_cache='cache/items/tbc.cavernoftime.com').scrape_item('', '24259'))
# print(Scraper('http://tbc.cavernoftime.com/item=', path_to_cache='cache/items/tbc.cavernoftime.com').scrape_item('', '30258'))
# print(Scraper('http://tbc.cavernoftime.com/item=', path_to_cache='cache/items/tbc.cavernoftime.com').scrape_item('', '23537'))
# print(Scraper('http://tbc.cavernoftime.com/item=', path_to_cache='cache/items/tbc.cavernoftime.com').scrape_item('', '29503'))
# print(Scraper('http://tbc.cavernoftime.com/item=', path_to_cache='cache/items/tbc.cavernoftime.com').scrape_item('', '29247'))
# print(Scraper('http://tbc.cavernoftime.com/item=', path_to_cache='cache/items/tbc.cavernoftime.com').scrape_item('', '30538'))
# print(Scraper('http://tbc.cavernoftime.com/item=', path_to_cache='cache/items/tbc.cavernoftime.com').scrape_item('', '25686'))
# print(Scraper('http://tbc.cavernoftime.com/item=', path_to_cache='cache/items/tbc.cavernoftime.com').scrape_item('', '31920'))
# print(Scraper('http://tbc.cavernoftime.com/item=', path_to_cache='cache/items/tbc.cavernoftime.com').scrape_item('', '28323'))
# print(Scraper('http://tbc.cavernoftime.com/item=', path_to_cache='cache/items/tbc.cavernoftime.com').scrape_item('', '29383'))
# print(Scraper('http://tbc.cavernoftime.com/item=', path_to_cache='cache/items/tbc.cavernoftime.com').scrape_item('', '28034'))
# print(Scraper('http://tbc.cavernoftime.com/item=', path_to_cache='cache/items/tbc.cavernoftime.com').scrape_item('main_hand', '28437'))
# print(Scraper('http://tbc.cavernoftime.com/item=', path_to_cache='cache/items/tbc.cavernoftime.com').scrape_item('off_hand', '23542'))
# print(Scraper('http://tbc.cavernoftime.com/item=', path_to_cache='cache/items/tbc.cavernoftime.com').scrape_item('', '29151'))


# from collections import defaultdict
# import os
#
#
# def find_files(base_dir, excluded_exts, excluded_dirs):
#     files = []
#     for element in os.listdir(base_dir):
#         path_to_element = os.path.join(base_dir, element)
#         if os.path.isfile(path_to_element) and os.path.splitext(element)[1] not in excluded_exts:
#             files.append(path_to_element)
#         elif os.path.isdir(path_to_element) and element not in excluded_dirs:
#             files.extend(find_files(path_to_element, excluded_exts, excluded_dirs))
#
#     return files
#
#
# # base_dir = r'C:\Users\Naturwerk\Desktop\VanillaUtils'
# # base_dir = r'C:\Users\Naturwerk\Desktop\VanillaUtils\wow_dps_sim\expansion'
# # excluded_dirs = {'.git', '.idea', '__pycache__', 'cache', 'logs', 'static'}
#
# # base_dir = r'C:\Users\Naturwerk\Documents\GitHub\izivi_new\apps\iZivi'
# # excluded_dirs = {'.git', '.idea', '__pycache__', 'font', 'fpdf', 'json', 'smarty', 'tcpdf', 'utf8fpdf', 'templates_c', 'tmp', 'lib', 'jscolor'}
#
# base_dir = r'C:\Users\Naturwerk\Documents\GitHub\naturvielfalt_drupal_8_composer\web\modules\custom'
# excluded_dirs = {'.git', '.idea', '__pycache__', 'language'}
#
# files = find_files(base_dir, {'.gif', '.jpg', '.png', '.doc', '.pdf', '.log', '.ico', '.swf'}, excluded_dirs)
# stats = defaultdict(int)
# for file in files:
#     ext = os.path.splitext(file)[1]
#     print(file)
#     with open(file, encoding='utf-8') as f:
#         try:
#             n_lines = len(f.readlines())
#         except UnicodeDecodeError:
#             with open(file) as f:
#                 n_lines = len(f.readlines())
#         stats[ext] += n_lines
#
# print(sum(stats.values()))
# print(stats)


# import math
#
# print(type(math.floor(2.1)))


print(int(' '))
