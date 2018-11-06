import heapq
import os
import random
import time

from .calcs import Calcs
from .constants import Constants
from .entities import AbilityLogEntry, Event, Player, Result, WhiteHitEvent
from .enums import AttackResult, AttackType, EventType, Hand, PlayerBuffs, Stance
from vanilla_utils.enums import Proc
import vanilla_utils.knowledge as knowledge
import vanilla_utils.rotation_config as rotation_config


class Sim:
    epsilon = 1e-7

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
            'on_stance_cd': False,
            'bloodthirst_available': True,
            'next_bloodthirst_available_at': 0.0,
            'whirlwind_available': True,
            'next_whirlwind_available_at': 0.0,
            'overpower_not_on_cd': True,
            'overpower_available_till': 0.0,
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
        self.crusader_main_proc_end_event = None
        self.crusader_off_proc_end_event = None

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
                # OP vs. no OP:
                # 586 vs. 573 DPS @ pre-raid BIS
                # 886 vs. 862 DPS @ Naxx BIS
                elif use_overpower():
                    pass

        def switch_stance(stance):
            assert self.player.stance != stance

            if not self.state['on_stance_cd']:
                self.player.stance = stance
                self.state['on_stance_cd'] = True
                self._add_event(knowledge.STANCE_CD_DURATION, EventType.STANCE_CD_END)
                self.log(f'{self._log_entry_beginning()} Switching stance to {stance}\n')
                self.state['rage'] = min(knowledge.MAX_RAGE_AFTER_STANCE_SWITCH, self.state['rage'])
                self.log(f"{self._log_entry_beginning()} Rage={self.state['rage']}\n")

                return True
            else:
                return False

        def use_bloodthirst():
            if not self.state['on_gcd'] and self.state['bloodthirst_available'] and self.state['rage'] >= knowledge.BLOODTHIRST_RAGE_COST:
                ability = 'bloodthirst'
                self.state['bloodthirst_available'] = False
                self._apply_melee_attack_effects(ability, self.calcs.bloodthirst(), True, AttackType.YELLOW, Hand.MAIN, rage_cost=knowledge.BLOODTHIRST_RAGE_COST)
                added_event = self._add_event(knowledge.BLOODTHIRST_CD, EventType.BLOODTHIRST_CD_END)
                self.state['next_bloodthirst_available_at'] = added_event.time

                return True
            else:
                return False

        def use_death_wish():
            if self.state['rage'] >= knowledge.DEATH_WISH_RAGE_COST:
                self.state['death_wish_available'] = False
                self._consume_rage('death_wish', knowledge.DEATH_WISH_RAGE_COST, None)
                self.player.buffs.add(PlayerBuffs.DEATH_WISH)
                self._add_event(knowledge.DEATH_WISH_DURATION, EventType.DEATH_WISH_END)
                self._add_event(knowledge.DEATH_WISH_CD, EventType.DEATH_WISH_CD_END)
                self.log(f"{self._log_entry_beginning('death_wish')} activated\n")

                return True
            else:
                return False

        def use_execute():
            if not self.state['on_gcd'] and self.state['rage'] >= knowledge.EXECUTE_BASE_RAGE_COST:
                ability = 'execute'
                self._apply_melee_attack_effects(
                    ability, self.calcs.execute(self.state['rage']), True, AttackType.YELLOW, Hand.MAIN,
                    rage_cost=self.state['rage'], base_rage_cost=knowledge.EXECUTE_BASE_RAGE_COST
                )

                return True
            else:
                return False

        def use_heroic_strike():
            if not self.state['execute_phase'] and self.state['rage'] >= rotation_config.HEROIC_STRIKE_MIN_RAGE_THRESHOLD:
                self.state['heroic_strike_toggled'] = True

        def use_overpower():
            if (
                not self.state['on_gcd']
                and self.state['overpower_not_on_cd'] and (self.state['overpower_available_till'] - self.current_time_seconds) > self.epsilon
                and self.state['rage'] >= knowledge.OVERPOWER_RAGE_COST and self.state['rage'] <= rotation_config.OVERPOWER_MAX_RAGE_THRESHOLD
                and (self.state['next_bloodthirst_available_at'] - self.current_time_seconds) > rotation_config.OVERPOWER_MIN_BLOODTHIRST_CD_LEFT
                and (self.state['next_whirlwind_available_at'] - self.current_time_seconds) > rotation_config.OVERPOWER_MIN_WHIRLWIND_CD_LEFT
            ):
                assert self.player.stance == Stance.BERSERKER
                assert not self.state['bloodthirst_available']
                assert not self.state['whirlwind_available']

                if switch_stance(Stance.BATTLE):
                    ability = 'overpower'
                    self.state['overpower_not_on_cd'] = False
                    self.state['overpower_available_till'] = self.current_time_seconds
                    self._apply_melee_attack_effects(ability, self.calcs.overpower(), True, AttackType.YELLOW, Hand.MAIN, rage_cost=knowledge.OVERPOWER_RAGE_COST)
                    self._add_event(knowledge.OVERPOWER_CD, EventType.OVERPOWER_CD_END)

                    return True

            return False

        def use_whirlwind():
            # When between 25 and 29 rage and both BT + WW are available, both my intuition and this sim tell us
            # it's slightly better to delay WW and wait until 30 rage are available to use BT instead.
            if (
                not self.state['on_gcd'] and not self.state['bloodthirst_available']
                and self.state['whirlwind_available'] and self.player.stance == Stance.BERSERKER and self.state['rage'] >= knowledge.WHIRLWIND_RAGE_COST
            ):
                ability = 'whirlwind'
                self.state['whirlwind_available'] = False
                self._apply_melee_attack_effects(ability, self.calcs.whirlwind(), True, AttackType.YELLOW, Hand.MAIN, rage_cost=knowledge.WHIRLWIND_RAGE_COST)
                added_event = self._add_event(knowledge.WHIRLWIND_CD, EventType.WHIRLWIND_CD_END)
                self.state['next_whirlwind_available_at'] = added_event.time

                return True
            else:
                return False

        # self.log(f"{self._log_entry_beginning()} flurry_charges={self.state['flurry_charges']}\n")
        event_type = event.event_type
        if event_type == EventType.BLOODRAGE_CD_END:
            self._add_rage('bloodrage', knowledge.BLOODRAGE_BASE_RAGE)
            for i in range(knowledge.BLOODRAGE_DURATION):
                self._add_event(i + 1, EventType.BLOODRAGE_ADD_RAGE_OVER_TIME)
            self._add_event(knowledge.BLOODRAGE_CD, EventType.BLOODRAGE_CD_END)
        elif event_type == EventType.BLOODRAGE_ADD_RAGE_OVER_TIME:
            self._add_rage('bloodrage', knowledge.BLOODRAGE_TICK_RAGE)
        elif event_type == EventType.DEATH_WISH_END:
            self.player.buffs.remove(PlayerBuffs.DEATH_WISH)
            self.log(f"{self._log_entry_beginning('death_wish')} fades\n")
        elif event_type == EventType.DEATH_WISH_CD_END:
            self.state['death_wish_available'] = True
            use_death_wish()
        elif event_type == EventType.RECKLESSNESS_END:
            self.player.buffs.remove(PlayerBuffs.RECKLESSNESS)
            self.log(f"{self._log_entry_beginning('recklessness')} fades\n")
        # TODO Check if in berserker stance. Make sure it gets triggered as soon as possible if currently not in berserker stance.
        elif event_type == EventType.RECKLESSNESS_CD_END:
            self.player.buffs.add(PlayerBuffs.RECKLESSNESS)
            self._add_event(knowledge.RECKLESSNESS_DURATION, EventType.RECKLESSNESS_END)
            self._add_event(knowledge.RECKLESSNESS_CD, EventType.RECKLESSNESS_CD_END)
            self.log(f"{self._log_entry_beginning('recklessness')} activated\n")
        elif event_type == EventType.BLOODTHIRST_CD_END:
            self.state['bloodthirst_available'] = True
            do_rota()
        elif event_type == EventType.WHIRLWIND_CD_END:
            self.state['whirlwind_available'] = True
            do_rota()
        elif event_type == EventType.OVERPOWER_CD_END:
            self.state['overpower_not_on_cd'] = True
            do_rota()
        elif event_type == EventType.ATTACK_DODGED:
            do_rota()
        elif event_type == EventType.GCD_END:
            self.state['on_gcd'] = False
            do_rota()
        elif event_type == EventType.STANCE_CD_END:
            self.state['on_stance_cd'] = False
            # TODO (?) Edge case: @ Battle Stance after OP, BT available / available very very soon, rage >= 30: use BT before switching
            if self.player.stance != Stance.BERSERKER:
                switch_stance(Stance.BERSERKER)
            do_rota()
        elif event_type == EventType.WHITE_HIT_MAIN:
            self.next_white_hit_main = self._add_event(self.calcs.current_speed(Hand.MAIN), EventType.WHITE_HIT_MAIN)
            if self.state['heroic_strike_toggled'] and self.state['rage'] >= knowledge.HEROIC_STRIKE_RAGE_COST:
                self._apply_melee_attack_effects('heroic_strike', self.calcs.heroic_strike(), False, AttackType.HEROIC_STRIKE, Hand.MAIN, rage_cost=knowledge.HEROIC_STRIKE_RAGE_COST)
                self._add_event(0.0, EventType.HEROIC_STRIKE_LANDED)
            else:
                self._apply_melee_attack_effects('white_main', self.calcs.white_hit(Hand.MAIN), False, AttackType.WHITE, Hand.MAIN)
            self.state['heroic_strike_toggled'] = False
        elif event_type == EventType.WHITE_HIT_OFF:
            self.next_white_hit_off = self._add_event(self.calcs.current_speed(Hand.OFF), EventType.WHITE_HIT_OFF)
            self._apply_melee_attack_effects('white_off', self.calcs.white_hit(Hand.OFF), False, AttackType.WHITE, Hand.OFF)
        elif event_type == EventType.HAND_OF_JUSTICE_PROC:
            self._apply_melee_attack_effects('hand_of_justice_proc', self.calcs.white_hit(Hand.MAIN), False, AttackType.WHITE, Hand.MAIN, is_white_proc=True)
        elif event_type == EventType.THRASH_BLADE_PROC:
            self._apply_melee_attack_effects('thrash_blade_proc', self.calcs.white_hit(Hand.MAIN), False, AttackType.WHITE, Hand.MAIN, is_white_proc=True)
        elif event_type == EventType.IRONFOE_PROC:
            self._apply_melee_attack_effects('ironfoe_proc', self.calcs.white_hit(Hand.MAIN), False, AttackType.WHITE, Hand.MAIN, is_white_proc=True)
            self._apply_melee_attack_effects('ironfoe_proc', self.calcs.white_hit(Hand.MAIN), False, AttackType.WHITE, Hand.MAIN, is_white_proc=True)
        elif event_type == EventType.RAGE_GAINED:
            if self.state['death_wish_available']:
                use_death_wish()
            do_rota()
            use_heroic_strike()
        elif event_type == EventType.HEROIC_STRIKE_LANDED:
            use_heroic_strike()
        elif event_type == EventType.CRUSADER_MAIN_PROC:
            if self.crusader_main_proc_end_event is None:
                self.crusader_main_proc_end_event = self._add_event(knowledge.CRUSADER_DURATION, EventType.CRUSADER_MAIN_PROC_END)
                self.log(f"{self._log_entry_beginning()} Crusader Main Hand Proc\n")
            else:
                self.crusader_main_proc_end_event.time = self.current_time_seconds + knowledge.CRUSADER_DURATION
                self.event_queue.sort()
                self.log(f"{self._log_entry_beginning()} Crusader Main Hand Proc refreshed\n")
            self.player.buffs.add(PlayerBuffs.CRUSADER_MAIN)
        elif event_type == EventType.CRUSADER_MAIN_PROC_END:
            self.crusader_main_proc_end_event = None
            self.player.buffs.remove(PlayerBuffs.CRUSADER_MAIN)
            self.log(f"{self._log_entry_beginning()} Crusader Main Hand Proc fades\n")
        elif event_type == EventType.CRUSADER_OFF_PROC:
            if self.crusader_off_proc_end_event is None:
                self.crusader_off_proc_end_event = self._add_event(knowledge.CRUSADER_DURATION, EventType.CRUSADER_OFF_PROC_END)
                self.log(f"{self._log_entry_beginning()} Crusader Off Hand Proc\n")
            else:
                self.crusader_off_proc_end_event.time = self.current_time_seconds + knowledge.CRUSADER_DURATION
                self.event_queue.sort()
                self.log(f"{self._log_entry_beginning()} Crusader Off Hand Proc refreshed\n")
            self.player.buffs.add(PlayerBuffs.CRUSADER_OFF)
        elif event_type == EventType.CRUSADER_OFF_PROC_END:
            self.crusader_off_proc_end_event = None
            self.player.buffs.remove(PlayerBuffs.CRUSADER_OFF)
            self.log(f"{self._log_entry_beginning()} Crusader Off Hand Proc fades\n")

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
            self.state['rage'] = min(knowledge.MAX_RAGE, self.state['rage'] + rage)
            self._add_event(0.0, EventType.RAGE_GAINED)
            self.log(f'{self._log_entry_beginning(ability)} generates {rage} rage\n')
            self.log(f"{self._log_entry_beginning()} Rage={self.state['rage']}\n")

    def _apply_melee_attack_effects(self, ability, attack_result_damage_rage_tuple, triggers_gcd, attack_type, hand,
                                    rage_cost=None, base_rage_cost=None, is_white_proc=False):
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
                    event.time = self.current_time_seconds + (event.time - self.current_time_seconds)*knowledge.FLURRY_FACTOR
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

        def handle_procs(hand):
            if Proc.HAND_OF_JUSTICE in self.player.procs:
                if random.random() < knowledge.HAND_OF_JUSTICE_PROC_CHANCE:
                    self._add_event(0.0, EventType.HAND_OF_JUSTICE_PROC)
            # Not implemented on-next-swing for simplicity, difference should be negligible
            if Proc.THRASH_BLADE_MAIN in self.player.procs:
                # ~1.2 PPM =~ 5% PPH
                if hand == Hand.MAIN and random.random() < knowledge.THRASH_BLADE_PROC_CHANCE:
                    self._add_event(0.0, EventType.THRASH_BLADE_PROC)
            if Proc.THRASH_BLADE_OFF in self.player.procs:
                # ~1.2 PPM =~ 5% PPH
                if hand == hand.OFF and random.random() < knowledge.THRASH_BLADE_PROC_CHANCE:
                    self._add_event(0.0, EventType.THRASH_BLADE_PROC)
            if Proc.IRONFOE in self.player.procs:
                if hand == Hand.MAIN and random.random() < knowledge.IRONFOE_PROC_CHANCE:
                    self._add_event(0.0, EventType.IRONFOE_PROC)

            # PPM converted to PPH in the interval [0, 1]
            current_stats = self.calcs.current_stats()
            if hand == Hand.MAIN and random.random() < (knowledge.CRUSADER_PPM * current_stats['speed_main_hand'] / 60):
                self._add_event(0.0, EventType.CRUSADER_MAIN_PROC)
            if hand == Hand.OFF and random.random() < (knowledge.CRUSADER_PPM * current_stats['speed_off_hand'] / 60):
                self._add_event(0.0, EventType.CRUSADER_OFF_PROC)

        attack_result, damage, rage_gained = attack_result_damage_rage_tuple
        if rage_cost is not None:
            self._consume_rage(ability, rage_cost, attack_result, base_rage_cost=base_rage_cost)
        apply_damage(ability, damage, attack_result)
        self._add_rage(ability, rage_gained)
        if attack_result == AttackResult.DODGE:
            self.state['overpower_available_till'] = self.current_time_seconds + knowledge.OVERPOWER_AVAILABILITY_DURATION
            self._add_event(0.0, EventType.ATTACK_DODGED)

        if (attack_type == AttackType.WHITE and not is_white_proc) or attack_type == AttackType.HEROIC_STRIKE:
            apply_flurry(hand)

        if triggers_gcd:
            self.state['on_gcd'] = True
            self._add_event(knowledge.GCD_DURATION, EventType.GCD_END)

        handle_procs(hand)

        self.ability_log.append(AbilityLogEntry(ability, attack_result, damage))

    def _consume_rage(self, ability, rage, attack_result, base_rage_cost=None):
        assert rage > 0
        assert self.state['rage'] >= rage
        # Dodged and parried abilities don't cost rage: https://forum.nostalrius.org/viewtopic.php?f=36&t=2670&start=20
        if attack_result is None or attack_result != AttackResult.DODGE:
            # Execute miss only costs base rage cost, not all rage available
            if attack_result is not None and attack_result == AttackResult.MISS and base_rage_cost is not None:
                rage = base_rage_cost
            self.state['rage'] -= rage
            self.log(f'{self._log_entry_beginning(ability)} consumes {rage} rage\n')
            self.log(f"{self._log_entry_beginning()} Rage={self.state['rage']}\n")

    def _log_entry_beginning(self, ability=None):
        log_entry = f'[{self.current_time_seconds:.2f}]'
        if ability is not None:
            log_entry += f' {Constants.ability_names_lookup[ability]}'

        return log_entry


def do_sim(player, boss, config):
    def do_n_runs(player, boss, config):
        def sample_fight_duration(mu, sigma):
            """Normal distribution truncated at +/- 3*sigma"""
            f = random.gauss(mu, sigma)
            max_ = mu + 3*sigma
            min_ = mu - 3*sigma
            if f > max_:
                f = max_
            elif f < min_:
                f = min_

            return f

        result_list = []
        for run_nr in range(config.n_runs):
            # Call copy constructor to start with a fresh state
            player = Player.from_player(player)
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

    result_baseline = do_n_runs(player, boss, config)
    stat_weights = dict()
    # for stat, increase in config.stat_increase_tuples:
    #     stats_copy = copy.copy(partial_buffed_permanent_stats)
    #     stats_copy[stat] += increase
    #     result = do_n_runs(faction, race, class_, spec, items, stats_copy, boss, config)
    #     stat_weights[stat] = (result.dps - result_baseline.dps) / increase

    return result_baseline, stat_weights
