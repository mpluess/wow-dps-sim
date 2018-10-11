from enum import auto, Enum


class AttackTable(Enum):
    MISS = auto()
    DODGE = auto()
    GLANCING = auto()
    CRIT = auto()
    HIT = auto()


class AttackType(Enum):
    WHITE = auto()
    YELLOW = auto()


class BossDebuffs(Enum):
    SUNDER_ARMOR_X5 = auto()
    FAERIE_FIRE = auto()
    CURSE_OF_RECKLESSNESS = auto()


class EventType(Enum):
    WHITE_HIT_MAIN = auto()
    WHITE_HIT_OFF = auto()

    BLOODTHIRST_CD_END = auto()
    WHIRLWIND_CD_END = auto()

    BLOODRAGE_CD_END = auto()
    DEATH_WISH_END = auto()
    DEATH_WISH_CD_END = auto()
    RECKLESSNESS_END = auto()
    RECKLESSNESS_CD_END = auto()

    GCD_END = auto()
    RAGE_GAINED = auto()

    BLOODRAGE_ADD_RAGE_OVER_TIME = auto()


class Hand(Enum):
    MAIN = auto()
    OFF = auto()


class PlayerBuffs(Enum):
    DEATH_WISH = auto()
    RECKLESSNESS = auto()
