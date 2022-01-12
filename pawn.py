KINGS = True

AP = 1.0
STR = 2.0
CRIT = 2.2
AGI = 1.47
HIT = 1.8
HASTE = 1.8
EXP = 2.8

item_ap = 60
item_str = 4
item_crit = 20
item_agi = 35
item_hit = 0
item_haste = 0
item_exp = 12

pawn = (
    item_ap*AP
    + item_str*STR*(1.1 if KINGS else 1.0)
    + item_crit*CRIT
    + item_agi*AGI*(1.1 if KINGS else 1.0)
    + item_hit*HIT
    + item_haste*HASTE
    + item_exp*EXP
)
print(f'{pawn:.2f}')
