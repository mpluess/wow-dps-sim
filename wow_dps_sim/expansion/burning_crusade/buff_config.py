""" https://www.dalaran-wow.com/forums/community/general-discussion/topic/2149/the-comprehensive-list-of-raid-buffs-debuffs """

from collections import defaultdict

from wow_dps_sim.enums import Proc, OnUseEffect

# TODO check wowhead composition tool for possible missing buffs and debuffs
# TODO retri aura 2% damage

# imp. battle shout 8
_BATTLE_SHOUT_ADDITIONAL_AP = 382

_SOLARIANS_SAPPHIRE_ADDITIONAL_AP = 88

# imp. greater blessing of might 3
_BLESSING_OF_MIGHT_ADDITIONAL_AP = 264

# imp. hunter's mark 4
_HUNTERS_MARK_ADDITIONAL_AP = 110

_TRUESHOT_AURA_ADDITIONAL_AP = 125

_HEROIC_PRESENCE_ADDITIONAL_HIT = 1

# imp. faerie fire
_FAERIE_FIRE_ADDITIONAL_HIT = 3

# https://tbc.wowhead.com/item=32387/idol-of-the-raven-goddess
_LEADER_OF_THE_PACK_ADDITIONAL_CRIT = 5.91

# imp. seal of the crusader
_SEAL_OF_THE_CRUSADER_ADDITIONAL_CRIT = 3

# imp. mark of the wild 8
_MARK_OF_THE_WILD_ADDITIONAL_STATS = 19

# imp. strength of earth 6
_STRENGTH_OF_EARTH_TOTEM_ADDITIONAL_STRENGTH = 100

# imp. grace of air 3
_GRACE_OF_AIR_TOTEM_ADDITIONAL_AGILITY = 89

_permanent_buff_flat_stats_alliance = defaultdict(int)

_permanent_buff_flat_stats_alliance['ap'] += _BATTLE_SHOUT_ADDITIONAL_AP
_permanent_buff_flat_stats_alliance['ap'] += _SOLARIANS_SAPPHIRE_ADDITIONAL_AP
_permanent_buff_flat_stats_alliance['ap'] += _BLESSING_OF_MIGHT_ADDITIONAL_AP
_permanent_buff_flat_stats_alliance['ap'] += _HUNTERS_MARK_ADDITIONAL_AP
_permanent_buff_flat_stats_alliance['ap'] += _TRUESHOT_AURA_ADDITIONAL_AP

# _permanent_buff_flat_stats_alliance['hit'] += _HEROIC_PRESENCE_ADDITIONAL_HIT
_permanent_buff_flat_stats_alliance['hit'] += _FAERIE_FIRE_ADDITIONAL_HIT

_permanent_buff_flat_stats_alliance['crit'] += _LEADER_OF_THE_PACK_ADDITIONAL_CRIT
_permanent_buff_flat_stats_alliance['crit'] += _SEAL_OF_THE_CRUSADER_ADDITIONAL_CRIT

_permanent_buff_flat_stats_alliance['agi'] += _MARK_OF_THE_WILD_ADDITIONAL_STATS
_permanent_buff_flat_stats_alliance['int'] += _MARK_OF_THE_WILD_ADDITIONAL_STATS
_permanent_buff_flat_stats_alliance['spi'] += _MARK_OF_THE_WILD_ADDITIONAL_STATS
_permanent_buff_flat_stats_alliance['sta'] += _MARK_OF_THE_WILD_ADDITIONAL_STATS
_permanent_buff_flat_stats_alliance['str'] += _MARK_OF_THE_WILD_ADDITIONAL_STATS

_permanent_buff_flat_stats_alliance['str'] += _STRENGTH_OF_EARTH_TOTEM_ADDITIONAL_STRENGTH

_permanent_buff_flat_stats_alliance['agi'] += _GRACE_OF_AIR_TOTEM_ADDITIONAL_AGILITY

PERMANENT_BUFF_FLAT_STATS = {
    'alliance': _permanent_buff_flat_stats_alliance,
}

_BLESSING_OF_KINGS_STATS_MULTIPLIER = 1.1
_BLOOD_FRENZY_DAMAGE_MULTIPLIER = 1.04
_FEROCIOUS_INSPIRATION_DAMAGE_MULTIPLIER = 1.03
_UNLEASHED_RAGE_AP_MULTIPLIER = 1.1

PERMANENT_BUFF_MULTIPLIERS = {
    'alliance': {
        'agi': _BLESSING_OF_KINGS_STATS_MULTIPLIER,
        'int': _BLESSING_OF_KINGS_STATS_MULTIPLIER,
        'spi': _BLESSING_OF_KINGS_STATS_MULTIPLIER,
        'sta': _BLESSING_OF_KINGS_STATS_MULTIPLIER,
        'str': _BLESSING_OF_KINGS_STATS_MULTIPLIER,
        'ap': _UNLEASHED_RAGE_AP_MULTIPLIER,
        'damage_multiplier': _BLOOD_FRENZY_DAMAGE_MULTIPLIER * _FEROCIOUS_INSPIRATION_DAMAGE_MULTIPLIER,
    }

    # 'alliance': dict()
}

BUFF_PROCS = {
    Proc.WINDFURY_TOTEM,
}
# BUFF_PROCS = set()

BUFF_ON_USE_EFFECTS = {
    OnUseEffect.HEROISM,
}
# BUFF_ON_USE_EFFECTS = set()
