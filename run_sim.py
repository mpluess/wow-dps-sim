from collections import defaultdict

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
    {'name': "Edgemaster's Handguards", 'stats': defaultdict(int, {'armor': 201, 'Axe': 7, 'Dagger': 7, 'Sword': 7}), 'set': {'name': None, 'bonuses': {}}},
    {'name': "Omokk's Girth Restrainer", 'stats': defaultdict(int, {'armor': 353, 'str': 15, 'sta': 9, 'crit': 1}), 'set': {'name': None, 'bonuses': {}}},
    {'name': 'Blademaster Leggings', 'stats': defaultdict(int, {'armor': 154, 'agi': 5, 'hit': 1, 'crit': 1, 'dodge': 2}), 'set': {'name': None, 'bonuses': {}}},
    {'name': 'Pads of the Dread Wolf', 'stats': defaultdict(int, {'armor': 116, 'sta': 14, 'ap': 40}), 'set': {'name': None, 'bonuses': {}}},
    {'name': 'Blackstone Ring', 'stats': defaultdict(int, {'sta': 6, 'ap': 20, 'hit': 1}), 'set': {'name': None, 'bonuses': {}}},
    {'name': 'Tarnished Elven Ring', 'stats': defaultdict(int, {'agi': 15, 'hit': 1}), 'set': {'name': None, 'bonuses': {}}},
    {'name': 'Hand of Justice', 'stats': defaultdict(int, {'ap': 20}), 'set': {'name': None, 'bonuses': {}}},
    {'name': "Blackhand's Breadth", 'stats': defaultdict(int, {'crit': 2}), 'set': {'name': None, 'bonuses': {}}},
    {'name': 'Thrash Blade', 'stats': defaultdict(int, {'weapon_type_main_hand': 'Sword', 'damage_range_main_hand': (66, 124), 'speed_main_hand': 2.7}), 'set': {'name': None, 'bonuses': {}}},
    {'name': "Mirah's Song", 'stats': defaultdict(int, {'agi': 9, 'str': 9, 'weapon_type_off_hand': 'Sword', 'damage_range_off_hand': (57, 87), 'speed_off_hand': 1.8}), 'set': {'name': None, 'bonuses': {}}},
    {'name': "Satyr's Bow", 'stats': defaultdict(int, {'agi': 7, 'hit': 1}), 'set': {'name': None, 'bonuses': {}}}
]
partial_buffed_permanent_stats = defaultdict(int, {
    'agi': 199, 'int': 58, 'spi': 70, 'sta': 172, 'str': 302,
    'crit': 26, 'Mace': 5, 'Sword': 12, 'damage_multiplier': 1.0, 'armor': 2215, 'hit': 9, 'ap': 707, 'Axe': 7, 'Dagger': 7, 'dodge': 2,
    'weapon_type_main_hand': 'Sword', 'damage_range_main_hand': (74, 132), 'speed_main_hand': 2.7, 'weapon_type_off_hand': 'Sword', 'damage_range_off_hand': (57, 87), 'speed_off_hand': 1.8
})

avg_dps, stat_weights = do_sim(faction, race, class_, spec, items, partial_buffed_permanent_stats)
print(f'Average DPS: {avg_dps}')
print(f'Stat weights: {stat_weights}')
