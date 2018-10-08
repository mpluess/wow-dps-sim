from collections import defaultdict
import copy
from enum import auto, Enum
import heapq
import random
from statistics import mean


class Player:
    def __init__(self, stats):
        self.stats = stats

        self.buffs = set()


class Boss:
    def __init__(self, stats, debuffs):
        self.stats = stats
        self.debuffs = debuffs


class Sim:
    def __init__(self, boss, player):
        self.boss = boss
        self.player = player
        self.calcs = Calcs(boss, player)

        self.event_queue = []
        self.event_count = 0
        self.current_time_seconds = 0.0
        self.damage_done = defaultdict(int)

        self.state = {
            'rage': 0,
            'on_gcd': False,
            'bloodthirst_available': True,
            'whirlwind_available': True,
            'death_wish_available': True,
        }

        self._add_event(0.0, Event.BLOODRAGE_CD_END)
        self._add_event(0.0, Event.DEATH_WISH_CD_END)
        self._add_event(0.0, Event.RECKLESSNESS_CD_END)
        self._add_event(0.0, Event.GCD_END)
        self.next_white_hit_main = self._add_event(self.calcs.current_speed(False), Event.WHITE_HIT_MAIN)
        self.next_white_hit_off = self._add_event(self.calcs.current_speed(True), Event.WHITE_HIT_OFF)

    def get_next_event(self):
        time, _, event = heapq.heappop(self.event_queue)
        self.current_time_seconds = time

        return event

    def handle_event(self, event):
        if event == Event.BLOODRAGE_CD_END:
            self._add_rage(10)
            for i in range(10):
                self._add_event(i + 1, Event.BLOODRAGE_ADD_RAGE_OVER_TIME)
            self._add_event(60, Event.BLOODRAGE_CD_END)
        elif event == Event.BLOODRAGE_ADD_RAGE_OVER_TIME:
            self._add_rage(1)
        elif event == Event.DEATH_WISH_END:
            self.player.buffs.remove(PlayerBuffs.DEATH_WISH)
        elif event == Event.DEATH_WISH_CD_END:
            self.state['death_wish_available'] = True
            self._apply_death_wish()
        elif event == Event.RECKLESSNESS_END:
            self.player.buffs.remove(PlayerBuffs.RECKLESSNESS)
        elif event == Event.RECKLESSNESS_CD_END:
            self.player.buffs.add(PlayerBuffs.RECKLESSNESS)
            self._add_event(15, Event.RECKLESSNESS_END)
            self._add_event(1800, Event.RECKLESSNESS_CD_END)
        elif event == Event.BLOODTHIRST_CD_END:
            self.state['bloodthirst_available'] = True
        elif event == Event.WHIRLWIND_CD_END:
            self.state['whirlwind_available'] = True
        elif event == Event.GCD_END:
            self.state['on_gcd'] = False
            self._do_rota()
        elif event == Event.WHITE_HIT_MAIN:
            damage, rage = self.calcs.white_hit(False)
            self._apply_damage('white_main', damage)
            self._add_rage(rage)
            self.next_white_hit_main = self._add_event(self.calcs.current_speed(False), Event.WHITE_HIT_MAIN)
        elif event == Event.WHITE_HIT_OFF:
            damage, rage = self.calcs.white_hit(True)
            self._apply_damage('white_off', damage)
            self._add_rage(rage)
            self.next_white_hit_off = self._add_event(self.calcs.current_speed(True), Event.WHITE_HIT_OFF)
        elif event == Event.RAGE_GAINED:
            if self.state['death_wish_available']:
                self._apply_death_wish()
            if not self.state['on_gcd']:
                self._do_rota()

    def _add_event(self, time_delta, event):
        event_tuple = (self.current_time_seconds + time_delta, self.event_count, event)
        heapq.heappush(self.event_queue, event_tuple)
        self.event_count += 1

        return event_tuple

    def _add_rage(self, amount):
        if amount > 0:
            self.state['rage'] = min(100, self.state['rage'] + amount)
            self._add_event(0, Event.RAGE_GAINED)

    def _apply_damage(self, ability, damage):
        assert damage >= 0
        self.damage_done[ability] += damage

    def _apply_death_wish(self):
        if self.state['rage'] >= 10:
            self.player.buffs.add(PlayerBuffs.DEATH_WISH)
            self.state['death_wish_available'] = False
            self.state['rage'] -= 10
            self._add_event(30, Event.DEATH_WISH_END)
            self._add_event(180, Event.DEATH_WISH_CD_END)

    def _do_rota(self):
        if self.state['bloodthirst_available'] and self.state['rage'] >= 30:
            damage, rage = self.calcs.bloodthirst()
            self.state['bloodthirst_available'] = False
            self._apply_damage('bloodthirst', damage)
            self.state['rage'] -= 30
            self._add_event(6, Event.BLOODTHIRST_CD_END)
            self.state['on_gcd'] = True
            self._add_event(1.5, Event.GCD_END)
            self._add_rage(rage)
        elif not self.state['bloodthirst_available'] and self.state['whirlwind_available'] and self.state['rage'] >= 25:
            damage, rage = self.calcs.whirlwind()
            self.state['whirlwind_available'] = False
            self._apply_damage('whirlwind', damage)
            self.state['rage'] -= 25
            self._add_event(10, Event.WHIRLWIND_CD_END)
            self.state['on_gcd'] = True
            self._add_event(1.5, Event.GCD_END)
            self._add_rage(rage)


class Calcs:
    normalized_weapon_speed_lookup = {
        'Dagger': 1.7,
        'Axe': 2.4,
        'Fist Weapon': 2.4,
        'Mace': 2.4,
        'Sword': 2.4,
    }

    def __init__(self, boss, player):
        self.boss = boss
        self.player = player

        self.stats = {
            'attack_table': {
                'white': defaultdict(int),
                'yellow': defaultdict(int),
            }
        }

    def current_speed(self, offhand):
        return self.player.stats[('speed_off_hand' if offhand else 'speed_main_hand')] * (1 - self.player.stats['haste']/100)

    def current_boss_armor(self):
        return (
            self.boss.stats['armor']
            - (1 if BossDebuffs.SUNDER_ARMOR_X5 in self.boss.debuffs else 0)*450*5
            - (1 if BossDebuffs.FAERIE_FIRE in self.boss.debuffs else 0)*505
            - (1 if BossDebuffs.CURSE_OF_RECKLESSNESS in self.boss.debuffs else 0)*640
        )

    def white_hit(self, offhand):
        weapon_damage = self._calc_weapon_damage(
            self.player.stats[('damage_range_off_hand' if offhand else 'damage_range_main_hand')],
            self.player.stats[('speed_off_hand' if offhand else 'speed_main_hand')]
        )

        damage = self._apply_boss_armor(weapon_damage)
        if offhand:
            damage = round(damage * 0.625)
        attack_result = self._attack_table_roll(False)
        damage = self._apply_attack_table_roll(damage, attack_result)

        # https://forum.elysium-project.org/topic/22647-rage-explained-by-blizzard/
        # TODO not sure if I understood this correctly
        rage = round(damage / 230.6 * 7.5)
        if damage > 0:
            rage += self._unbridled_wrath()

        return damage, rage

    def bloodthirst(self):
        damage = self._apply_boss_armor(0.45 * self.player.stats['ap'])
        attack_result = self._attack_table_roll(True)
        damage = self._apply_attack_table_roll(damage, attack_result)

        return damage, (self._unbridled_wrath() if damage > 0 else 0)

    def whirlwind(self):
        normalized_weapon_damage = self._calc_weapon_damage(
            self.player.stats['damage_range_main_hand'],
            self.normalized_weapon_speed_lookup[self.player.stats['weapon_type_main_hand']]
        )
        damage = self._apply_boss_armor(normalized_weapon_damage)
        attack_result = self._attack_table_roll(True)
        damage = self._apply_attack_table_roll(damage, attack_result)

        return damage, (self._unbridled_wrath() if damage > 0 else 0)

    def _apply_boss_armor(self, damage):
        boss_armor = self.current_boss_armor()

        # See http://wowwiki.wikia.com/wiki/Armor
        # TODO not 100% sure if that's correct for player vs. boss @ vanilla
        damage_reduction = boss_armor / (boss_armor + 5882.5)

        return round(damage * (1 - damage_reduction))

    def _calc_weapon_damage(self, base_damage_range, speed):
        base_weapon_min, base_weapon_max = base_damage_range
        base_weapon_damage = random.randint(base_weapon_min, base_weapon_max)

        weapon_damage = base_weapon_damage + round(self.player.stats['ap'] / 14 * speed)

        return weapon_damage

    def _attack_table_roll(self, yellow):
        # TODO research the exact influence of weapon skill, implement
        miss_chance = (0.09 if yellow else 0.28) - self.player.stats['hit']/100
        dodge_chance = 0.065
        glancing_chance = (0.0 if yellow else 0.4)
        crit_chance = self.player.stats['crit']/100

        roll = random.random()
        if roll < miss_chance:
            attack_result = AttackTable.MISS
        elif roll < miss_chance + dodge_chance:
            attack_result = AttackTable.DODGE
        elif roll < miss_chance + dodge_chance + glancing_chance:
            attack_result = AttackTable.GLANCING
        elif roll < miss_chance + dodge_chance + glancing_chance + crit_chance:
            attack_result = AttackTable.CRIT
        else:
            attack_result = AttackTable.HIT
        self.stats['attack_table']['yellow' if yellow else 'white'][attack_result] += 1

        return attack_result

    def _apply_attack_table_roll(self, damage, attack_result):
        if attack_result == AttackTable.MISS or attack_result == AttackTable.DODGE:
            return 0
        elif attack_result == AttackTable.GLANCING:
            # TODO weapon skill
            return round(damage * 0.7)
        elif attack_result == AttackTable.CRIT:
            return round(damage * 2.2)
        elif attack_result == AttackTable.HIT:
            return damage
        else:
            raise ValueError(attack_result)

    def _unbridled_wrath(self):
        return 1 if random.random() < 0.4 else 0


class Event(Enum):
    WHITE_HIT_MAIN = auto()
    WHITE_HIT_OFF = auto()

    BLOODTHIRST_CD_END = auto()
    WHIRLWIND_CD_END = auto()

    BLOODRAGE_CD_END = auto()
    DEATH_WISH_END = auto()
    DEATH_WISH_CD_END = auto()
    RECKLESSNESS_END = auto()
    RECKLESSNESS_CD_END = auto()

    GCD_END = auto()
    RAGE_GAINED = auto()

    BLOODRAGE_ADD_RAGE_OVER_TIME = auto()


class LogLevel(Enum):
    INFO = 1
    DEBUG = 2


class BossDebuffs(Enum):
    SUNDER_ARMOR_X5 = auto()
    FAERIE_FIRE = auto()
    CURSE_OF_RECKLESSNESS = auto()


class PlayerBuffs(Enum):
    DEATH_WISH = auto()
    RECKLESSNESS = auto()


class AttackTable(Enum):
    MISS = auto()
    DODGE = auto()
    GLANCING = auto()
    CRIT = auto()
    HIT = auto()


def do_sim(player_stats):
    boss = Boss(
        {
            'armor': 4691,
        },
        {BossDebuffs.SUNDER_ARMOR_X5, BossDebuffs.FAERIE_FIRE, BossDebuffs.CURSE_OF_RECKLESSNESS},
    )
    config = {
        'n_runs': 1,
        'boss_fight_time_seconds': 180.0,
    }

    result_list_baseline = do_n_runs(boss, player_stats, config)
    avg_dps_baseline = mean([t[1] for t in result_list_baseline])
    stat_weights = dict()
    for stat, increase in []:
        player_stats_copy = copy.copy(player_stats)
        player_stats_copy[stat] += increase
        result_list = do_n_runs(boss, player_stats_copy, config)
        avg_dps = mean([t[1] for t in result_list])
        stat_weights[stat] = (avg_dps - avg_dps_baseline) / increase

    return avg_dps_baseline, stat_weights


def do_n_runs(boss, player_stats, config):
    result_list = []
    for _ in range(config['n_runs']):
        player = Player(player_stats)
        sim = Sim(boss, player)
        while sim.current_time_seconds < config['boss_fight_time_seconds']:
            event = sim.get_next_event()
            sim.handle_event(event)
        damage_done = sim.damage_done
        dps = sum(sim.damage_done.values()) / sim.current_time_seconds
        result_list.append((damage_done, dps))
        print(damage_done)
        print(dps)
        print(sim.calcs.stats)

    return result_list
