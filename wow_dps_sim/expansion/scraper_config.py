import re

from wow_dps_sim.enums import OnUseEffect, Proc


class ScraperConfig:
    primary_stats_attr_regex_tuples = [
        ('armor', re.compile(r'(?P<value>\d+) Armor')),
        ('agi', re.compile(r'\+(?P<value>\d+) Agility')),
        ('int', re.compile(r'\+(?P<value>\d+) Intellect')),
        ('spi', re.compile(r'\+(?P<value>\d+) Spirit')),
        ('sta', re.compile(r'\+(?P<value>\d+) Stamina')),
        ('str', re.compile(r'\+(?P<value>\d+) Strength')),
    ]
    weapon_stats_attr_regex_tuples = [
        ('speed', re.compile(r'Speed (?P<value>[\d.]+)')),
        ('damage_range', re.compile(r'(?P<value_min>\d+) - (?P<value_max>\d+)\s+Damage')),
        ('weapon_type', re.compile(r'(?P<value>Axe|Dagger|Fist Weapon|Mace|Sword)')),
    ]
    secondary_stats_attr_regex_tuples = [
        ('ap', re.compile(r'\+(?P<value>\d+) Attack Power')),
        ('crit', re.compile(r'Improves your chance to get a critical strike by (?P<value>\d+)%')),
        ('hit', re.compile(r'Improves your chance to hit by (?P<value>\d+)%')),
        ('dodge', re.compile(r'Increases your chance to dodge an attack by (?P<value>\d+)%')),
        ('Axe', re.compile(r'Increased Axes \+(?P<value>\d+)')),
        ('Dagger', re.compile(r'Increased Daggers \+(?P<value>\d+)')),
        ('Mace', re.compile(r'Increased Maces \+(?P<value>\d+)')),
        ('Sword', re.compile(r'Increased Swords \+(?P<value>\d+)')),
        ('def', re.compile(r'Increased Defense \+(?P<value>\d+)')),
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
    on_use_effect_mapping = {
        'Kiss of the Spider': OnUseEffect.KISS_OF_THE_SPIDER,
        "Slayer's Crest": OnUseEffect.SLAYERS_CREST,
    }
