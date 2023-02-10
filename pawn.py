STR = 1.02
HIT = 0.726
CRIT = 0.99
HASTE = 0.983
EXP = 1.404
ARP = 0.206

AGI = CRIT * 0.7333
AP = STR / 2.2

item_str = 0
item_agi = 0
item_hit = 0
item_crit = 20
item_haste = 0
item_exp = 0
item_ap = 46
item_arp = 112

pawn = (
    item_str*STR
    + item_agi*AGI
    + item_hit*HIT
    + item_crit*CRIT
    + item_haste*HASTE
    + item_exp*EXP
    + item_ap*AP
    + item_arp*ARP
)
print(f'{pawn:.2f}')
