from enum import auto, Enum


class AttackResult(Enum):
    MISS = auto()
    DODGE = auto()
    GLANCING = auto()
    CRIT = auto()
    HIT = auto()


class AttackTableModification(Enum):
    OVERPOWER = auto()


class AttackType(Enum):
    WHITE = auto()
    YELLOW = auto()
    HEROIC_STRIKE = auto()


class BossDebuffs(Enum):
    SUNDER_ARMOR_X5 = auto()
    FAERIE_FIRE = auto()
    CURSE_OF_RECKLESSNESS = auto()


class EventType(Enum):
    WHITE_HIT_MAIN = auto()
    HAND_OF_JUSTICE_PROC = auto()
    THRASH_BLADE_PROC = auto()
    IRONFOE_PROC = auto()
    WHITE_HIT_OFF = auto()
    HEROIC_STRIKE_LANDED = auto()

    BLOODTHIRST_CD_END = auto()
    WHIRLWIND_CD_END = auto()
    OVERPOWER_CD_END = auto()
    ATTACK_DODGED = auto()

    BLOODRAGE_CD_END = auto()
    DEATH_WISH_END = auto()
    DEATH_WISH_CD_END = auto()
    RECKLESSNESS_END = auto()
    RECKLESSNESS_CD_END = auto()

    GCD_END = auto()
    STANCE_CD_END = auto()
    RAGE_GAINED = auto()

    BLOODRAGE_ADD_RAGE_OVER_TIME = auto()

    CRUSADER_MAIN_PROC = auto()
    CRUSADER_MAIN_PROC_END = auto()
    CRUSADER_OFF_PROC = auto()
    CRUSADER_OFF_PROC_END = auto()

    KISS_OF_THE_SPIDER_CD_END = auto()
    KISS_OF_THE_SPIDER_END = auto()
    SLAYERS_CREST_CD_END = auto()
    SLAYERS_CREST_END = auto()

    JUJU_FLURRY_CD_END = auto()
    JUJU_FLURRY_END = auto()
    MIGHTY_RAGE_POTION_CD_END = auto()
    MIGHTY_RAGE_POTION_END = auto()

    # Burning Crusade
    RAMPAGE_END = auto()
    ATTACK_CRIT = auto()


class Hand(Enum):
    MAIN = auto()
    OFF = auto()


class OnUseEffect(Enum):
    # Vanilla
    KISS_OF_THE_SPIDER = auto()
    SLAYERS_CREST = auto()

    MIGHTY_RAGE_POTION = auto()
    JUJU_FLURRY = auto()

    # BC
    HASTE_POTION = auto()


class PlayerBuffs(Enum):
    DEATH_WISH = auto()
    RECKLESSNESS = auto()

    CRUSADER_MAIN = auto()
    CRUSADER_OFF = auto()

    KISS_OF_THE_SPIDER = auto()
    SLAYERS_CREST = auto()

    JUJU_FLURRY = auto()
    MIGHTY_RAGE_POTION = auto()

    # Burning Crusade
    RAMPAGE = auto()


class Proc(Enum):
    # Vanilla
    CRUSADER_MAIN = auto()
    CRUSADER_OFF = auto()
    HAND_OF_JUSTICE = auto()
    IRONFOE = auto()
    THRASH_BLADE_MAIN = auto()
    THRASH_BLADE_OFF = auto()

    # Burning Crusade
    EXECUTIONER_MAIN = auto()
    EXECUTIONER_OFF = auto()
    MONGOOSE_MAIN = auto()
    MONGOOSE_OFF = auto()


class Stance(Enum):
    BATTLE = auto()
    BERSERKER = auto()
