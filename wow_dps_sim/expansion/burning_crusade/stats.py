import copy

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

        stats['ap'] *= knowledge.BERSERKER_STANCE_AP_MULTIPLIER

        return stats

    @staticmethod
    def add_tertiary_stats(race, class_, spec, stats):
        stats = copy.copy(stats)

        if class_ == 'warrior' and spec == 'fury':
            # TODO No idea if this is still correct
            stats['health'] = 1509 + min(stats['sta'], 20) * 1 + max(stats['sta'] - 20, 0) * 10

            weapon_type_main_hand = stats['weapon_type_main_hand']
            stats['weapon_skill_bonus_main_hand'] = stats[weapon_type_main_hand] if weapon_type_main_hand in stats else 0
            weapon_type_off_hand = stats['weapon_type_off_hand']
            stats['weapon_skill_bonus_off_hand'] = stats[weapon_type_off_hand] if weapon_type_off_hand in stats else 0
        else:
            raise NotImplementedError(
                f'Primary stats effects for class={class_}, spec={spec} are not implemented.')

        return stats
