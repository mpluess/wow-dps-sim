""" https://www.dalaran-wow.com/forums/community/general-discussion/topic/2149/the-comprehensive-list-of-raid-buffs-debuffs """

# TODO Moonkin hit? Retri % damage?

from collections import defaultdict

from wow_dps_sim.enums import Proc, OnUseEffect

# imp. battle shout 8
_BATTLE_SHOUT_ADDITIONAL_AP = 381

# imp. greater blessing of might 3
_BLESSING_OF_MIGHT_ADDITIONAL_AP = 264

_HEROIC_PRESENCE_ADDITIONAL_HIT = 1

_LEADER_OF_THE_PACK_ADDITIONAL_CRIT = 5

# imp. mark of the wild 8
_MARK_OF_THE_WILD_ADDITIONAL_STATS = 19

# imp. strength of earth 6
_STRENGTH_OF_EARTH_TOTEM_ADDITIONAL_STRENGTH = 100

_permanent_buff_flat_stats_alliance = defaultdict(int)

_permanent_buff_flat_stats_alliance['ap'] += _BATTLE_SHOUT_ADDITIONAL_AP

_permanent_buff_flat_stats_alliance['ap'] += _BLESSING_OF_MIGHT_ADDITIONAL_AP

_permanent_buff_flat_stats_alliance['hit'] += _HEROIC_PRESENCE_ADDITIONAL_HIT

_permanent_buff_flat_stats_alliance['crit'] += _LEADER_OF_THE_PACK_ADDITIONAL_CRIT

_permanent_buff_flat_stats_alliance['agi'] += _MARK_OF_THE_WILD_ADDITIONAL_STATS
_permanent_buff_flat_stats_alliance['int'] += _MARK_OF_THE_WILD_ADDITIONAL_STATS
_permanent_buff_flat_stats_alliance['spi'] += _MARK_OF_THE_WILD_ADDITIONAL_STATS
_permanent_buff_flat_stats_alliance['sta'] += _MARK_OF_THE_WILD_ADDITIONAL_STATS
_permanent_buff_flat_stats_alliance['str'] += _MARK_OF_THE_WILD_ADDITIONAL_STATS

_permanent_buff_flat_stats_alliance['str'] += _STRENGTH_OF_EARTH_TOTEM_ADDITIONAL_STRENGTH

PERMANENT_BUFF_FLAT_STATS = {
    'alliance': _permanent_buff_flat_stats_alliance,
}

_BLESSING_OF_KINGS_STATS_MULTIPLIER = 1.1
_BLOOD_FRENZY_DAMAGE_MULTIPLIER = 1.04
_UNLEASHED_RAGE_AP_MULTIPLIER = 1.1

PERMANENT_BUFF_MULTIPLIERS = {
    'alliance': {
        'agi': _BLESSING_OF_KINGS_STATS_MULTIPLIER,
        'int': _BLESSING_OF_KINGS_STATS_MULTIPLIER,
        'spi': _BLESSING_OF_KINGS_STATS_MULTIPLIER,
        'sta': _BLESSING_OF_KINGS_STATS_MULTIPLIER,
        'str': _BLESSING_OF_KINGS_STATS_MULTIPLIER,
        'ap': _UNLEASHED_RAGE_AP_MULTIPLIER,
        'damage_multiplier': _BLOOD_FRENZY_DAMAGE_MULTIPLIER,
    }
}

BUFF_PROCS = {
    Proc.WINDFURY_TOTEM,
}

BUFF_ON_USE_EFFECTS = {
    OnUseEffect.HEROISM,
}
