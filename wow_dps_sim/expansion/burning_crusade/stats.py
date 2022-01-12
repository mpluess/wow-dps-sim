import copy
import math

from . import knowledge
import wow_dps_sim.expansion.stats


class Stats(wow_dps_sim.expansion.stats.Stats):
    @staticmethod
    def apply_primary_stats_effects(race, class_, spec, stats):
        stats = copy.copy(stats)

        if class_ == 'warrior' and spec == 'fury':
            stats['ap'] += stats['str'] * 2
            stats['armor'] += stats['agi'] * 2
            stats['crit'] += stats['agi'] / 33

            stats['crit'] += stats['crit_rating'] / 22.08
            stats['haste'] += stats['haste_rating'] / 15.77
            stats['hit'] += stats['hit_rating'] / 15.77
            stats['minus_dodge'] += math.floor(stats['exp_rating'] / 3.9423) * 0.25
        else:
            raise NotImplementedError(
                f'Primary stats effects for class={class_}, spec={spec} are not implemented.')

        return stats

    @staticmethod
    def apply_berserker_stance_flat_effects(stats):
        stats = copy.copy(stats)

        stats['crit'] += knowledge.BERSERKER_STANCE_ADDITIONAL_CRIT

        return stats

    @staticmethod
    def apply_berserker_stance_percentage_effects(stats):
        stats = copy.copy(stats)

        stats['ap'] = round(stats['ap'] * knowledge.BERSERKER_STANCE_AP_MULTIPLIER)

        return stats

    @staticmethod
    def add_tertiary_stats(race, class_, spec, stats):
        stats = copy.copy(stats)

        if class_ == 'warrior' and spec == 'fury':
            stats['health'] = 4264 + stats['sta'] * 10

            weapon_type_main_hand = stats['weapon_type_main_hand']
            stats['minus_dodge_bonus_main_hand'] = stats[weapon_type_main_hand]['minus_dodge'] if weapon_type_main_hand in stats else 0
            weapon_type_off_hand = stats['weapon_type_off_hand']
            stats['minus_dodge_bonus_off_hand'] = stats[weapon_type_off_hand]['minus_dodge'] if weapon_type_off_hand in stats else 0
        else:
            raise NotImplementedError(
                f'Primary stats effects for class={class_}, spec={spec} are not implemented.')

        return stats

    @staticmethod
    def get_displayable_stats(items, stats):
        base_stats = [
            ('Items', ', '.join([item['name'] for item in items])),
            ('Health', stats['health']),
            ('Armor', stats['armor']),
        ]
        primary_stats = [
            ('Agility', stats['agi']),
            ('Intelligence', stats['int']),
            ('Spirit', stats['spi']),
            ('Stamina', stats['sta']),
            ('Strength', stats['str']),
        ]
        secondary_stats = [
            ('Attack Power', stats['ap']),
            ('Crit', f"{stats['crit']:.2f}"),
            ('Hit', f"{stats['hit']:.2f}"),
            ('Haste', f"{stats['haste']:.2f}"),
            ('Minus Dodge', f"{stats['minus_dodge']:.2f}"),
            ('Armor Penetration', stats['arp']),
        ]

        return base_stats, primary_stats, secondary_stats
