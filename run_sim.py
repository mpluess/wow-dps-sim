from collections import defaultdict
import time

from sim.entities import Boss, Config
from sim.sim import do_sim

faction = 'alliance'
race = 'human'
class_ = 'warrior'
spec = 'fury'

items = [
    {'name': 'Lionheart Helm', 'stats': defaultdict(int, {'armor': 565, 'str': 18, 'crit': 2, 'hit': 2}), 'set': {'name': None, 'bonuses': {}}},
    {'name': 'Mark of Fordring', 'stats': defaultdict(int, {'crit': 1, 'ap': 26}), 'set': {'name': None, 'bonuses': {}}},
    {'name': 'Truestrike Shoulders', 'stats': defaultdict(int, {'armor': 129, 'hit': 2, 'ap': 24}), 'set': {'name': None, 'bonuses': {}}},
    {'name': 'Cape of the Black Baron', 'stats': defaultdict(int, {'armor': 45, 'agi': 15, 'ap': 20}), 'set': {'name': None, 'bonuses': {}}},
    {'name': 'Ogre Forged Hauberk', 'stats': defaultdict(int, {'armor': 365, 'agi': 20, 'sta': 13, 'int': 8, 'str': 8, 'crit': 1}), 'set': {'name': None, 'bonuses': {}}},
    {'name': 'Battleborn Armbraces', 'stats': defaultdict(int, {'armor': 287, 'hit': 1, 'crit': 1}), 'set': {'name': None, 'bonuses': {}}},
    {'name': 'Devilsaur Gauntlets', 'stats': defaultdict(int, {'armor': 103, 'sta': 9, 'ap': 28, 'crit': 1}), 'set': {'name': 'Devilsaur Armor', 'bonuses': {2: ('hit', 2)}}},
    {'name': "Omokk's Girth Restrainer", 'stats': defaultdict(int, {'armor': 353, 'str': 15, 'sta': 9, 'crit': 1}), 'set': {'name': None, 'bonuses': {}}},
    {'name': 'Devilsaur Leggings', 'stats': defaultdict(int, {'armor': 148, 'sta': 12, 'ap': 46, 'crit': 1}), 'set': {'name': 'Devilsaur Armor', 'bonuses': {2: ('hit', 2)}}},
    {'name': 'Pads of the Dread Wolf', 'stats': defaultdict(int, {'armor': 116, 'sta': 14, 'ap': 40}), 'set': {'name': None, 'bonuses': {}}},
    {'name': 'Blackstone Ring', 'stats': defaultdict(int, {'sta': 6, 'ap': 20, 'hit': 1}), 'set': {'name': None, 'bonuses': {}}},
    {'name': 'Tarnished Elven Ring', 'stats': defaultdict(int, {'agi': 15, 'hit': 1}), 'set': {'name': None, 'bonuses': {}}},
    {'name': 'Hand of Justice', 'stats': defaultdict(int, {'ap': 20}), 'set': {'name': None, 'bonuses': {}}},
    {'name': "Blackhand's Breadth", 'stats': defaultdict(int, {'crit': 2}), 'set': {'name': None, 'bonuses': {}}},
    {'name': 'Mass of McGowan', 'stats': defaultdict(int, {'str': 10, 'sta': 10, 'weapon_type_main_hand': 'Mace', 'damage_range_main_hand': (80, 149), 'speed_main_hand': 2.8}), 'set': {'name': None, 'bonuses': {}}},
    {'name': "Mirah's Song", 'stats': defaultdict(int, {'agi': 9, 'str': 9, 'weapon_type_off_hand': 'Sword', 'damage_range_off_hand': (57, 87), 'speed_off_hand': 1.8}), 'set': {'name': None, 'bonuses': {}}},
    {'name': "Satyr's Bow", 'stats': defaultdict(int, {'agi': 7, 'hit': 1}), 'set': {'name': None, 'bonuses': {}}}
]
partial_buffed_permanent_stats = defaultdict(
    int, {
        'agi': 194, 'int': 58, 'spi': 70, 'sta': 203, 'str': 312,
        'crit': 24, 'Mace': 5, 'Sword': 5, 'damage_multiplier': 1.0, 'armor': 2111, 'hit': 10, 'ap': 781,
        'weapon_type_main_hand': 'Mace', 'damage_range_main_hand': (88, 157), 'speed_main_hand': 2.8,
        'weapon_type_off_hand': 'Sword', 'damage_range_off_hand': (57, 87), 'speed_off_hand': 1.8
    }
)

start = time.time()
result, stat_weights = do_sim(
    faction, race, class_, spec, items, partial_buffed_permanent_stats,
    boss=Boss(),
    config=Config(n_runs=1000, logging=False)
    # config=Config(n_runs=1, logging=True)
)
print(f'Runtime: {(time.time() - start):.2f} s')
print(str(result))
print(f'Stat weights: {stat_weights}')

# import cProfile
# cProfile.run("do_sim(faction, race, class_, spec, items, partial_buffed_permanent_stats, config={'n_runs': 100, 'logging': False, 'boss_fight_time_seconds': 180.0,})")
