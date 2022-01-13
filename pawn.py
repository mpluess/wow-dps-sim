AP = 0.283
STR = 0.623
CRIT = 0.693
AGI = 0.508
HIT = 0.607
HASTE = 0.733
EXP = 0.866
ARP = 0.101

item_ap = 0
item_str = 47
item_crit = 0
item_agi = 0
item_hit = 19
item_haste = 35
item_exp = 0
item_arp = 0

pawn = (
    item_ap*AP
    + item_str*STR
    + item_crit*CRIT
    + item_agi*AGI
    + item_hit*HIT
    + item_haste*HASTE
    + item_exp*EXP
    + item_arp*ARP
)
print(f'{pawn:.2f}')
