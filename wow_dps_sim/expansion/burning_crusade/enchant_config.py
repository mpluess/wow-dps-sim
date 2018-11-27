""" http://web.archive.org/web/20130810120034/http://elitistjerks.com/f81/t22705-dps_compendium/ """

from collections import defaultdict

from wow_dps_sim.enums import Proc


_ENCHANT_BACK_AGILITY = 12
_ENCHANT_CHEST_STATS = 6
_ENCHANT_FEET_AGILITY = 6
_ENCHANT_HANDS_STRENGTH = 15
_ENCHANT_HEAD_AP = 34
_ENCHANT_HEAD_HIT_RATING = 16
_ENCHANT_LEGS_AP = 50
_ENCHANT_LEGS_CRIT_RATING = 12
_ENCHANT_SHOULDER_AP = 30
_ENCHANT_SHOULDER_CRIT_RATING = 10
_ENCHANT_WRIST_STRENGTH = 12

_enchant_stats_warrior_fury = defaultdict(int)

# Back
_enchant_stats_warrior_fury['agi'] += _ENCHANT_BACK_AGILITY

# Chest
_enchant_stats_warrior_fury['agi'] += _ENCHANT_CHEST_STATS
_enchant_stats_warrior_fury['int'] += _ENCHANT_CHEST_STATS
_enchant_stats_warrior_fury['spi'] += _ENCHANT_CHEST_STATS
_enchant_stats_warrior_fury['sta'] += _ENCHANT_CHEST_STATS
_enchant_stats_warrior_fury['str'] += _ENCHANT_CHEST_STATS

# Feet
_enchant_stats_warrior_fury['agi'] += _ENCHANT_FEET_AGILITY

# Hands
_enchant_stats_warrior_fury['str'] += _ENCHANT_HANDS_STRENGTH

# Head
_enchant_stats_warrior_fury['ap'] += _ENCHANT_HEAD_AP
_enchant_stats_warrior_fury['hit_rating'] += _ENCHANT_HEAD_HIT_RATING

# Legs
_enchant_stats_warrior_fury['ap'] += _ENCHANT_LEGS_AP
_enchant_stats_warrior_fury['crit_rating'] += _ENCHANT_LEGS_CRIT_RATING

# Shoulder
_enchant_stats_warrior_fury['ap'] += _ENCHANT_SHOULDER_AP
_enchant_stats_warrior_fury['crit_rating'] += _ENCHANT_SHOULDER_CRIT_RATING

# Wrist
_enchant_stats_warrior_fury['str'] += _ENCHANT_WRIST_STRENGTH

ENCHANT_STATS = {
    'warrior': {
        'fury': _enchant_stats_warrior_fury,
    },
}
ENCHANT_PROCS = {
    Proc.EXECUTIONER_MAIN,
    Proc.MONGOOSE_OFF,
}
