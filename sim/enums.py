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


class Hand(Enum):
    MAIN = auto()
    OFF = auto()


class PlayerBuffs(Enum):
    DEATH_WISH = auto()
    RECKLESSNESS = auto()
    CRUSADER_MAIN = auto()
    CRUSADER_OFF = auto()


class Stance(Enum):
    BATTLE = auto()
    BERSERKER = auto()
