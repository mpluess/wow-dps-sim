from collections import defaultdict
from statistics import mean

from .constants import Constants
from .enums import BossDebuffs


class AbilityLogEntry:
    def __init__(self, ability, attack_result, damage):
        self.ability = ability
        self.attack_result = attack_result
        self.damage = damage


class Boss:
    def __init__(self, armor=4691, base_miss=0.086, base_dodge=0.056, debuffs=None):
        self.armor = armor
        self.base_miss = base_miss
        self.base_dodge = base_dodge
        self.debuffs = debuffs if debuffs is not None else {BossDebuffs.SUNDER_ARMOR_X5, BossDebuffs.FAERIE_FIRE, BossDebuffs.CURSE_OF_RECKLESSNESS}


class Config:
    def __init__(self, n_runs=1, logging=True, fight_duration_seconds_mu=180.0, fight_duration_seconds_sigma=20.0,
                 stat_increase_tuples=None):
        self.n_runs = n_runs
        self.logging = logging
        self.fight_duration_seconds_mu = fight_duration_seconds_mu
        self.fight_duration_seconds_sigma = fight_duration_seconds_sigma

        # [('hit', 1), ('crit', 1), ('agi', 20), ('ap', 30), ('str', 15), ('haste', 1), ('Sword', 1)]
        self.stat_increase_tuples = stat_increase_tuples if stat_increase_tuples is not None else []


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
    def __init__(self, faction, race, class_, spec, items, partial_buffed_permanent_stats):
        self.faction = faction
        self.race = race
        self.class_ = class_
        self.spec = spec
        self.items = items
        self.partial_buffed_permanent_stats = partial_buffed_permanent_stats

        self.buffs = set()


class Result:
    def __init__(self, dps, statistics):
        self.dps = dps
        self.statistics = statistics

    @classmethod
    def from_ability_log(cls, dps, ability_log):
        statistics = Result._create_statistics()
        for log_entry in ability_log:
            ability = Constants.ability_mapping[log_entry.ability]
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
        output = f'DPS: {self.dps}\n\n'
        for ability, ability_statistics in sorted(self.statistics.items(), key=lambda t: sum(t[1]['damage']), reverse=True):
            damage_sum = sum(ability_statistics['damage'])
            non_zero_damage_values = [damage for damage in ability_statistics['damage'] if damage > 0]
            output += f"{Constants.ability_names_lookup[ability]} {damage_sum} {(damage_sum / total_damage * 100):.2f}"
            output += f" min={min(non_zero_damage_values)} max={max(non_zero_damage_values)} mean={mean(non_zero_damage_values)}\n"
        output += '\n'
        for ability, ability_statistics in sorted(self.statistics.items(), key=lambda t: sum(t[1]['damage']), reverse=True):
            total_count = sum(ability_statistics['attack_result'].values())
            output += Constants.ability_names_lookup[ability]
            for attack_result, count in sorted(ability_statistics['attack_result'].items(), key=lambda t: t[1], reverse=True):
                output += f' {attack_result} {count} {(count / total_count * 100):.2f}'
            output += '\n'

        return output
