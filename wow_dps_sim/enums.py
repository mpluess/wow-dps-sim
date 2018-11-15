from enum import auto, Enum


class OnUseEffect(Enum):
    # Vanilla
    KISS_OF_THE_SPIDER = auto()
    SLAYERS_CREST = auto()

    MIGHTY_RAGE_POTION = auto()
    JUJU_FLURRY = auto()

    # BC
    HASTE_POTION = auto()


class Proc(Enum):
    # Vanilla
    CRUSADER_MAIN = auto()
    CRUSADER_OFF = auto()
    HAND_OF_JUSTICE = auto()
    IRONFOE = auto()
    THRASH_BLADE_MAIN = auto()
    THRASH_BLADE_OFF = auto()

    # BC
    EXECUTIONER_MAIN = auto()
    EXECUTIONER_OFF = auto()
    MONGOOSE_MAIN = auto()
    MONGOOSE_OFF = auto()
