from collections import defaultdict


# Warrior general
GCD_DURATION = 1.5
STANCE_CD_DURATION = 1.5

MAX_RAGE = 100
MAX_RAGE_AFTER_STANCE_SWITCH = 25

CRIT_DAMAGE_MULTIPLIER = 2.0
CRIT_WITH_IMPALE_DAMAGE_MULTIPLIER = 2.2

OFF_HAND_FACTOR = 0.625

BERSERKER_STANCE_ADDITIONAL_CRIT = 3

# Warrior abilities
BLOODRAGE_BASE_RAGE = 10
BLOODRAGE_CD = 60.0
BLOODRAGE_DURATION = 10
BLOODRAGE_TICK_RAGE = 1

BLOODTHIRST_AP_FACTOR = 0.45
BLOODTHIRST_CD = 6.0
BLOODTHIRST_RAGE_COST = 30

DEATH_WISH_CD = 180.0
DEATH_WISH_DAMAGE_MULTIPLIER = 1.2
DEATH_WISH_DURATION = 30.0
DEATH_WISH_RAGE_COST = 10

EXECUTE_BASE_DAMAGE = 600
EXECUTE_BASE_RAGE_COST = 10
EXECUTE_DAMAGE_PER_RAGE = 15

FLURRY_FACTOR = 1.3

# Rank 8
HEROIC_STRIKE_ADDITIONAL_DAMAGE = 138
HEROIC_STRIKE_RAGE_COST = 13

OVERPOWER_ADDITIONAL_DAMAGE = 35
OVERPOWER_AVAILABILITY_DURATION = 4.0
OVERPOWER_CD = 5.0
OVERPOWER_RAGE_COST = 5

RECKLESSNESS_ADDITIONAL_CRIT = 100
RECKLESSNESS_CD = 1800.0
RECKLESSNESS_DURATION = 15.0

SUNDER_ARMOR_REDUCTION_PER_STACK = 450

WHIRLWIND_CD = 10.0
WHIRLWIND_RAGE_COST = 25

# Other abilities
CURSE_OF_RECKLESSNESS_ARMOR_REDUCTION = 640
FAERIE_FIRE_ARMOR_REDUCTION = 505

# Items
NORMALIZED_WEAPON_SPEED_LOOKUP = {
    'Dagger': 1.7,
    'Axe': 2.4,
    'Fist Weapon': 2.4,
    'Mace': 2.4,
    'Sword': 2.4,
}

HAND_OF_JUSTICE_PROC_CHANCE = 0.02
IRONFOE_PROC_CHANCE = 0.05
THRASH_BLADE_PROC_CHANCE = 0.05

KISS_OF_THE_SPIDER_CD = 120.0
KISS_OF_THE_SPIDER_DURATION = 15.0
KISS_OF_THE_SPIDER_SPEED_MULTIPLIER = 1.2

SLAYERS_CREST_ADDITIONAL_AP = 260
SLAYERS_CREST_CD = 120.0
SLAYERS_CREST_DURATION = 20.0

JUJU_FLURRY_ADDITIONAL_HASTE = 3
JUJU_FLURRY_CD = 60.0
JUJU_FLURRY_DURATION = 20.0

MIGHTY_RAGE_POTION_ADDITIONAL_STRENGTH = 60
MIGHTY_RAGE_POTION_CD = 120.0
MIGHTY_RAGE_POTION_DURATION = 20.0
MIGHTY_RAGE_POTION_MIN_RAGE = 45
MIGHTY_RAGE_POTION_MAX_RAGE = 75

# Enchants
CRUSADER_ADDITIONAL_STRENGTH = 100
CRUSADER_DURATION = 15.0
CRUSADER_PPM = 1.0

# Stats
# TODO are these really correct?
# https://www.getmangos.eu/forums/topic/8703-level-60-stats/
BASE_STATS = {
    'human': {
        'warrior': defaultdict(int, {
            'agi': 80,
            'int': 30,
            'spi': 50,
            'sta': 110,
            'str': 120,
            'damage_multiplier': 1.0,
            'speed_multiplier': 1.0,
            'Mace': 5,
            'Sword': 5,
        }),
    },
}

_CRUELTY_ADDITIONAL_CRIT = 5
SPEC_STATS = {
    'warrior': {
        'fury': defaultdict(int, {
            'crit': _CRUELTY_ADDITIONAL_CRIT,
        }),
    },
}
