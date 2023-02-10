import re

from wow_dps_sim.enums import Proc, OnUseEffect
import wow_dps_sim.expansion.scraper_config


class ScraperConfig(wow_dps_sim.expansion.scraper_config.ScraperConfig):
    secondary_stats_attr_regex_tuples = [
        ('ap', re.compile(r'Increases attack power by (?P<value>\d+)')),
        ('crit_rating', re.compile(r'(?:Increases your critical strike rating|Improves melee critical strike rating) by (?P<value>\d+)')),
        ('hit_rating', re.compile(r'Increases your hit rating by (?P<value>\d+)')),
        ('haste_rating', re.compile(r'Improves haste rating by (?P<value>\d+)')),
        ('arp', re.compile(r"Your attacks ignore (?P<value>\d+) of your opponent's armor")),
        ('exp_rating', re.compile(r'Increases your expertise rating by (?P<value>\d+)')),
    ]

    proc_mapping = {
        'Hourglass of the Unraveller': Proc.HOURGLASS_OF_THE_UNRAVELLER,
        'Dragonspine Trophy': Proc.DRAGONSPINE_TROPHY,
    }

    weapon_proc_mapping = {
        'Drakefist Hammer': {
            'main_hand': Proc.DRAKEFIST_HAMMER_MAIN,
            'off_hand': Proc.DRAKEFIST_HAMMER_OFF
        },
        'Dragonmaw': {
            'main_hand': Proc.DRAKEFIST_HAMMER_MAIN,
            'off_hand': Proc.DRAKEFIST_HAMMER_OFF
        },
        'Dragonstrike': {
            'main_hand': Proc.DRAKEFIST_HAMMER_MAIN,
            'off_hand': Proc.DRAKEFIST_HAMMER_OFF
        },
        'Blackout Truncheon': {
            'main_hand': Proc.BLACKOUT_TRUNCHEON_MAIN,
            'off_hand': Proc.BLACKOUT_TRUNCHEON_OFF
        },
    }

    on_use_effect_mapping = {
        'Bloodlust Brooch': OnUseEffect.BLOODLUST_BROOCH,
    }
