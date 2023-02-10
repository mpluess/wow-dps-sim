""" http://web.archive.org/web/20130810120034/http://elitistjerks.com/f81/t22705-dps_compendium/ """

from collections import defaultdict

from wow_dps_sim.enums import OnUseEffect

_FLASK_OF_RELENTLESS_ASSAULT_ADDITIONAL_AP = 120
_ROASTED_CLEFTHOOF_ADDITIONAL_STRENGTH = 20
_ADAMANTITE_SHARPENING_STONE_ADDITIONAL_DAMAGE = (12, 12)
_ADAMANTITE_SHARPENING_STONE_ADDITIONAL_CRIT_RATING = 14

CONSUMABLE_STATS = defaultdict(int, {
    'ap': _FLASK_OF_RELENTLESS_ASSAULT_ADDITIONAL_AP,
    'crit_rating': _ADAMANTITE_SHARPENING_STONE_ADDITIONAL_CRIT_RATING,
    # Applies to both hands
    'damage_range_main_hand': _ADAMANTITE_SHARPENING_STONE_ADDITIONAL_DAMAGE,
    'damage_range_off_hand': _ADAMANTITE_SHARPENING_STONE_ADDITIONAL_DAMAGE,
    'str': _ROASTED_CLEFTHOOF_ADDITIONAL_STRENGTH
})
CONSUMABLE_ON_USE_EFFECTS = {
    OnUseEffect.DRUMS_OF_BATTLE,
    OnUseEffect.HASTE_POTION,
}
