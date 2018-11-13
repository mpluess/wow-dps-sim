from collections import defaultdict
import copy

from wow_dps_sim.helpers import from_module_import_x
from wow_dps_sim.main_config import EXPANSION_MODULE
buff_config = from_module_import_x(EXPANSION_MODULE, 'buff_config')
consumable_config = from_module_import_x(EXPANSION_MODULE, 'consumable_config')
enchant_config = from_module_import_x(EXPANSION_MODULE, 'enchant_config')
knowledge = from_module_import_x(EXPANSION_MODULE, 'knowledge')
Stats = from_module_import_x(EXPANSION_MODULE + '.stats', 'Stats')


def calc_unbuffed_stats(race, class_, spec, items):
    stats = _base_stats(race, class_)
    stats = _merge_stats(stats, _spec_stats(class_, spec))
    stats = _merge_stats(stats, _item_stats(items))
    stats = _merge_stats(stats, _enchant_stats(class_, spec))
    stats = apply_berserker_stance_effects(stats)
    stats = Stats.apply_primary_stats_effects(race, class_, spec, stats)
    stats = Stats.add_tertiary_stats(race, class_, spec, stats)

    return stats


def calc_partial_buffed_permanent_stats(faction, race, class_, spec, items):
    stats = _base_stats(race, class_)
    stats = _merge_stats(stats, _spec_stats(class_, spec))
    stats = _merge_stats(stats, _item_stats(items))
    stats = _merge_stats(stats, _enchant_stats(class_, spec))
    stats = _merge_stats(stats, _permanent_buff_flat_stats(faction))
    stats = _merge_stats(stats, _consumable_stats())

    return stats


def apply_berserker_stance_effects(stats):
    stats = copy.copy(stats)

    stats['crit'] += knowledge.BERSERKER_STANCE_ADDITIONAL_CRIT

    return stats


def finalize_buffed_stats(faction, race, class_, spec, stats):
    stats = _apply_permanent_buff_percentage_effects(faction, stats)
    stats = Stats.apply_primary_stats_effects(race, class_, spec, stats)
    stats = Stats.add_tertiary_stats(race, class_, spec, stats)

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
    if race in knowledge.BASE_STATS and class_ in knowledge.BASE_STATS[race]:
        stats = knowledge.BASE_STATS[race][class_]
    else:
        raise NotImplementedError(f'Base stats for the combination race={race}, class={class_} are not implemented.')

    return stats


def _spec_stats(class_, spec):
    if class_ in knowledge.SPEC_STATS and spec in knowledge.SPEC_STATS[class_]:
        stats = knowledge.SPEC_STATS[class_][spec]
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
    if class_ in enchant_config.ENCHANT_STATS and spec in enchant_config.ENCHANT_STATS[class_]:
        stats = enchant_config.ENCHANT_STATS[class_][spec]
    else:
        raise NotImplementedError(f'Enchant stats for class={class_}, spec={spec} are not implemented.')

    return stats


def _permanent_buff_flat_stats(faction):
    if faction in buff_config.PERMANENT_BUFF_FLAT_STATS:
        stats = buff_config.PERMANENT_BUFF_FLAT_STATS[faction]
    else:
        raise NotImplementedError(f'Buffs for faction {faction} not implemented')

    return stats


def _consumable_stats():
    return consumable_config.CONSUMABLE_STATS


def _apply_permanent_buff_percentage_effects(faction, stats):
    stats = copy.copy(stats)

    if faction in buff_config.PERMANENT_BUFF_MULTIPLIERS:
        for stat in buff_config.PERMANENT_BUFF_MULTIPLIERS[faction].keys():
            stats[stat] = round(stats[stat] * buff_config.PERMANENT_BUFF_MULTIPLIERS[faction][stat])
    else:
        raise NotImplementedError(f'Buffs for faction {faction} not implemented')

    return stats
