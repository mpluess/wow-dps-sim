from collections import defaultdict
import copy

import vanilla_utils.knowledge as knowledge


def calc_unbuffed_stats(race, class_, spec, items):
    stats = _base_stats(race, class_)
    stats = _merge_stats(stats, _spec_stats(class_, spec))
    stats = _merge_stats(stats, _item_stats(items))
    stats = _merge_stats(stats, _enchant_stats(class_, spec))
    stats = apply_berserker_stance_effects(stats)
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


def apply_berserker_stance_effects(stats):
    stats = copy.copy(stats)

    stats['crit'] += knowledge.BERSERKER_STANCE_ADDITIONAL_CRIT

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
    if race in knowledge.BASE_STATS and class_ in knowledge.BASE_STATS[race]:
        stats = knowledge.BASE_STATS[race][class_]
    else:
        raise NotImplementedError(f'Base stats for the combination race={race}, class={class_} are not implemented.')

    return stats


def _spec_stats(class_, spec):
    stats = defaultdict(int)
    if class_ == 'warrior' and spec == 'fury':
        stats['crit'] += knowledge.CRUELTY_ADDITIONAL_CRIT
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
        # stats['haste'] += knowledge.ENCHANT_HEAD_HASTE
        stats['str'] += knowledge.ENCHANT_HEAD_STRENGTH

        # Back
        stats['agi'] += knowledge.ENCHANT_BACK_AGILITY

        # Chest
        stats['agi'] += knowledge.ENCHANT_CHEST_STATS
        stats['int'] += knowledge.ENCHANT_CHEST_STATS
        stats['spi'] += knowledge.ENCHANT_CHEST_STATS
        stats['sta'] += knowledge.ENCHANT_CHEST_STATS
        stats['str'] += knowledge.ENCHANT_CHEST_STATS

        # Wrist
        stats['str'] += knowledge.ENCHANT_WRIST_STRENGTH

        # Hands
        # stats['haste'] += knowledge.ENCHANT_HANDS_HASTE
        stats['str'] += knowledge.ENCHANT_HANDS_STRENGTH

        # Legs
        # stats['haste'] += knowledge.ENCHANT_LEGS_HASTE
        stats['str'] += knowledge.ENCHANT_LEGS_STRENGTH

        # Off Hand
        # stats['str'] += knowledge.ENCHANT_OFF_HAND_STRENGTH
    else:
        raise NotImplementedError(f'Enchant stats for class={class_}, spec={spec} are not implemented.')

    return stats


def _permanent_buff_flat_stats(faction):
    """https://github.com/Sweeksprox/vanilla-wow-raid-buffs/blob/master/raidBuffs.js"""

    stats = defaultdict(int)
    if faction == 'alliance':
        stats['ap'] += knowledge.BATTLE_SHOUT_ADDITIONAL_AP

        stats['ap'] += knowledge.BLESSING_OF_MIGHT_ADDITIONAL_AP

        stats['agi'] += knowledge.MARK_OF_THE_WILD_ADDITIONAL_STATS
        stats['int'] += knowledge.MARK_OF_THE_WILD_ADDITIONAL_STATS
        stats['spi'] += knowledge.MARK_OF_THE_WILD_ADDITIONAL_STATS
        stats['sta'] += knowledge.MARK_OF_THE_WILD_ADDITIONAL_STATS
        stats['str'] += knowledge.MARK_OF_THE_WILD_ADDITIONAL_STATS

        # stats['crit'] += knowledge.LEADER_OF_THE_PACK_ADDITIONAL_CRIT

        stats['ap'] += knowledge.TRUESHOT_AURA_ADDITIONAL_AP
    else:
        raise NotImplementedError(f'Buffs for faction {faction} not implemented')

    return stats


def _consumable_stats():
    """https://docs.google.com/spreadsheets/d/1MsDWgYDIcPE_5nX6pRbea-hW9JQjYikfCDWk16l5V-8/pubhtml#"""

    stats = defaultdict(int)
    stats['str'] += knowledge.ROIDS_ADDITIONAL_STRENGTH
    stats['agi'] += knowledge.ELIXIR_OF_THE_MONGOOSE_ADDITIONAL_AGILITY
    stats['crit'] += knowledge.ELIXIR_OF_THE_MONGOOSE_ADDITIONAL_CRIT
    stats['str'] += knowledge.JUJU_POWER_ADDITIONAL_STRENGTH
    stats['ap'] += knowledge.JUJU_MIGHT_ADDITIONAL_AP
    stats['str'] += knowledge.BLESSED_SUNFRUIT_ADDITIONAL_STRENGTH

    # stats['damage_range_main_hand'] = knowledge.DENSE_SHARPENING_STONE_ADDITIONAL_DAMAGE
    stats['crit'] += knowledge.ELEMENTAL_SHARPENING_STONE_ADDITIONAL_CRIT

    stats['crit'] += knowledge.ELEMENTAL_SHARPENING_STONE_ADDITIONAL_CRIT

    return stats


def _apply_permanent_buff_percentage_effects(faction, stats):
    stats = copy.copy(stats)

    if faction == 'alliance':
        stats['agi'] = round(stats['agi'] * knowledge.BLESSING_OF_KINGS_STATS_MULTIPLIER)
        stats['int'] = round(stats['int'] * knowledge.BLESSING_OF_KINGS_STATS_MULTIPLIER)
        stats['spi'] = round(stats['spi'] * knowledge.BLESSING_OF_KINGS_STATS_MULTIPLIER)
        stats['sta'] = round(stats['sta'] * knowledge.BLESSING_OF_KINGS_STATS_MULTIPLIER)
        stats['str'] = round(stats['str'] * knowledge.BLESSING_OF_KINGS_STATS_MULTIPLIER)
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
