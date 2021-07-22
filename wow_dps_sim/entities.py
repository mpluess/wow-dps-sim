from collections import defaultdict
from statistics import mean

from .constants import Constants
from .enums import Stance
from .helpers import from_module_import_x
from .stats import Stats


class AbilityLogEntry:
    def __init__(self, ability, attack_result, damage):
        self.ability = ability
        self.attack_result = attack_result
        self.damage = damage


class Event:
    def __init__(self, time_, count, event_type):
        self.time = time_
        self.count = count
        self.event_type = event_type

    def __lt__(self, other):
        # Comparing float equality here is not really optimal, but the actual game code probably does the same.
        # Best option would probably be to discretize time and use ints.
        if self.time != other.time:
            return self.time < other.time
        elif self.count != other.count:
            return self.count < other.count
        else:
            raise ValueError(f'__lt__: compared objects have the same time and count')

    def __repr__(self):
        return f'time={self.time}, count={self.count}, event_type={self.event_type}'


class WhiteHitEvent(Event):
    def __init__(self, time_, count, event_type):
        super().__init__(time_, count, event_type)

        self.has_flurry = False

    def __repr__(self):
        return super().__repr__() + f', has_flurry={self.has_flurry}'


class Player:
    def __init__(
        self, faction, race, class_, spec, items, items_execute, meta_socket_active,
        expansion=None, socket_stats=None,
        partial_buffed_permanent_stats=None, partial_buffed_permanent_stats_execute=None,
        procs=None,  # procs_execute=None,
        on_use_effects=None,  # on_use_effects_execute=None
    ):
        self.faction = faction
        self.race = race
        self.class_ = class_
        self.spec = spec
        self.items = items
        self.items_execute = items_execute
        self.meta_socket_active = meta_socket_active

        if partial_buffed_permanent_stats is None:
            assert socket_stats is not None and expansion is not None
            stats = Stats(expansion)
            self.partial_buffed_permanent_stats = stats.calc_partial_buffed_permanent_stats(faction, race, class_, spec, items, socket_stats)
        else:
            assert socket_stats is None and expansion is None
            self.partial_buffed_permanent_stats = partial_buffed_permanent_stats

        if partial_buffed_permanent_stats_execute is None:
            assert socket_stats is not None and expansion is not None
            stats = Stats(expansion)
            self.partial_buffed_permanent_stats_execute = stats.calc_partial_buffed_permanent_stats(faction, race, class_, spec, items_execute, socket_stats)
        else:
            assert socket_stats is None and expansion is None
            self.partial_buffed_permanent_stats_execute = partial_buffed_permanent_stats_execute

        if procs is None:
            buff_config = from_module_import_x('wow_dps_sim.expansion.' + expansion, 'buff_config')
            enchant_config = from_module_import_x('wow_dps_sim.expansion.' + expansion, 'enchant_config')
            self.procs = self._create_proc_set(items, set.union(buff_config.BUFF_PROCS, enchant_config.ENCHANT_PROCS))
        else:
            self.procs = procs

        # if procs_execute is None:
        #     buff_config = from_module_import_x('wow_dps_sim.expansion.' + expansion, 'buff_config')
        #     enchant_config = from_module_import_x('wow_dps_sim.expansion.' + expansion, 'enchant_config')
        #     self.procs_execute = self._create_proc_set(items_execute, set.union(buff_config.BUFF_PROCS, enchant_config.ENCHANT_PROCS))
        # else:
        #     self.procs_execute = procs_execute

        if on_use_effects is None:
            buff_config = from_module_import_x('wow_dps_sim.expansion.' + expansion, 'buff_config')
            consumable_config = from_module_import_x('wow_dps_sim.expansion.' + expansion, 'consumable_config')
            self.on_use_effects = self._create_on_use_effect_set(items, set.union(buff_config.BUFF_ON_USE_EFFECTS, consumable_config.CONSUMABLE_ON_USE_EFFECTS))
        else:
            self.on_use_effects = on_use_effects

        # if on_use_effects_execute is None:
        #     buff_config = from_module_import_x('wow_dps_sim.expansion.' + expansion, 'buff_config')
        #     consumable_config = from_module_import_x('wow_dps_sim.expansion.' + expansion, 'consumable_config')
        #     self.on_use_effects_execute = self._create_on_use_effect_set(items_execute, set.union(buff_config.BUFF_ON_USE_EFFECTS, consumable_config.CONSUMABLE_ON_USE_EFFECTS))
        # else:
        #     self.on_use_effects_execute = on_use_effects_execute

        self.buffs = set()
        self.stance = Stance.BERSERKER

    @classmethod
    def from_player(cls, player):
        return cls(
            player.faction, player.race, player.class_, player.spec, player.items, player.items_execute, player.meta_socket_active,
            partial_buffed_permanent_stats=player.partial_buffed_permanent_stats,
            partial_buffed_permanent_stats_execute=player.partial_buffed_permanent_stats_execute,
            procs=player.procs,
            # procs_execute=player.procs_execute,
            on_use_effects=player.on_use_effects,
            # on_use_effects_execute=player.on_use_effects_execute,
        )

    @staticmethod
    def _create_proc_set(items, additional_procs):
        list_of_proc_sets = [item['procs'] for item in items] + [additional_procs]
        return set.union(*list_of_proc_sets)

    @staticmethod
    def _create_on_use_effect_set(items, additional_on_use_effects):
        list_of_on_use_effect_sets = [item['on_use_effects'] for item in items] + [additional_on_use_effects]
        return set.union(*list_of_on_use_effect_sets)


class Result:
    def __init__(self, dps, statistics):
        self.dps = dps
        self.statistics = statistics

    @classmethod
    def from_ability_log(cls, dps, ability_log):
        statistics = Result._create_statistics()
        for log_entry in ability_log:
            ability = Constants.statistics_ability_mapping[log_entry.ability]
            statistics[ability]['damage'].append(log_entry.damage)
            statistics[ability]['attack_result'][log_entry.attack_result] += 1

        return cls(dps, statistics)

    @staticmethod
    def get_merged_result(result_list):
        def merge_statistics(result_list):
            statistics = Result._create_statistics()
            for result in result_list:
                for ability in result.statistics.keys():
                    statistics[ability]['damage'].extend(result.statistics[ability]['damage'])
                    for attack_result, count in result.statistics[ability]['attack_result'].items():
                        statistics[ability]['attack_result'][attack_result] += count

            return statistics

        dps = mean([result.dps for result in result_list])
        statistics = merge_statistics(result_list)

        return Result(dps, statistics)

    @staticmethod
    def _create_statistics():
        return defaultdict(lambda: {'damage': [], 'attack_result': defaultdict(int)})

    def __repr__(self):
        total_damage = sum([sum(d['damage']) for d in self.statistics.values()])
        output = f'DPS: {self.dps:.2f}\n\n'
        for ability, ability_statistics in sorted(self.statistics.items(), key=lambda t: sum(t[1]['damage']), reverse=True):
            damage_sum = sum(ability_statistics['damage'])
            non_zero_damage_values = [damage for damage in ability_statistics['damage'] if damage > 0]
            output += f"{Constants.ability_names_lookup[ability]} {damage_sum} {(damage_sum / total_damage * 100):.2f}"
            if len(non_zero_damage_values) > 0:
                output += f" min={min(non_zero_damage_values)} max={max(non_zero_damage_values)} mean={round(mean(non_zero_damage_values))}\n"
        output += '\n'
        for ability, ability_statistics in sorted(self.statistics.items(), key=lambda t: sum(t[1]['damage']), reverse=True):
            total_count = sum(ability_statistics['attack_result'].values())
            output += Constants.ability_names_lookup[ability]
            for attack_result, count in sorted(ability_statistics['attack_result'].items(), key=lambda t: t[1], reverse=True):
                output += f' {attack_result} {count} {(count / total_count * 100):.2f}'
            output += '\n'

        return output
