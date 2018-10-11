from collections import defaultdict
import copy


def calc_unbuffed_stats(race, class_, spec, items):
    stats = _base_stats(race, class_)
    stats = _merge_stats(stats, _spec_stats(class_, spec))
    stats = _merge_stats(stats, _item_stats(items))
    stats = _merge_stats(stats, _enchant_stats(class_, spec))
    stats = _apply_primary_stats_effects(race, class_, spec, stats)
    stats = _add_tertiary_stats(race, class_, spec, stats)

    return stats


def calc_partial_buffed_permanent_stats(faction, race, class_, spec, items):
    stats = _base_stats(race, class_)
    stats = _merge_stats(stats, _spec_stats(class_, spec))
    stats = _merge_stats(stats, _item_stats(items))
    stats = _merge_stats(stats, _enchant_stats(class_, spec))
    stats = _merge_stats(stats, _permanent_buff_flat_stats(faction))
    stats = _merge_stats(stats, _consumable_stats())

    return stats


def finalize_buffed_stats(faction, race, class_, spec, stats):
    stats = _apply_permanent_buff_percentage_effects(faction, stats)
    stats = _apply_primary_stats_effects(race, class_, spec, stats)
    stats = _add_tertiary_stats(race, class_, spec, stats)

    return stats


def _merge_stats(stats_1, stats_2):
    merged_stats = copy.copy(stats_1)
    for stat_key, stat_value in stats_2.items():
        if stat_key in merged_stats:
            if isinstance(stat_value, tuple):
                merged_stats[stat_key] = (merged_stats[stat_key][0] + stat_value[0], merged_stats[stat_key][1] + stat_value[1])
            else:
                merged_stats[stat_key] += stat_value
        else:
            merged_stats[stat_key] = stat_value

    return merged_stats


def _base_stats(race, class_):
    stats = defaultdict(int)
    if race == 'human' and class_ == 'warrior':
        # TODO are these really correct?
        # https://www.getmangos.eu/forums/topic/8703-level-60-stats/
        stats['agi'] = 80
        stats['int'] = 30
        stats['spi'] = 50
        stats['sta'] = 110
        stats['str'] = 120
        stats['crit'] = 5
        stats['Mace'] = 5
        stats['Sword'] = 5
        stats['damage_multiplier'] = 1.0
    else:
        raise NotImplementedError(f'Base stats for the combination race={race}, class={class_} are not implemented.')

    return stats


def _spec_stats(class_, spec):
    stats = defaultdict(int)
    if class_ == 'warrior' and spec == 'fury':
        # Berserker Stance
        stats['crit'] += 3

        # Talents
        stats['crit'] += 5
    else:
        raise NotImplementedError(f'Stats for class={class_}, spec={spec} are not implemented.')

    return stats


def _item_stats(items):
    stats = defaultdict(int)
    itemsets = dict()
    for item in items:
        for stat_key, stat_value in item['stats'].items():
            if stat_key in stats:
                stats[stat_key] += stat_value
            else:
                stats[stat_key] = stat_value
        if item['set']['name'] is not None:
            if item['set']['name'] not in itemsets:
                itemsets[item['set']['name']] = dict()
                itemsets[item['set']['name']]['count'] = 1
                itemsets[item['set']['name']]['bonuses'] = item['set']['bonuses']
            else:
                itemsets[item['set']['name']]['count'] += 1

    for name, itemset in itemsets.items():
        for n_set_pieces_for_bonus, (stat_key, stat_value) in itemset['bonuses'].items():
            if itemset['count'] >= n_set_pieces_for_bonus:
                stats[stat_key] += stat_value

    return stats


def _enchant_stats(class_, spec):
    stats = defaultdict(int)
    if class_ == 'warrior' and spec == 'fury':
        # Head
        # stats['haste'] += 1
        stats['str'] += 8

        # Back
        stats['agi'] += 3

        # Chest
        stats['agi'] += 4
        stats['int'] += 4
        stats['spi'] += 4
        stats['sta'] += 4
        stats['str'] += 4

        # Wrist
        stats['str'] += 9

        # Hands
        # stats['haste'] += 1
        stats['str'] += 7

        # Legs
        # stats['haste'] += 1
        stats['str'] += 8

        # Off Hand
        stats['str'] += 15
    else:
        raise NotImplementedError(f'Enchant stats for class={class_}, spec={spec} are not implemented.')

    return stats


def _permanent_buff_flat_stats(faction):
    """https://github.com/Sweeksprox/vanilla-wow-raid-buffs/blob/master/raidBuffs.js"""

    stats = defaultdict(int)
    if faction == 'alliance':
        # imp. battle shout 6
        stats['ap'] += 231

        # imp. blessing of might 6
        stats['ap'] += 186

        # imp. mark of the wild 7
        stats['agi'] += 16
        stats['int'] += 16
        stats['spi'] += 16
        stats['sta'] += 16
        stats['str'] += 16

        # leader of the pack
        # stats['crit'] += 3

        # trueshot aura
        stats['ap'] += 100
    else:
        raise NotImplementedError(f'Buffs for faction {faction} not implemented')

    return stats


def _consumable_stats():
    """https://docs.google.com/spreadsheets/d/1MsDWgYDIcPE_5nX6pRbea-hW9JQjYikfCDWk16l5V-8/pubhtml#"""

    stats = defaultdict(int)

    # R.O.I.D.S.
    stats['str'] += 25

    # Elixir of the Mongoose
    stats['agi'] += 25
    stats['crit'] += 2

    # Juju Power
    stats['str'] += 30

    # Juju Might
    stats['ap'] += 40

    # Blessed Sunfruit
    stats['str'] += 10

    # Dense Sharpening Stone / Weightstone
    stats['damage_range_main_hand'] = (8, 8)

    # Elemental Sharpening Stone
    stats['crit'] += 2

    return stats


def _apply_permanent_buff_percentage_effects(faction, stats):
    stats = copy.copy(stats)

    if faction == 'alliance':
        # blessing of kings
        stats['agi'] = round(stats['agi'] * 1.1)
        stats['int'] = round(stats['int'] * 1.1)
        stats['spi'] = round(stats['spi'] * 1.1)
        stats['sta'] = round(stats['sta'] * 1.1)
        stats['str'] = round(stats['str'] * 1.1)
    else:
        raise NotImplementedError(f'Buffs for faction {faction} not implemented')

    return stats


def _apply_primary_stats_effects(race, class_, spec, stats):
    stats = copy.copy(stats)

    if class_ == 'warrior' and spec == 'fury':
        stats['ap'] += stats['str'] * 2
        stats['armor'] += stats['agi'] * 2
        stats['crit'] += stats['agi'] / 20
    else:
        raise NotImplementedError(
            f'Primary stats effects for class={class_}, spec={spec} are not implemented.')

    return stats


def _add_tertiary_stats(race, class_, spec, stats):
    stats = copy.copy(stats)

    if class_ == 'warrior' and spec == 'fury':
        stats['health'] = 1509 + min(stats['sta'], 20) * 1 + max(stats['sta'] - 20, 0) * 10

        weapon_type_main_hand = stats['weapon_type_main_hand']
        stats['weapon_skill_bonus_main_hand'] = stats[weapon_type_main_hand] if weapon_type_main_hand in stats else 0
        weapon_type_off_hand = stats['weapon_type_off_hand']
        stats['weapon_skill_bonus_off_hand'] = stats[weapon_type_off_hand] if weapon_type_off_hand in stats else 0
    else:
        raise NotImplementedError(
            f'Primary stats effects for class={class_}, spec={spec} are not implemented.')

    return stats
