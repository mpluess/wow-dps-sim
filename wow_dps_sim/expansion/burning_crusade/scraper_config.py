import re

import wow_dps_sim.expansion.scraper_config


class ScraperConfig(wow_dps_sim.expansion.scraper_config.ScraperConfig):
    secondary_stats_attr_regex_tuples = [
        ('ap', re.compile(r'Increases attack power by (?P<value>\d+)')),
        ('crit_rating', re.compile(r'Increases your critical strike rating by (?P<value>\d+)')),
        ('hit_rating', re.compile(r'Increases your hit rating by (?P<value>\d+)')),
        ('haste_rating', re.compile(r'Improves haste rating by (?P<value>\d+)')),
        ('arp', re.compile(r"Your attacks ignore (?P<value>\d+) of your opponent's armor")),
        ('exp_rating', re.compile(r'Increases your expertise rating by (?P<value>\d+)')),
    ]

    proc_mapping = dict()
    weapon_proc_mapping = dict()
    on_use_effect_mapping = dict()
