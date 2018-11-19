import copy

from . import knowledge
import wow_dps_sim.expansion.stats


class Stats(wow_dps_sim.expansion.stats.Stats):
    @staticmethod
    def add_tertiary_stats(race, class_, spec, stats):
        stats = copy.copy(stats)

        if class_ == 'warrior' and spec == 'fury':
            stats['health'] = 1509 + min(stats['sta'], 20) * 1 + max(stats['sta'] - 20, 0) * 10

            weapon_type_main_hand = stats['weapon_type_main_hand']
            stats['weapon_skill_bonus_main_hand'] = stats[
                weapon_type_main_hand] if weapon_type_main_hand in stats else 0
            weapon_type_off_hand = stats['weapon_type_off_hand']
            stats['weapon_skill_bonus_off_hand'] = stats[weapon_type_off_hand] if weapon_type_off_hand in stats else 0
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
        return stats

    @staticmethod
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
            ('Crit', stats['crit']),
            ('Hit', stats['hit']),
            ('Haste', stats['haste']),
            ('Axes', stats['Axe']),
            ('Daggers', stats['Dagger']),
            ('Maces', stats['Mace']),
            ('Swords', stats['Sword']),
        ]

        return base_stats, primary_stats, secondary_stats
