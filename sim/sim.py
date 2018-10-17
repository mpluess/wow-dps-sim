import copy
import heapq
import os
import random
import time

from .calcs import Calcs
from .constants import Constants
from .entities import AbilityLogEntry, Event, Player, Result, WhiteHitEvent
from .enums import AttackResult, AttackType, EventType, Hand, PlayerBuffs


class Sim:
    def __init__(self, boss, player, fight_duration, logging=False, run_nr=None):
        self.boss = boss
        self.player = player
        self.calcs = Calcs(boss, player)
        self.fight_duration = fight_duration
        self.execute_phase_start_time = fight_duration * 0.8
        self.logging = logging
        self.run_nr = run_nr
        self.log_handle = None

        self.event_queue = []
        self.event_count = 0
        self.current_time_seconds = 0.0
        self.damage_done = 0
        self.ability_log = []

        self.state = {
            'rage': 0,
            'on_gcd': False,
            'bloodthirst_available': True,
            'whirlwind_available': True,
            'death_wish_available': True,
            'flurry_charges': 0,
            'heroic_strike_toggled': False,
            'execute_phase': False,
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
        if not self.state['execute_phase'] and self.current_time_seconds >= self.execute_phase_start_time:
            self.state['execute_phase'] = True

        return event

    def handle_event(self, event):
        def do_rota():
            if self.state['execute_phase']:
                use_execute()
            else:
                if use_bloodthirst():
                    pass
                elif use_whirlwind():
                    pass

        def use_bloodthirst():
            if not self.state['on_gcd'] and self.state['bloodthirst_available'] and self.state['rage'] >= 30:
                ability = 'bloodthirst'
                self.state['bloodthirst_available'] = False
                self._apply_melee_attack_effects(ability, self.calcs.bloodthirst(), True, AttackType.YELLOW, rage_cost=30)
                self._add_event(6.0, EventType.BLOODTHIRST_CD_END)

                return True
            else:
                return False

        def use_death_wish():
            if self.state['rage'] >= 10:
                self.state['death_wish_available'] = False
                self._consume_rage('death_wish', 10, None)
                self.player.buffs.add(PlayerBuffs.DEATH_WISH)
                self._add_event(30.0, EventType.DEATH_WISH_END)
                self._add_event(180.0, EventType.DEATH_WISH_CD_END)
                self.log(f"{self._log_entry_beginning('death_wish')} activated\n")

                return True
            else:
                return False

        def use_execute():
            if not self.state['on_gcd'] and self.state['rage'] >= 10:
                ability = 'execute'
                self._apply_melee_attack_effects(ability, self.calcs.execute(self.state['rage']), True, AttackType.YELLOW, rage_cost=self.state['rage'])

                return True
            else:
                return False

        def use_heroic_strike():
            # BT 30 + WW 25 + HS 13
            if not self.state['execute_phase'] and self.state['rage'] >= 68:
                self.state['heroic_strike_toggled'] = True

        def use_whirlwind():
            # When between 25 and 29 rage and both BT + WW are available, both my intuition and this sim tell us
            # it's slightly better to delay WW and wait until 30 rage are available to use BT instead.
            if not self.state['on_gcd'] and not self.state['bloodthirst_available'] and self.state['whirlwind_available'] and self.state['rage'] >= 25:
                ability = 'whirlwind'
                self.state['whirlwind_available'] = False
                self._apply_melee_attack_effects(ability, self.calcs.whirlwind(), True, AttackType.YELLOW, rage_cost=25)
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
            do_rota()
        elif event_type == EventType.WHIRLWIND_CD_END:
            self.state['whirlwind_available'] = True
            do_rota()
        elif event_type == EventType.GCD_END:
            self.state['on_gcd'] = False
            do_rota()
        elif event_type == EventType.WHITE_HIT_MAIN:
            self.next_white_hit_main = self._add_event(self.calcs.current_speed(Hand.MAIN), EventType.WHITE_HIT_MAIN)
            if self.state['heroic_strike_toggled'] and self.state['rage'] >= 13:
                self._apply_melee_attack_effects('heroic_strike', self.calcs.heroic_strike(), False, AttackType.HEROIC_STRIKE, rage_cost=13)
                self._add_event(0.0, EventType.HEROIC_STRIKE_LANDED)
            else:
                self._apply_melee_attack_effects('white_main', self.calcs.white_hit(Hand.MAIN), False, AttackType.WHITE, hand_current_white_hit=Hand.MAIN)
            self.state['heroic_strike_toggled'] = False
        elif event_type == EventType.WHITE_HIT_OFF:
            self.next_white_hit_off = self._add_event(self.calcs.current_speed(Hand.OFF), EventType.WHITE_HIT_OFF)
            self._apply_melee_attack_effects('white_off', self.calcs.white_hit(Hand.OFF), False, AttackType.WHITE, hand_current_white_hit=Hand.OFF)
        elif event_type == EventType.RAGE_GAINED:
            if self.state['death_wish_available']:
                use_death_wish()
            do_rota()
            use_heroic_strike()
        elif event_type == EventType.HEROIC_STRIKE_LANDED:
            use_heroic_strike()

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

    def _apply_melee_attack_effects(self, ability, attack_result_damage_rage_tuple, triggers_gcd, attack_type,
                                    hand_current_white_hit=None, rage_cost=None):
        assert (attack_type == AttackType.YELLOW or attack_type == AttackType.HEROIC_STRIKE) or (attack_type == AttackType.WHITE and isinstance(hand_current_white_hit, Hand))

        def apply_damage(ability, damage, attack_result):
            assert damage >= 0

            if damage > 0:
                self.damage_done += damage

            if attack_result == AttackResult.MISS:
                self.log(f'{self._log_entry_beginning(ability)} missed\n')
            elif attack_result == AttackResult.DODGE:
                self.log(f'{self._log_entry_beginning(ability)} dodged\n')
            elif attack_result == AttackResult.GLANCING:
                self.log(f'{self._log_entry_beginning(ability)} glances for {damage}\n')
            elif attack_result == AttackResult.CRIT:
                self.log(f'{self._log_entry_beginning(ability)} crits for {damage}\n')
            elif attack_result == AttackResult.HIT:
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
            if attack_result == AttackResult.CRIT:
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

        attack_result, damage, rage_gained = attack_result_damage_rage_tuple
        if rage_cost is not None:
            self._consume_rage(ability, rage_cost, attack_result)
        apply_damage(ability, damage, attack_result)
        self._add_rage(ability, rage_gained)

        if attack_type == AttackType.WHITE:
            apply_flurry(hand_current_white_hit)
        elif attack_type == AttackType.HEROIC_STRIKE:
            apply_flurry(Hand.MAIN)

        if triggers_gcd:
            self.state['on_gcd'] = True
            self._add_event(1.5, EventType.GCD_END)

        self.ability_log.append(AbilityLogEntry(ability, attack_result, damage))

    def _consume_rage(self, ability, rage, attack_result):
        assert rage > 0
        assert self.state['rage'] >= rage
        # Dodged and parried abilities don't cost rage: https://forum.nostalrius.org/viewtopic.php?f=36&t=2670&start=20
        if attack_result is None or attack_result != AttackResult.DODGE:
            self.state['rage'] -= rage
            self.log(f'{self._log_entry_beginning(ability)} consumes {rage} rage\n')
            self.log(f"{self._log_entry_beginning()} Rage={self.state['rage']}\n")

    def _log_entry_beginning(self, ability=None):
        log_entry = f'[{self.current_time_seconds:.2f}]'
        if ability is not None:
            log_entry += f' {Constants.ability_names_lookup[ability]}'

        return log_entry


def do_sim(faction, race, class_, spec, items, partial_buffed_permanent_stats, boss, config):
    def do_n_runs(faction, race, class_, spec, items, partial_buffed_permanent_stats, boss, config):
        def sample_fight_duration(mu, sigma):
            """Normal distribution truncated at +/- 3*sigma"""
            f = random.gauss(mu, sigma)
            max_ = mu + 3 * sigma
            min_ = mu - 3 * sigma
            if f > max_:
                f = max_
            elif f < min_:
                f = min_

            return f

        result_list = []
        for run_nr in range(config.n_runs):
            player = Player(faction, race, class_, spec, items, partial_buffed_permanent_stats)
            fight_duration = sample_fight_duration(config.fight_duration_seconds_mu, config.fight_duration_seconds_sigma)
            with Sim(boss, player, fight_duration, logging=config.logging, run_nr=run_nr) as sim:
                while sim.current_time_seconds < fight_duration:
                    event = sim.get_next_event()
                    sim.handle_event(event)
                dps = sim.damage_done / sim.current_time_seconds
                result = Result.from_ability_log(dps, sim.ability_log)
                result_list.append(result)
                sim.log('\n')
                sim.log(str(result))

        return Result.get_merged_result(result_list)

    result_baseline = do_n_runs(faction, race, class_, spec, items, partial_buffed_permanent_stats, boss, config)
    stat_weights = dict()
    for stat, increase in config.stat_increase_tuples:
        stats_copy = copy.copy(partial_buffed_permanent_stats)
        stats_copy[stat] += increase
        result = do_n_runs(faction, race, class_, spec, items, stats_copy, boss, config)
        stat_weights[stat] = (result.dps - result_baseline.dps) / increase

    return result_baseline, stat_weights
