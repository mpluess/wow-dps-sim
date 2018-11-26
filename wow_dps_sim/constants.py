from .enums import Ability, EventType, OnUseEffect


class Constants:
    ability_names_lookup = {
        Ability.ANGER_MANAGEMENT: 'Anger Management',
        Ability.BLOODRAGE: 'Bloodrage',
        Ability.BLOODTHIRST: 'Bloodthirst',
        Ability.DEATH_WISH: 'Death Wish',
        Ability.EXECUTE: 'Execute',
        Ability.HAND_OF_JUSTICE_PROC: 'Hand of Justice Proc',
        Ability.HEROIC_STRIKE: 'Heroic Strike',
        Ability.IRONFOE_PROC: 'Ironfoe Proc',
        Ability.JUJU_FLURRY: 'Juju Flurry',
        Ability.KISS_OF_THE_SPIDER: 'Kiss of the Spider',
        Ability.MIGHTY_RAGE_POTION: 'Mighty Rage Potion',
        Ability.OVERPOWER: 'Overpower',
        Ability.RAMPAGE: 'Rampage',
        Ability.RECKLESSNESS: 'Recklessness',
        Ability.SLAYERS_CREST: "Slayer's Crest",
        Ability.THRASH_BLADE_PROC: 'Thrash Blade Proc',
        Ability.WHIRLWIND: 'Whirlwind',
        Ability.WHIRLWIND_MAIN: 'Whirlwind Main',
        Ability.WHIRLWIND_OFF: 'Whirlwind Off',
        Ability.WHITE: 'White Hit',
        Ability.WHITE_MAIN: 'White Hit Main',
        Ability.WHITE_OFF: 'White Hit Off',
        Ability.WINDFURY_PROC: 'Windfury Proc',
    }

    on_use_effect_to_cd_end_event_type = {
        OnUseEffect.KISS_OF_THE_SPIDER: EventType.KISS_OF_THE_SPIDER_CD_END,
        OnUseEffect.SLAYERS_CREST: EventType.SLAYERS_CREST_CD_END,

        OnUseEffect.JUJU_FLURRY: EventType.JUJU_FLURRY_CD_END,
        OnUseEffect.MIGHTY_RAGE_POTION: EventType.MIGHTY_RAGE_POTION_CD_END,
    }

    statistics_ability_mapping = {
        Ability.BLOODTHIRST: Ability.BLOODTHIRST,
        Ability.EXECUTE: Ability.EXECUTE,
        Ability.HAND_OF_JUSTICE_PROC: Ability.HAND_OF_JUSTICE_PROC,
        Ability.HEROIC_STRIKE: Ability.HEROIC_STRIKE,
        Ability.IRONFOE_PROC: Ability.IRONFOE_PROC,
        Ability.OVERPOWER: Ability.OVERPOWER,
        Ability.THRASH_BLADE_PROC: Ability.THRASH_BLADE_PROC,
        Ability.WHIRLWIND: Ability.WHIRLWIND,
        Ability.WHIRLWIND_MAIN: Ability.WHIRLWIND,
        Ability.WHIRLWIND_OFF: Ability.WHIRLWIND,
        Ability.WHITE_MAIN: Ability.WHITE,
        Ability.WHITE_OFF: Ability.WHITE,
        Ability.WINDFURY_PROC: Ability.WINDFURY_PROC,
    }
