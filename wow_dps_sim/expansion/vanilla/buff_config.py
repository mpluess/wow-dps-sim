"""https://github.com/Sweeksprox/vanilla-wow-raid-buffs/blob/master/raidBuffs.js"""

from collections import defaultdict

# imp. battle shout 6
_BATTLE_SHOUT_ADDITIONAL_AP = 231

_BLESSING_OF_KINGS_STATS_MULTIPLIER = 1.1

# imp. blessing of might 6
_BLESSING_OF_MIGHT_ADDITIONAL_AP = 186

_LEADER_OF_THE_PACK_ADDITIONAL_CRIT = 3

# imp. mark of the wild 7
_MARK_OF_THE_WILD_ADDITIONAL_STATS = 16

_TRUESHOT_AURA_ADDITIONAL_AP = 100

_permanent_buff_flat_stats_alliance = defaultdict(int)

_permanent_buff_flat_stats_alliance['ap'] += _BATTLE_SHOUT_ADDITIONAL_AP

_permanent_buff_flat_stats_alliance['ap'] += _BLESSING_OF_MIGHT_ADDITIONAL_AP

_permanent_buff_flat_stats_alliance['agi'] += _MARK_OF_THE_WILD_ADDITIONAL_STATS
_permanent_buff_flat_stats_alliance['int'] += _MARK_OF_THE_WILD_ADDITIONAL_STATS
_permanent_buff_flat_stats_alliance['spi'] += _MARK_OF_THE_WILD_ADDITIONAL_STATS
_permanent_buff_flat_stats_alliance['sta'] += _MARK_OF_THE_WILD_ADDITIONAL_STATS
_permanent_buff_flat_stats_alliance['str'] += _MARK_OF_THE_WILD_ADDITIONAL_STATS

# _permanent_buff_flat_stats_alliance['crit'] += _LEADER_OF_THE_PACK_ADDITIONAL_CRIT

_permanent_buff_flat_stats_alliance['ap'] += _TRUESHOT_AURA_ADDITIONAL_AP

PERMANENT_BUFF_FLAT_STATS = {
    'alliance': _permanent_buff_flat_stats_alliance,
}

PERMANENT_BUFF_MULTIPLIERS = {
    'alliance': {
        'agi': _BLESSING_OF_KINGS_STATS_MULTIPLIER,
        'int': _BLESSING_OF_KINGS_STATS_MULTIPLIER,
        'spi': _BLESSING_OF_KINGS_STATS_MULTIPLIER,
        'sta': _BLESSING_OF_KINGS_STATS_MULTIPLIER,
        'str': _BLESSING_OF_KINGS_STATS_MULTIPLIER,
    }
}
