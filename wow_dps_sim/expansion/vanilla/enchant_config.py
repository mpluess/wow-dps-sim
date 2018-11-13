from collections import defaultdict

from wow_dps_sim.enums import Proc


_ENCHANT_BACK_AGILITY = 3
_ENCHANT_CHEST_STATS = 4
_ENCHANT_HANDS_HASTE = 1
_ENCHANT_HANDS_STRENGTH = 7
_ENCHANT_HEAD_HASTE = 1
_ENCHANT_HEAD_STRENGTH = 8
_ENCHANT_LEGS_HASTE = 1
_ENCHANT_LEGS_STRENGTH = 8
_ENCHANT_OFF_HAND_STRENGTH = 15
_ENCHANT_WRIST_STRENGTH = 9

_enchant_stats_warrior_fury = defaultdict(int)

# Head
# _enchant_stats_warrior_fury['haste'] += _ENCHANT_HEAD_HASTE
_enchant_stats_warrior_fury['str'] += _ENCHANT_HEAD_STRENGTH

# Back
_enchant_stats_warrior_fury['agi'] += _ENCHANT_BACK_AGILITY

# Chest
_enchant_stats_warrior_fury['agi'] += _ENCHANT_CHEST_STATS
_enchant_stats_warrior_fury['int'] += _ENCHANT_CHEST_STATS
_enchant_stats_warrior_fury['spi'] += _ENCHANT_CHEST_STATS
_enchant_stats_warrior_fury['sta'] += _ENCHANT_CHEST_STATS
_enchant_stats_warrior_fury['str'] += _ENCHANT_CHEST_STATS

# Wrist
_enchant_stats_warrior_fury['str'] += _ENCHANT_WRIST_STRENGTH

# Hands
# _enchant_stats_warrior_fury['haste'] += _ENCHANT_HANDS_HASTE
_enchant_stats_warrior_fury['str'] += _ENCHANT_HANDS_STRENGTH

# Legs
# _enchant_stats_warrior_fury['haste'] += _ENCHANT_LEGS_HASTE
_enchant_stats_warrior_fury['str'] += _ENCHANT_LEGS_STRENGTH

# Off Hand
# _enchant_stats_warrior_fury['str'] += _ENCHANT_OFF_HAND_STRENGTH

ENCHANT_STATS = {
    'warrior': {
        'fury': _enchant_stats_warrior_fury,
    },
}
ENCHANT_PROCS = {Proc.CRUSADER_MAIN, Proc.CRUSADER_OFF}
