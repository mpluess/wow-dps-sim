from collections import defaultdict
import copy
import heapq
import random
from statistics import mean

from .enums import AttackTable, AttackType, BossDebuffs, Event, Hand, PlayerBuffs
from stats import finalize_buffed_stats


class Boss:
    def __init__(self, stats, debuffs):
        self.stats = stats
        self.debuffs = debuffs


class Player:
    def __init__(self, faction, race, class_, spec, items, partial_buffed_permanent_stats):
        self.faction = faction
        self.race = race
        self.class_ = class_
        self.spec = spec
        self.items = items
        self.partial_buffed_permanent_stats = partial_buffed_permanent_stats

        self.buffs = set()


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
        self.next_white_hit_main = self._add_event(self.calcs.current_speed(Hand.MAIN), Event.WHITE_HIT_MAIN)
        self.next_white_hit_off = self._add_event(self.calcs.current_speed(Hand.OFF), Event.WHITE_HIT_OFF)

    def get_next_event(self):
        time, _, event = heapq.heappop(self.event_queue)
        self.current_time_seconds = time

        return event

    def handle_event(self, event):
        if event == Event.BLOODRAGE_CD_END:
            self._add_rage('bloodrage', 10)
            for i in range(10):
                self._add_event(i + 1, Event.BLOODRAGE_ADD_RAGE_OVER_TIME)
            self._add_event(60, Event.BLOODRAGE_CD_END)
        elif event == Event.BLOODRAGE_ADD_RAGE_OVER_TIME:
            self._add_rage('bloodrage', 1)
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
            ability = 'white_main'
            damage, rage = self.calcs.white_hit(Hand.MAIN)
            self._apply_damage(ability, damage)
            self._add_rage(ability, rage)
            self.next_white_hit_main = self._add_event(self.calcs.current_speed(Hand.MAIN), Event.WHITE_HIT_MAIN)
        elif event == Event.WHITE_HIT_OFF:
            ability = 'white_off'
            damage, rage = self.calcs.white_hit(Hand.OFF)
            self._apply_damage(ability, damage)
            self._add_rage(ability, rage)
            self.next_white_hit_off = self._add_event(self.calcs.current_speed(Hand.OFF), Event.WHITE_HIT_OFF)
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

    def _add_rage(self, ability, rage):
        assert rage >= 0
        if rage > 0:
            self.state['rage'] = min(100, self.state['rage'] + rage)
            self._add_event(0, Event.RAGE_GAINED)

    def _apply_damage(self, ability, damage):
        assert damage >= 0
        if damage > 0:
            self.damage_done[ability] += damage

    def _apply_death_wish(self):
        if self.state['rage'] >= 10:
            self.state['death_wish_available'] = False
            self._consume_rage(10)
            self.player.buffs.add(PlayerBuffs.DEATH_WISH)
            self._add_event(30, Event.DEATH_WISH_END)
            self._add_event(180, Event.DEATH_WISH_CD_END)

    def _consume_rage(self, rage):
        assert rage > 0
        assert self.state['rage'] >= rage
        self.state['rage'] -= rage

    def _do_rota(self):
        if self.state['bloodthirst_available'] and self.state['rage'] >= 30:
            ability = 'bloodthirst'
            self.state['bloodthirst_available'] = False
            self._consume_rage(30)
            damage, rage = self.calcs.bloodthirst()
            self._apply_damage(ability, damage)
            self._add_rage(ability, rage)
            self._add_event(6, Event.BLOODTHIRST_CD_END)
            self.state['on_gcd'] = True
            self._add_event(1.5, Event.GCD_END)
        elif not self.state['bloodthirst_available'] and self.state['whirlwind_available'] and self.state['rage'] >= 25:
            ability = 'whirlwind'
            self.state['whirlwind_available'] = False
            self._consume_rage(25)
            damage, rage = self.calcs.whirlwind()
            self._apply_damage(ability, damage)
            self._add_rage(ability, rage)
            self._add_event(10, Event.WHIRLWIND_CD_END)
            self.state['on_gcd'] = True
            self._add_event(1.5, Event.GCD_END)


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

        self.statistics = {
            'attack_table': {
                'white': defaultdict(int),
                'yellow': defaultdict(int),
            }
        }

    def current_speed(self, hand):
        assert isinstance(hand, Hand)
        current_stats = self.current_stats()

        return current_stats[('speed_off_hand' if hand == Hand.OFF else 'speed_main_hand')] * (1 - current_stats['haste']/100)

    def current_stats(self):
        stats = self.player.partial_buffed_permanent_stats
        stats = self._apply_temporary_buffs(stats)
        stats = finalize_buffed_stats(self.player.faction, self.player.race, self.player.class_, self.player.spec, stats)

        return stats

    def bloodthirst(self):
        current_stats = self.current_stats()
        base_damage = round(0.45 * current_stats['ap'])

        return self._calc_damage_and_rage(base_damage, AttackType.YELLOW, Hand.MAIN)

    def whirlwind(self):
        current_stats = self.current_stats()
        base_damage = self._calc_weapon_damage(
            current_stats['damage_range_main_hand'],
            self.normalized_weapon_speed_lookup[current_stats['weapon_type_main_hand']]
        )

        return self._calc_damage_and_rage(base_damage, AttackType.YELLOW, Hand.MAIN)

    def white_hit(self, hand):
        assert isinstance(hand, Hand)
        current_stats = self.current_stats()
        base_damage = self._calc_weapon_damage(
            current_stats[('damage_range_off_hand' if hand == Hand.OFF else 'damage_range_main_hand')],
            current_stats[('speed_off_hand' if hand == Hand.OFF else 'speed_main_hand')]
        )

        return self._calc_damage_and_rage(base_damage, AttackType.WHITE, hand)

    def _calc_damage_and_rage(self, base_damage, attack_type, hand):
        assert isinstance(hand, Hand)
        assert base_damage >= 0
        damage = base_damage

        attack_result = self._attack_table_roll(attack_type)
        damage = self._apply_attack_table_roll(damage, attack_result)
        rage = 0
        if damage > 0:
            damage = self._apply_boss_armor(damage)

            if hand == Hand.OFF:
                damage = round(damage * 0.625)

            current_stats = self.current_stats()
            damage = round(damage * current_stats['damage_multiplier'])

            # https://forum.elysium-project.org/topic/22647-rage-explained-by-blizzard/
            # TODO not sure if I understood this correctly
            if attack_type == AttackType.WHITE:
                rage += round(damage / 230.6 * 7.5)
            rage += self._unbridled_wrath()

        return damage, rage

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

    def _apply_boss_armor(self, damage):
        boss_armor = self._current_boss_armor()

        # See http://wowwiki.wikia.com/wiki/Armor
        # TODO not 100% sure if that's correct for player vs. boss @ vanilla
        damage_reduction = boss_armor / (boss_armor + 5882.5)

        return round(damage * (1 - damage_reduction))

    def _apply_temporary_buffs(self, stats):
        stats = self._apply_temporary_buff_flat_stats(stats)
        stats = self._apply_temporary_buff_percentage_effects(stats)

        return stats

    def _apply_temporary_buff_flat_stats(self, stats):
        stats = copy.copy(stats)

        if PlayerBuffs.RECKLESSNESS in self.player.buffs:
            stats['crit'] += 100

        return stats

    def _apply_temporary_buff_percentage_effects(self, stats):
        stats = copy.copy(stats)

        if PlayerBuffs.DEATH_WISH in self.player.buffs:
            stats['damage_multiplier'] *= 1.2

        return stats

    # TODO research the exact influence of weapon skill, implement
    def _attack_table_roll(self, attack_type):
        assert isinstance(attack_type, AttackType)
        current_stats = self.current_stats()

        miss_chance = max(0.0, (0.09 if attack_type == AttackType.YELLOW else 0.28) - current_stats['hit']/100)
        dodge_chance = 0.065
        glancing_chance = (0.0 if attack_type == AttackType.YELLOW else 0.4)
        crit_chance = current_stats['crit'] / 100

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
        self.statistics['attack_table']['yellow' if attack_type == AttackType.YELLOW else 'white'][attack_result] += 1

        return attack_result

    def _calc_weapon_damage(self, base_damage_range, speed):
        base_weapon_min, base_weapon_max = base_damage_range
        base_weapon_damage = random.randint(base_weapon_min, base_weapon_max)

        current_stats = self.current_stats()
        weapon_damage = base_weapon_damage + round(current_stats['ap'] / 14 * speed)

        return weapon_damage

    def _current_boss_armor(self):
        # TODO armor pen
        return max(
            0,

            self.boss.stats['armor']
            - (1 if BossDebuffs.SUNDER_ARMOR_X5 in self.boss.debuffs else 0)*450*5
            - (1 if BossDebuffs.FAERIE_FIRE in self.boss.debuffs else 0)*505
            - (1 if BossDebuffs.CURSE_OF_RECKLESSNESS in self.boss.debuffs else 0)*640
        )

    def _unbridled_wrath(self):
        return 1 if random.random() < 0.4 else 0


def do_sim(faction, race, class_, spec, items, partial_buffed_permanent_stats):
    boss = Boss(
        {
            'armor': 4691,
        },
        {BossDebuffs.SUNDER_ARMOR_X5, BossDebuffs.FAERIE_FIRE, BossDebuffs.CURSE_OF_RECKLESSNESS},
    )
    config = {
        'n_runs': 1000,
        'boss_fight_time_seconds': 180.0,
    }

    result_list_baseline = do_n_runs(boss, config, faction, race, class_, spec, items, partial_buffed_permanent_stats)
    avg_dps_baseline = mean([t[1] for t in result_list_baseline])
    stat_weights = dict()
    # TODO currently only stats not affecting other stats are possible
    for stat, increase in []:  # [('hit', 1), ('crit', 1), ('ap', 30)]:
        stats_copy = copy.copy(partial_buffed_permanent_stats)
        stats_copy[stat] += increase
        result_list = do_n_runs(boss, config, faction, race, class_, spec, items, stats_copy)
        avg_dps = mean([t[1] for t in result_list])
        stat_weights[stat] = (avg_dps - avg_dps_baseline) / increase

    return avg_dps_baseline, stat_weights


def do_n_runs(boss, config, faction, race, class_, spec, items, partial_buffed_permanent_stats):
    result_list = []
    for _ in range(config['n_runs']):
        player = Player(faction, race, class_, spec, items, partial_buffed_permanent_stats)
        sim = Sim(boss, player)
        while sim.current_time_seconds < config['boss_fight_time_seconds']:
            event = sim.get_next_event()
            sim.handle_event(event)
        damage_done = sim.damage_done
        dps = sum(damage_done.values()) / sim.current_time_seconds
        result_list.append((damage_done, dps))

        # print(damage_done)
        # print(dps)
        # print(sim.calcs.statistics)

    return result_list
