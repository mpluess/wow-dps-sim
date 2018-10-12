from collections import defaultdict
import copy
import heapq
import os
import random
from statistics import mean
import time

from .enums import AttackTable, AttackType, BossDebuffs, EventType, Hand, PlayerBuffs
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


class Sim:
    ability_names_lookup = {
        'bloodrage': 'Bloodrage',
        'bloodthirst': 'Bloodthirst',
        'death_wish': 'Death Wish',
        'recklessness': 'Recklessness',
        'whirlwind': 'Whirlwind',
        'white_main': 'White Hit Main',
        'white_off': 'White Hit Off',
    }

    def __init__(self, boss, player, logging=False, run_nr=None):
        self.boss = boss
        self.player = player
        self.calcs = Calcs(boss, player)
        self.logging = logging
        self.run_nr = run_nr
        self.log_handle = None

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
            'flurry_charges': 0,
        }

        self._add_event(0.0, EventType.BLOODRAGE_CD_END)
        self._add_event(0.0, EventType.DEATH_WISH_CD_END)
        self._add_event(0.0, EventType.RECKLESSNESS_CD_END)
        self.next_white_hit_main = self._add_event(0.0, EventType.WHITE_HIT_MAIN)
        self.next_white_hit_off = self._add_event(0.0, EventType.WHITE_HIT_OFF)

    def __enter__(self):
        if self.logging:
            ts = time.strftime('%Y%m%d-%H%M%S', time.localtime())
            id_ = random.randrange(1000000000) if self.run_nr is None else self.run_nr
            self.log_handle = open(os.path.join('logs', f'{ts}-{id_}.txt'), 'w')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.log_handle is not None:
            self.log_handle.close()

    def get_next_event(self):
        event = heapq.heappop(self.event_queue)
        self.current_time_seconds = event.time

        return event

    def handle_event(self, event):
        def do_rota(event):
            if use_bloodthirst(event):
                pass
            elif use_whirlwind(event):
                pass

        def use_bloodthirst(event):
            if not self.state['on_gcd'] and self.state['bloodthirst_available'] and self.state['rage'] >= 30:
                ability = 'bloodthirst'
                self.state['bloodthirst_available'] = False
                self._consume_rage(ability, 30)
                self._apply_melee_attack_effects(ability, self.calcs.bloodthirst(), True, AttackType.YELLOW)
                self._add_event(6.0, EventType.BLOODTHIRST_CD_END)

                return True
            else:
                return False

        def use_death_wish():
            if self.state['rage'] >= 10:
                self.state['death_wish_available'] = False
                self._consume_rage('death_wish', 10)
                self.player.buffs.add(PlayerBuffs.DEATH_WISH)
                self._add_event(30.0, EventType.DEATH_WISH_END)
                self._add_event(180.0, EventType.DEATH_WISH_CD_END)
                self.log(f"{self._log_entry_beginning('death_wish')} activated\n")

                return True
            else:
                return False

        def use_whirlwind(event):
            # When between 25 and 29 rage and both BT + WW are available, both my intuition and this sim tell us
            # it's slightly better to delay WW and wait until 30 rage are available to use BT instead.
            if not self.state['on_gcd'] and not self.state['bloodthirst_available'] and self.state['whirlwind_available'] and self.state['rage'] >= 25:
                ability = 'whirlwind'
                self.state['whirlwind_available'] = False
                self._consume_rage(ability, 25)
                self._apply_melee_attack_effects(ability, self.calcs.whirlwind(), True, AttackType.YELLOW)
                self._add_event(10.0, EventType.WHIRLWIND_CD_END)

                return True
            else:
                return False

        # self.log(f"{self._log_entry_beginning()} flurry_charges={self.state['flurry_charges']}\n")
        event_type = event.event_type
        if event_type == EventType.BLOODRAGE_CD_END:
            self._add_rage('bloodrage', 10)
            for i in range(10):
                self._add_event(i + 1, EventType.BLOODRAGE_ADD_RAGE_OVER_TIME)
            self._add_event(60.0, EventType.BLOODRAGE_CD_END)
        elif event_type == EventType.BLOODRAGE_ADD_RAGE_OVER_TIME:
            self._add_rage('bloodrage', 1)
        elif event_type == EventType.DEATH_WISH_END:
            self.player.buffs.remove(PlayerBuffs.DEATH_WISH)
            self.log(f"{self._log_entry_beginning('death_wish')} fades\n")
        elif event_type == EventType.DEATH_WISH_CD_END:
            self.state['death_wish_available'] = True
            use_death_wish()
        elif event_type == EventType.RECKLESSNESS_END:
            self.player.buffs.remove(PlayerBuffs.RECKLESSNESS)
            self.log(f"{self._log_entry_beginning('recklessness')} fades\n")
        elif event_type == EventType.RECKLESSNESS_CD_END:
            self.player.buffs.add(PlayerBuffs.RECKLESSNESS)
            self._add_event(15.0, EventType.RECKLESSNESS_END)
            self._add_event(1800.0, EventType.RECKLESSNESS_CD_END)
            self.log(f"{self._log_entry_beginning('recklessness')} activated\n")
        elif event_type == EventType.BLOODTHIRST_CD_END:
            self.state['bloodthirst_available'] = True
            use_bloodthirst(event)
        elif event_type == EventType.WHIRLWIND_CD_END:
            self.state['whirlwind_available'] = True
            use_whirlwind(event)
        elif event_type == EventType.GCD_END:
            self.state['on_gcd'] = False
            do_rota(event)
        elif event_type == EventType.WHITE_HIT_MAIN:
            self.next_white_hit_main = self._add_event(self.calcs.current_speed(Hand.MAIN), EventType.WHITE_HIT_MAIN)
            self._apply_melee_attack_effects('white_main', self.calcs.white_hit(Hand.MAIN), False, AttackType.WHITE, Hand.MAIN)
        elif event_type == EventType.WHITE_HIT_OFF:
            self.next_white_hit_off = self._add_event(self.calcs.current_speed(Hand.OFF), EventType.WHITE_HIT_OFF)
            self._apply_melee_attack_effects('white_off', self.calcs.white_hit(Hand.OFF), False, AttackType.WHITE, Hand.OFF)
        elif event_type == EventType.RAGE_GAINED:
            if self.state['death_wish_available']:
                use_death_wish()
            do_rota(event)

    def log(self, message):
        if self.logging:
            self.log_handle.write(message)

    def _add_event(self, time_delta, event_type):
        assert time_delta >= 0.0

        if event_type == EventType.WHITE_HIT_MAIN or event_type == EventType.WHITE_HIT_OFF:
            event = WhiteHitEvent(self.current_time_seconds + time_delta, self.event_count, event_type)
        else:
            event = Event(self.current_time_seconds + time_delta, self.event_count, event_type)
        heapq.heappush(self.event_queue, event)
        self.event_count += 1

        return event

    def _add_rage(self, ability, rage):
        assert rage >= 0
        if rage > 0:
            self.state['rage'] = min(100, self.state['rage'] + rage)
            self._add_event(0.0, EventType.RAGE_GAINED)
            self.log(f'{self._log_entry_beginning(ability)} generates {rage} rage\n')
            self.log(f"{self._log_entry_beginning()} Rage={self.state['rage']}\n")

    def _apply_melee_attack_effects(self, ability, attack_result_damage_rage_tuple, triggers_gcd, attack_type, hand_current_white_hit=None):
        assert attack_type == AttackType.YELLOW or (attack_type == AttackType.WHITE and isinstance(hand_current_white_hit, Hand))

        def apply_damage(ability, damage, attack_result):
            assert damage >= 0

            if damage > 0:
                self.damage_done[ability] += damage

            if attack_result == AttackTable.MISS:
                self.log(f'{self._log_entry_beginning(ability)} missed\n')
            elif attack_result == AttackTable.DODGE:
                self.log(f'{self._log_entry_beginning(ability)} dodged\n')
            elif attack_result == AttackTable.GLANCING:
                self.log(f'{self._log_entry_beginning(ability)} glances for {damage}\n')
            elif attack_result == AttackTable.CRIT:
                self.log(f'{self._log_entry_beginning(ability)} crits for {damage}\n')
            elif attack_result == AttackTable.HIT:
                self.log(f'{self._log_entry_beginning(ability)} hits for {damage}\n')
            else:
                raise NotImplementedError()

        # TODO edge case: don't apply flurry to white hit hitting in less than epsilon seconds
        # (should I really implement this? how often is this the case? how is it implemented in the game?)
        def apply_flurry(hand_current_white_hit):
            def apply_flurry_to_event(event):
                if not event.has_flurry:
                    event_str_before = str(event)
                    event.time = self.current_time_seconds + (event.time - self.current_time_seconds)*0.7
                    event.has_flurry = True
                    self.log(f'{self._log_entry_beginning()} Applying flurry, before={{{event_str_before}}}, after={{{event}}}\n')

                    return True
                else:
                    return False

            resort_events = False
            # New flurry proc, apply to both the current white hit proccing it and the existing white hit (other hand)
            if attack_result == AttackTable.CRIT:
                self.log(f'{self._log_entry_beginning()} Flurry proc\n')
                self.state['flurry_charges'] = 3
                flurry_applied_main = apply_flurry_to_event(self.next_white_hit_main)
                flurry_applied_off = apply_flurry_to_event(self.next_white_hit_off)
                resort_events = flurry_applied_main or flurry_applied_off
                self.state['flurry_charges'] = 1
            # Existing flurry charge, only apply to the current white hit proccing it since the existing white hit (other hand)
            # will already have flurry at this point.
            elif self.state['flurry_charges'] > 0:
                resort_events = apply_flurry_to_event(self.next_white_hit_off if hand_current_white_hit == Hand.OFF else self.next_white_hit_main)
                self.state['flurry_charges'] -= 1

            if resort_events:
                self.event_queue.sort()

        attack_result, damage, rage = attack_result_damage_rage_tuple
        apply_damage(ability, damage, attack_result)
        self._add_rage(ability, rage)

        # TODO HS
        if attack_type == AttackType.WHITE:
            apply_flurry(hand_current_white_hit)

        if triggers_gcd:
            self.state['on_gcd'] = True
            self._add_event(1.5, EventType.GCD_END)

    def _consume_rage(self, ability, rage):
        assert rage > 0
        assert self.state['rage'] >= rage
        self.state['rage'] -= rage
        self.log(f'{self._log_entry_beginning(ability)} consumes {rage} rage\n')
        self.log(f"{self._log_entry_beginning()} Rage={self.state['rage']}\n")

    def _log_entry_beginning(self, ability=None):
        log_entry = f'[{self.current_time_seconds:.2f}]'
        if ability is not None:
            log_entry += f' {self.ability_names_lookup[ability]}'

        return log_entry


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
        def apply_temporary_buffs(stats):
            def apply_temporary_buff_flat_stats(stats):
                stats = copy.copy(stats)

                if PlayerBuffs.RECKLESSNESS in self.player.buffs:
                    stats['crit'] += 100

                return stats

            def apply_temporary_buff_percentage_effects(stats):
                stats = copy.copy(stats)

                if PlayerBuffs.DEATH_WISH in self.player.buffs:
                    stats['damage_multiplier'] *= 1.2

                return stats

            stats = apply_temporary_buff_flat_stats(stats)
            stats = apply_temporary_buff_percentage_effects(stats)

            return stats

        stats = self.player.partial_buffed_permanent_stats
        stats = apply_temporary_buffs(stats)
        stats = finalize_buffed_stats(self.player.faction, self.player.race, self.player.class_, self.player.spec, stats)

        return stats

    def bloodthirst(self):
        current_stats = self.current_stats()
        base_damage = round(0.45 * current_stats['ap'])

        return self._calc_attack_result_damage_rage(base_damage, AttackType.YELLOW, Hand.MAIN)

    def whirlwind(self):
        current_stats = self.current_stats()
        base_damage = self._calc_weapon_damage(
            current_stats['damage_range_main_hand'],
            self.normalized_weapon_speed_lookup[current_stats['weapon_type_main_hand']]
        )

        return self._calc_attack_result_damage_rage(base_damage, AttackType.YELLOW, Hand.MAIN)

    def white_hit(self, hand):
        assert isinstance(hand, Hand)
        current_stats = self.current_stats()
        base_damage = self._calc_weapon_damage(
            current_stats[('damage_range_off_hand' if hand == Hand.OFF else 'damage_range_main_hand')],
            current_stats[('speed_off_hand' if hand == Hand.OFF else 'speed_main_hand')]
        )

        return self._calc_attack_result_damage_rage(base_damage, AttackType.WHITE, hand)

    def _calc_attack_result_damage_rage(self, base_damage, attack_type, hand):
        def apply_attack_table_roll(damage, attack_result, hand):
            if attack_result == AttackTable.MISS or attack_result == AttackTable.DODGE:
                return 0
            elif attack_result == AttackTable.GLANCING:
                current_stats = self.current_stats()
                weapon_skill_bonus = current_stats[('weapon_skill_bonus_off_hand' if hand == Hand.OFF else 'weapon_skill_bonus_main_hand')]
                glancing_factor = (0.7 + min(10, weapon_skill_bonus) * 0.03)
                return round(damage * glancing_factor)
            elif attack_result == AttackTable.CRIT:
                return round(damage * 2.2)
            elif attack_result == AttackTable.HIT:
                return damage
            else:
                raise ValueError(attack_result)

        def apply_boss_armor(damage):
            def current_boss_armor():
                # TODO further armor pen if available
                return max(
                    0,

                    self.boss.stats['armor']
                    - (1 if BossDebuffs.SUNDER_ARMOR_X5 in self.boss.debuffs else 0) * 450 * 5
                    - (1 if BossDebuffs.FAERIE_FIRE in self.boss.debuffs else 0) * 505
                    - (1 if BossDebuffs.CURSE_OF_RECKLESSNESS in self.boss.debuffs else 0) * 640
                )

            boss_armor = current_boss_armor()

            # See http://wowwiki.wikia.com/wiki/Armor
            # TODO not 100% sure if that's correct for player vs. boss @ vanilla
            damage_reduction = boss_armor / (boss_armor + 5882.5)

            return round(damage * (1 - damage_reduction))

        def attack_table_roll(attack_type, hand):
            """
            https://web.archive.org/web/20061115223930/http://forums.wow-europe.com/thread.html?topicId=14381707&sid=1

            miss:
            300: 8.6
            ...
            315: 8.0

            dodge:
            300: 5.6%
            ...
            315: 5.0

            crit:
            300: 4.4
            ...
            315: 5

            glancing:
            300: *0.7
            301: *0.73
            ...
            310: *1.0
            """

            assert isinstance(attack_type, AttackType)
            assert isinstance(hand, Hand)
            current_stats = self.current_stats()
            weapon_skill_bonus = current_stats[
                ('weapon_skill_bonus_off_hand' if hand == Hand.OFF else 'weapon_skill_bonus_main_hand')]

            miss_chance = max(
                0.0,
                (self.boss.stats['base_miss'] if attack_type == AttackType.YELLOW else self.boss.stats[
                                                                                           'base_miss'] + 0.19)
                - current_stats['hit'] / 100
                - weapon_skill_bonus * 0.0004
            )
            dodge_chance = max(0.0, self.boss.stats['base_dodge'] - weapon_skill_bonus * 0.0004)
            glancing_chance = (0.0 if attack_type == AttackType.YELLOW else 0.4)
            crit_chance = max(0.0, current_stats['crit'] / 100 - (15 - weapon_skill_bonus) * 0.0004)

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
            self.statistics['attack_table']['yellow' if attack_type == AttackType.YELLOW else 'white'][
                attack_result] += 1

            return attack_result

        def unbridled_wrath():
            return 1 if random.random() < 0.4 else 0

        assert isinstance(hand, Hand)
        assert base_damage >= 0
        damage = base_damage

        attack_result = attack_table_roll(attack_type, hand)
        damage = apply_attack_table_roll(damage, attack_result, hand)
        rage = 0
        if damage > 0:
            damage = apply_boss_armor(damage)

            if hand == Hand.OFF:
                damage = round(damage * 0.75)

            current_stats = self.current_stats()
            damage = round(damage * current_stats['damage_multiplier'])

            # https://forum.elysium-project.org/topic/22647-rage-explained-by-blizzard/
            # TODO not sure if I understood this correctly
            if attack_type == AttackType.WHITE:
                rage += round(damage / 230.6 * 7.5)

                # TODO HS
                rage += unbridled_wrath()

        return attack_result, damage, rage

    def _calc_weapon_damage(self, base_damage_range, speed):
        base_weapon_min, base_weapon_max = base_damage_range
        base_weapon_damage = random.randint(base_weapon_min, base_weapon_max)

        current_stats = self.current_stats()
        weapon_damage = base_weapon_damage + round(current_stats['ap'] / 14 * speed)

        return weapon_damage


def do_sim(faction, race, class_, spec, items, partial_buffed_permanent_stats):
    def do_n_runs(boss, config, faction, race, class_, spec, items, partial_buffed_permanent_stats):
        result_list = []
        for run_nr in range(config['n_runs']):
            player = Player(faction, race, class_, spec, items, partial_buffed_permanent_stats)
            with Sim(boss, player, config['logging'], run_nr) as sim:
                while sim.current_time_seconds < config['boss_fight_time_seconds']:
                    event = sim.get_next_event()
                    sim.handle_event(event)
                damage_done = sim.damage_done
                dps = sum(damage_done.values()) / sim.current_time_seconds
                result_list.append((damage_done, dps))

                sim.log(f'DPS: {dps}\n')
                sim.log(f'{damage_done}\n')
                sim.log(f'{sim.calcs.statistics}\n')

        return result_list

    boss = Boss(
        {
            'armor': 4691,
            'base_miss': 0.086,
            'base_dodge': 0.056,
        },
        {BossDebuffs.SUNDER_ARMOR_X5, BossDebuffs.FAERIE_FIRE, BossDebuffs.CURSE_OF_RECKLESSNESS},
    )
    config = {
        'n_runs': 1,
        'logging': True,
        'boss_fight_time_seconds': 180.0,
    }

    result_list_baseline = do_n_runs(boss, config, faction, race, class_, spec, items, partial_buffed_permanent_stats)
    avg_dps_baseline = mean([t[1] for t in result_list_baseline])
    stat_weights = dict()
    for stat, increase in []:  # [('hit', 1), ('crit', 1), ('agi', 20), ('ap', 30), ('str', 15), ('haste', 1), ('Sword', 1)]:
        stats_copy = copy.copy(partial_buffed_permanent_stats)
        stats_copy[stat] += increase
        result_list = do_n_runs(boss, config, faction, race, class_, spec, items, stats_copy)
        avg_dps = mean([t[1] for t in result_list])
        stat_weights[stat] = (avg_dps - avg_dps_baseline) / increase

    return avg_dps_baseline, stat_weights
