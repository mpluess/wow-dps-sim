from enum import auto, Enum


class Ability(Enum):
    BLOODRAGE = auto()
    BLOODTHIRST = auto()
    DEATH_WISH = auto()
    EXECUTE = auto()
    HAND_OF_JUSTICE_PROC = auto()
    HEROIC_STRIKE = auto()
    IRONFOE_PROC = auto()
    JUJU_FLURRY = auto()
    KISS_OF_THE_SPIDER = auto()
    MIGHTY_RAGE_POTION = auto()
    OVERPOWER = auto()
    RECKLESSNESS = auto()
    SLAYERS_CREST = auto()
    THRASH_BLADE_PROC = auto()
    WHIRLWIND = auto()
    WHITE = auto()
    WHITE_MAIN = auto()
    WHITE_OFF = auto()
    WINDFURY_PROC = auto()

    # BC
    ANGER_MANAGEMENT = auto()
    BLOODLUST_BROOCH = auto()
    DRAGONSPINE_TROPHY = auto()
    DRUMS_OF_BATTLE = auto()
    DRUMS_OF_WAR = auto()
    HASTE_POTION = auto()
    HEROISM = auto()
    HOURGLASS_OF_THE_UNRAVELLER = auto()
    RAMPAGE = auto()
    WHIRLWIND_MAIN = auto()
    WHIRLWIND_OFF = auto()


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

    WINDFURY_TOTEM_PROC = auto()

    # Burning Crusade
    RAMPAGE_END = auto()
    ATTACK_CRIT = auto()
    ANGER_MANAGEMENT_TICK = auto()

    DRAKEFIST_HAMMER_PROC = auto()
    DRAKEFIST_HAMMER_PROC_END = auto()

    BLACKOUT_TRUNCHEON_PROC = auto()
    BLACKOUT_TRUNCHEON_PROC_END = auto()

    HOURGLASS_OF_THE_UNRAVELLER_ICD_END = auto()
    HOURGLASS_OF_THE_UNRAVELLER_PROC = auto()
    HOURGLASS_OF_THE_UNRAVELLER_PROC_END = auto()

    DRAGONSPINE_TROPHY_PROC = auto()
    DRAGONSPINE_TROPHY_PROC_END = auto()

    EXECUTIONER_PROC = auto()
    EXECUTIONER_PROC_END = auto()

    MONGOOSE_MAIN_PROC = auto()
    MONGOOSE_MAIN_PROC_END = auto()
    MONGOOSE_OFF_PROC = auto()
    MONGOOSE_OFF_PROC_END = auto()

    BLOODLUST_BROOCH_CD_END = auto()
    BLOODLUST_BROOCH_END = auto()
    DRUMS_OF_BATTLE_CD_END = auto()
    DRUMS_OF_BATTLE_END = auto()
    DRUMS_OF_WAR_CD_END = auto()
    DRUMS_OF_WAR_END = auto()
    HASTE_POTION_CD_END = auto()
    HASTE_POTION_END = auto()
    HEROISM_CD_END = auto()
    HEROISM_END = auto()


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
    BLOODLUST_BROOCH = auto()

    DRUMS_OF_BATTLE = auto()
    DRUMS_OF_WAR = auto()
    HASTE_POTION = auto()

    HEROISM = auto()


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
    BLACKOUT_TRUNCHEON = auto()
    BLOODLUST_BROOCH = auto()
    DRAGONSPINE_TROPHY = auto()
    DRAKEFIST_HAMMER = auto()
    DRUMS_OF_BATTLE = auto()
    DRUMS_OF_WAR = auto()
    EXECUTIONER = auto()
    HASTE_POTION = auto()
    HEROISM = auto()
    HOURGLASS_OF_THE_UNRAVELLER = auto()
    MONGOOSE_MAIN = auto()
    MONGOOSE_OFF = auto()
    RAMPAGE = auto()


class Proc(Enum):
    # Vanilla
    CRUSADER_MAIN = auto()
    CRUSADER_OFF = auto()
    HAND_OF_JUSTICE = auto()
    IRONFOE = auto()
    THRASH_BLADE_MAIN = auto()
    THRASH_BLADE_OFF = auto()
    WINDFURY_TOTEM = auto()

    # Burning Crusade
    EXECUTIONER_MAIN = auto()
    EXECUTIONER_OFF = auto()
    MONGOOSE_MAIN = auto()
    MONGOOSE_OFF = auto()
    DRAKEFIST_HAMMER_MAIN = auto()
    DRAKEFIST_HAMMER_OFF = auto()
    BLACKOUT_TRUNCHEON_MAIN = auto()
    BLACKOUT_TRUNCHEON_OFF = auto()
    HOURGLASS_OF_THE_UNRAVELLER = auto()
    DRAGONSPINE_TROPHY = auto()


class Stance(Enum):
    BATTLE = auto()
    BERSERKER = auto()
