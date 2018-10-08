from collections import defaultdict
import copy


def base_stats(race, class_):
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
        stats['maces'] = 5
        stats['swords'] = 5
    else:
        raise NotImplementedError(f'Base stats for the combination race={race}, class={class_} are not implemented.')

    return stats


def spec_stats(class_, spec):
    stats = defaultdict(int)
    if class_ == 'warrior' and spec == 'fury':
        # Berserker Stance
        stats['crit'] += 3

        # Talents
        stats['crit'] += 5
    else:
        raise NotImplementedError(f'Stats for class={class_}, spec={spec} are not implemented.')

    return stats


def enchant_stats(class_, spec):
    stats = defaultdict(int)
    if class_ == 'warrior' and spec == 'fury':
        # Head
        stats['haste'] += 1

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
        stats['haste'] += 1

        # Legs
        stats['haste'] += 1

        # Off Hand
        stats['str'] += 15
    else:
        raise NotImplementedError(
            f'Enchant stats for class={class_}, spec={spec} are not implemented.')

    return stats


def item_stats(items):
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


def apply_primary_stats_effects(race, class_, spec, stats):
    stats = copy.copy(stats)

    if class_ == 'warrior' and spec == 'fury':
        stats['ap'] += stats['str'] * 2
        stats['armor'] += stats['agi'] * 2
        stats['crit'] += stats['agi'] / 20
    else:
        raise NotImplementedError(
            f'Primary stats effects for class={class_}, spec={spec} are not implemented.')

    return stats


def add_tertiary_stats(race, class_, spec, stats):
    stats = copy.copy(stats)

    if class_ == 'warrior' and spec == 'fury':
        stats['health'] = 1509 + min(stats['sta'], 20) * 1 + max(stats['sta'] - 20, 0) * 10
    else:
        raise NotImplementedError(
            f'Primary stats effects for class={class_}, spec={spec} are not implemented.')

    return stats
