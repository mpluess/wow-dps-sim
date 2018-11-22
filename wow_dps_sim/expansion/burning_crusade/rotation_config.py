from . import knowledge


# BT 30 + WW 25 + HS 13 = 68
# With pre BIS gear, it seems optimal to use HS already at about 60 rage.
HEROIC_STRIKE_MIN_RAGE_THRESHOLD = 60

# Only OP on rage <= 45 vs. OP regardless of rage:
# @ pre-raid BIS, OP regardless of rage is about 1 DPS better than on rage <= 45.
# @ Naxx BIS, OP regardless of rage is about 13 DPS better than on rage <= 45.
OVERPOWER_MAX_RAGE_THRESHOLD = knowledge.MAX_RAGE

OVERPOWER_MIN_BLOODTHIRST_CD_LEFT = 1.5
OVERPOWER_MIN_WHIRLWIND_CD_LEFT = 1.5

RAMPAGE_MIN_BLOODTHIRST_CD_LEFT = 1.0
RAMPAGE_MIN_WHIRLWIND_CD_LEFT = 1.0
RAMPAGE_REFRESH_THRESHOLD = 5.0
