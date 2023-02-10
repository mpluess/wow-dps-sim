from collections import defaultdict
import copy

from wow_dps_sim.helpers import from_module_import_x


class Stats:
    def __init__(self, expansion):
        expansion_module = 'wow_dps_sim.expansion.' + expansion
        self.buff_config = from_module_import_x(expansion_module, 'buff_config')
        self.consumable_config = from_module_import_x(expansion_module, 'consumable_config')
        self.enchant_config = from_module_import_x(expansion_module, 'enchant_config')
        self.knowledge = from_module_import_x(expansion_module, 'knowledge')
        self.ExpansionSpecificStats = from_module_import_x(expansion_module + '.stats', 'Stats')

    def calc_unbuffed_stats(self, race, class_, spec, items, socket_stats):
        stats = self._base_stats(race, class_)
        stats = self.merge_stats(stats, self._spec_stats(class_, spec))
        stats = self.merge_stats(stats, self._item_stats(items))
        stats = self.merge_stats(stats, socket_stats)
        stats = self.merge_stats(stats, self._enchant_stats(class_, spec))
        stats = self.ExpansionSpecificStats.apply_berserker_stance_flat_effects(stats)
        stats = self.ExpansionSpecificStats.apply_berserker_stance_percentage_effects(stats)
        stats = self.ExpansionSpecificStats.apply_primary_stats_effects(race, class_, spec, stats)
        stats = self.ExpansionSpecificStats.add_tertiary_stats(race, class_, spec, stats)

        return stats

    def calc_partial_buffed_permanent_stats(self, faction, race, class_, spec, items, socket_stats):
        stats = self._base_stats(race, class_)
        stats = self.merge_stats(stats, self._spec_stats(class_, spec))
        stats = self.merge_stats(stats, self._item_stats(items))
        stats = self.merge_stats(stats, socket_stats)
        stats = self.merge_stats(stats, self._enchant_stats(class_, spec))
        stats = self.merge_stats(stats, self._permanent_buff_flat_stats(faction))
        stats = self.merge_stats(stats, self._consumable_stats())

        return stats

    def finalize_buffed_stats(self, faction, race, class_, spec, stats):
        stats = self._apply_permanent_buff_percentage_effects(faction, stats)
        stats = self.ExpansionSpecificStats.apply_primary_stats_effects(race, class_, spec, stats)
        stats = self.ExpansionSpecificStats.add_tertiary_stats(race, class_, spec, stats)

        return stats

    @staticmethod
    def merge_stats(stats_1, stats_2):
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

    def _base_stats(self, race, class_):
        if race in self.knowledge.BASE_STATS and class_ in self.knowledge.BASE_STATS[race]:
            stats = self.knowledge.BASE_STATS[race][class_]
        else:
            raise NotImplementedError(f'Base stats for the combination race={race}, class={class_} are not implemented.')

        return stats

    def _spec_stats(self, class_, spec):
        if class_ in self.knowledge.SPEC_STATS and spec in self.knowledge.SPEC_STATS[class_]:
            stats = self.knowledge.SPEC_STATS[class_][spec]
        else:
            raise NotImplementedError(f'Stats for class={class_}, spec={spec} are not implemented.')

        return stats

    @staticmethod
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

    def _enchant_stats(self, class_, spec):
        if class_ in self.enchant_config.ENCHANT_STATS and spec in self.enchant_config.ENCHANT_STATS[class_]:
            stats = self.enchant_config.ENCHANT_STATS[class_][spec]
        else:
            raise NotImplementedError(f'Enchant stats for class={class_}, spec={spec} are not implemented.')

        return stats

    def _permanent_buff_flat_stats(self, faction):
        if faction in self.buff_config.PERMANENT_BUFF_FLAT_STATS:
            stats = self.buff_config.PERMANENT_BUFF_FLAT_STATS[faction]
        else:
            raise NotImplementedError(f'Buffs for faction {faction} not implemented')

        return stats

    def _consumable_stats(self):
        return self.consumable_config.CONSUMABLE_STATS

    def _apply_permanent_buff_percentage_effects(self, faction, stats):
        stats = copy.copy(stats)

        if faction in self.buff_config.PERMANENT_BUFF_MULTIPLIERS:
            for stat in self.buff_config.PERMANENT_BUFF_MULTIPLIERS[faction].keys():
                if type(stats[stat]) == int:
                    stats[stat] = round(stats[stat] * self.buff_config.PERMANENT_BUFF_MULTIPLIERS[faction][stat])
                else:
                    stats[stat] = stats[stat] * self.buff_config.PERMANENT_BUFF_MULTIPLIERS[faction][stat]
        else:
            raise NotImplementedError(f'Buffs for faction {faction} not implemented')

        return stats
