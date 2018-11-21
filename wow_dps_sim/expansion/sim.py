import heapq
import os
import random
import time

from wow_dps_sim.constants import Constants
from wow_dps_sim.entities import AbilityLogEntry, Event, WhiteHitEvent
from wow_dps_sim.enums import AttackResult, AttackType, EventType, Hand, PlayerBuffs, Proc, Stance
from wow_dps_sim.helpers import from_module_import_x


class Sim:
    epsilon = 1e-7

    def __init__(self, expansion, player, fight_duration, logging=False, run_nr=None):
        expansion_module = 'wow_dps_sim.expansion.' + expansion
        Calcs = from_module_import_x(expansion_module + '.calcs', 'Calcs')
        self.calcs = Calcs(expansion, player)
        self.knowledge = from_module_import_x(expansion_module, 'knowledge')
        self.rotation_config = from_module_import_x(expansion_module, 'rotation_config')

        self.player = player
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
            'recklessness_available': True,
            'flurry_charges': 0,
            'heroic_strike_toggled': False,
            'execute_phase': False,
        }

        self._add_event(0.0, EventType.BLOODRAGE_CD_END)
        for on_use_effect in self.player.on_use_effects:
            self._add_event(0.0, Constants.on_use_effect_to_cd_end_event_type[on_use_effect])
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
        # self.log(f"{self._log_entry_beginning()} flurry_charges={self.state['flurry_charges']}\n")
        event_type = event.event_type
        if event_type == EventType.BLOODRAGE_CD_END:
            self._add_rage('bloodrage', self.knowledge.BLOODRAGE_BASE_RAGE)
            for i in range(self.knowledge.BLOODRAGE_DURATION):
                self._add_event(i + 1, EventType.BLOODRAGE_ADD_RAGE_OVER_TIME)
            self._add_event(self.knowledge.BLOODRAGE_CD, EventType.BLOODRAGE_CD_END)
        elif event_type == EventType.BLOODRAGE_ADD_RAGE_OVER_TIME:
            self._add_rage('bloodrage', self.knowledge.BLOODRAGE_TICK_RAGE)
        elif event_type == EventType.DEATH_WISH_END:
            self.player.buffs.remove(PlayerBuffs.DEATH_WISH)
            self.log(f"{self._log_entry_beginning('death_wish')} fades\n")
        elif event_type == EventType.DEATH_WISH_CD_END:
            self.state['death_wish_available'] = True
            self._do_rota()
        elif event_type == EventType.RECKLESSNESS_END:
            self.player.buffs.remove(PlayerBuffs.RECKLESSNESS)
            self.log(f"{self._log_entry_beginning('recklessness')} fades\n")
        elif event_type == EventType.RECKLESSNESS_CD_END:
            self.state['recklessness_available'] = True
            self._do_rota()
        elif event_type == EventType.BLOODTHIRST_CD_END:
            self.state['bloodthirst_available'] = True
            self._do_rota()
        elif event_type == EventType.WHIRLWIND_CD_END:
            self.state['whirlwind_available'] = True
            self._do_rota()
        elif event_type == EventType.OVERPOWER_CD_END:
            self.state['overpower_not_on_cd'] = True
            self._do_rota()
        elif event_type == EventType.ATTACK_DODGED:
            self._do_rota()
        elif event_type == EventType.GCD_END:
            self.state['on_gcd'] = False
            self._do_rota()
        elif event_type == EventType.STANCE_CD_END:
            self.state['on_stance_cd'] = False
            # TODO (?) Edge case: @ Battle Stance after OP, BT available / available very very soon, rage >= 30: use BT before switching
            if self.player.stance != Stance.BERSERKER:
                self._switch_stance(Stance.BERSERKER)
            self._do_rota()
        elif event_type == EventType.WHITE_HIT_MAIN:
            self.next_white_hit_main = self._add_event(self.calcs.current_speed(Hand.MAIN), EventType.WHITE_HIT_MAIN)
            if self.state['heroic_strike_toggled'] and self.state['rage'] >= self.knowledge.HEROIC_STRIKE_RAGE_COST:
                self._apply_melee_attack_effects('heroic_strike', self.calcs.heroic_strike(), False, AttackType.HEROIC_STRIKE, Hand.MAIN, rage_cost=self.knowledge.HEROIC_STRIKE_RAGE_COST)
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
            self._do_rota()
            self._use_heroic_strike()
        elif event_type == EventType.HEROIC_STRIKE_LANDED:
            self._use_heroic_strike()
        elif event_type == EventType.CRUSADER_MAIN_PROC:
            if self.crusader_main_proc_end_event is None:
                self.crusader_main_proc_end_event = self._add_event(self.knowledge.CRUSADER_DURATION, EventType.CRUSADER_MAIN_PROC_END)
                self.log(f"{self._log_entry_beginning()} Crusader Main Hand Proc\n")
            else:
                self.crusader_main_proc_end_event.time = self.current_time_seconds + self.knowledge.CRUSADER_DURATION
                self.event_queue.sort()
                self.log(f"{self._log_entry_beginning()} Crusader Main Hand Proc refreshed\n")
            self.player.buffs.add(PlayerBuffs.CRUSADER_MAIN)
        elif event_type == EventType.CRUSADER_MAIN_PROC_END:
            self.crusader_main_proc_end_event = None
            self.player.buffs.remove(PlayerBuffs.CRUSADER_MAIN)
            self.log(f"{self._log_entry_beginning()} Crusader Main Hand Proc fades\n")
        elif event_type == EventType.CRUSADER_OFF_PROC:
            if self.crusader_off_proc_end_event is None:
                self.crusader_off_proc_end_event = self._add_event(self.knowledge.CRUSADER_DURATION, EventType.CRUSADER_OFF_PROC_END)
                self.log(f"{self._log_entry_beginning()} Crusader Off Hand Proc\n")
            else:
                self.crusader_off_proc_end_event.time = self.current_time_seconds + self.knowledge.CRUSADER_DURATION
                self.event_queue.sort()
                self.log(f"{self._log_entry_beginning()} Crusader Off Hand Proc refreshed\n")
            self.player.buffs.add(PlayerBuffs.CRUSADER_OFF)
        elif event_type == EventType.CRUSADER_OFF_PROC_END:
            self.crusader_off_proc_end_event = None
            self.player.buffs.remove(PlayerBuffs.CRUSADER_OFF)
            self.log(f"{self._log_entry_beginning()} Crusader Off Hand Proc fades\n")
        elif event_type == EventType.KISS_OF_THE_SPIDER_CD_END:
            self.player.buffs.add(PlayerBuffs.KISS_OF_THE_SPIDER)
            self._add_event(self.knowledge.KISS_OF_THE_SPIDER_DURATION, EventType.KISS_OF_THE_SPIDER_END)
            self._add_event(self.knowledge.KISS_OF_THE_SPIDER_CD, event_type)
            self.log(f"{self._log_entry_beginning('kiss_of_the_spider')} activated\n")
        elif event_type == EventType.KISS_OF_THE_SPIDER_END:
            self.player.buffs.remove(PlayerBuffs.KISS_OF_THE_SPIDER)
            self.log(f"{self._log_entry_beginning('kiss_of_the_spider')} fades\n")
        elif event_type == EventType.SLAYERS_CREST_CD_END:
            self.player.buffs.add(PlayerBuffs.SLAYERS_CREST)
            self._add_event(self.knowledge.SLAYERS_CREST_DURATION, EventType.SLAYERS_CREST_END)
            self._add_event(self.knowledge.SLAYERS_CREST_CD, event_type)
            self.log(f"{self._log_entry_beginning('slayers_crest')} activated\n")
        elif event_type == EventType.SLAYERS_CREST_END:
            self.player.buffs.remove(PlayerBuffs.SLAYERS_CREST)
            self.log(f"{self._log_entry_beginning('slayers_crest')} fades\n")
        elif event_type == EventType.JUJU_FLURRY_CD_END:
            self.player.buffs.add(PlayerBuffs.JUJU_FLURRY)
            self._add_event(self.knowledge.JUJU_FLURRY_DURATION, EventType.JUJU_FLURRY_END)
            self._add_event(self.knowledge.JUJU_FLURRY_CD, event_type)
            self.log(f"{self._log_entry_beginning('juju_flurry')} activated\n")
        elif event_type == EventType.JUJU_FLURRY_END:
            self.player.buffs.remove(PlayerBuffs.JUJU_FLURRY)
            self.log(f"{self._log_entry_beginning('juju_flurry')} fades\n")
        elif event_type == EventType.MIGHTY_RAGE_POTION_CD_END:
            self._add_rage('mighty_rage_potion', random.randint(self.knowledge.MIGHTY_RAGE_POTION_MIN_RAGE, self.knowledge.MIGHTY_RAGE_POTION_MAX_RAGE))
            self.player.buffs.add(PlayerBuffs.MIGHTY_RAGE_POTION)
            self._add_event(self.knowledge.MIGHTY_RAGE_POTION_DURATION, EventType.MIGHTY_RAGE_POTION_END)
            self._add_event(self.knowledge.MIGHTY_RAGE_POTION_CD, event_type)
            self.log(f"{self._log_entry_beginning('mighty_rage_potion')} activated\n")
        elif event_type == EventType.MIGHTY_RAGE_POTION_END:
            self.player.buffs.remove(PlayerBuffs.MIGHTY_RAGE_POTION)
            self.log(f"{self._log_entry_beginning('mighty_rage_potion')} fades\n")

    def _do_rota(self):
        if self.state['execute_phase']:
            if self._use_death_wish():
                pass
            elif self._use_recklessness():
                pass
            elif self._use_execute():
                pass
        else:
            if self._use_bloodthirst():
                pass
            elif self._use_whirlwind():
                pass
            # OP vs. no OP:
            # 586 vs. 573 DPS @ pre-raid BIS
            # 886 vs. 862 DPS @ Naxx BIS
            elif self._use_overpower():
                pass
            elif self._use_death_wish():
                pass
            elif self._use_recklessness():
                pass

    def _switch_stance(self, stance):
        assert self.player.stance != stance

        if not self.state['on_stance_cd']:
            self.player.stance = stance
            self.state['on_stance_cd'] = True
            self._add_event(self.knowledge.STANCE_CD_DURATION, EventType.STANCE_CD_END)
            self.log(f'{self._log_entry_beginning()} Switching stance to {stance}\n')
            self.state['rage'] = min(self.knowledge.MAX_RAGE_AFTER_STANCE_SWITCH, self.state['rage'])
            self.log(f"{self._log_entry_beginning()} Rage={self.state['rage']}\n")

            return True
        else:
            return False

    def _use_bloodthirst(self):
        if not self.state['on_gcd'] and self.state['bloodthirst_available'] and self.state['rage'] >= self.knowledge.BLOODTHIRST_RAGE_COST:
            ability = 'bloodthirst'
            self.state['bloodthirst_available'] = False
            self._apply_melee_attack_effects(ability, self.calcs.bloodthirst(), True, AttackType.YELLOW, Hand.MAIN,
                                             rage_cost=self.knowledge.BLOODTHIRST_RAGE_COST)
            added_event = self._add_event(self.knowledge.BLOODTHIRST_CD, EventType.BLOODTHIRST_CD_END)
            self.state['next_bloodthirst_available_at'] = added_event.time

            return True
        else:
            return False

    def _use_death_wish(self):
        if not self.state['on_gcd'] and self.state['death_wish_available'] and self.state['rage'] >= self.knowledge.DEATH_WISH_RAGE_COST:
            self.state['death_wish_available'] = False
            self._consume_rage('death_wish', self.knowledge.DEATH_WISH_RAGE_COST, None)
            self.player.buffs.add(PlayerBuffs.DEATH_WISH)
            self._trigger_gcd()
            self._add_event(self.knowledge.DEATH_WISH_DURATION, EventType.DEATH_WISH_END)
            self._add_event(self.knowledge.DEATH_WISH_CD, EventType.DEATH_WISH_CD_END)
            self.log(f"{self._log_entry_beginning('death_wish')} activated\n")

            return True
        else:
            return False

    def _use_execute(self):
        if not self.state['on_gcd'] and self.state['rage'] >= self.knowledge.EXECUTE_BASE_RAGE_COST:
            ability = 'execute'
            self._apply_melee_attack_effects(
                ability, self.calcs.execute(self.state['rage']), True, AttackType.YELLOW, Hand.MAIN,
                rage_cost=self.state['rage'], base_rage_cost=self.knowledge.EXECUTE_BASE_RAGE_COST
            )

            return True
        else:
            return False

    def _use_heroic_strike(self):
        if not self.state['execute_phase'] and self.state['rage'] >= self.rotation_config.HEROIC_STRIKE_MIN_RAGE_THRESHOLD:
            self.state['heroic_strike_toggled'] = True

    def _use_overpower(self):
        if (
            not self.state['on_gcd']
            and self.state['overpower_not_on_cd'] and (self.state['overpower_available_till'] - self.current_time_seconds) > self.epsilon
            and self.state['rage'] >= self.knowledge.OVERPOWER_RAGE_COST and self.state['rage'] <= self.rotation_config.OVERPOWER_MAX_RAGE_THRESHOLD
            and (self.state['next_bloodthirst_available_at'] - self.current_time_seconds) > self.rotation_config.OVERPOWER_MIN_BLOODTHIRST_CD_LEFT
            and (self.state['next_whirlwind_available_at'] - self.current_time_seconds) > self.rotation_config.OVERPOWER_MIN_WHIRLWIND_CD_LEFT
        ):
            assert self.player.stance == Stance.BERSERKER
            assert not self.state['bloodthirst_available']
            assert not self.state['whirlwind_available']

            if self._switch_stance(Stance.BATTLE):
                ability = 'overpower'
                self.state['overpower_not_on_cd'] = False
                self.state['overpower_available_till'] = self.current_time_seconds
                self._apply_melee_attack_effects(ability, self.calcs.overpower(), True, AttackType.YELLOW, Hand.MAIN,
                                                 rage_cost=self.knowledge.OVERPOWER_RAGE_COST)
                self._add_event(self.knowledge.OVERPOWER_CD, EventType.OVERPOWER_CD_END)

                return True

        return False

    def _use_recklessness(self):
        if not self.state['on_gcd'] and self.state['recklessness_available'] and self.player.stance == Stance.BERSERKER:
            self.state['recklessness_available'] = False
            self.player.buffs.add(PlayerBuffs.RECKLESSNESS)
            self._trigger_gcd()
            self._add_event(self.knowledge.RECKLESSNESS_DURATION, EventType.RECKLESSNESS_END)
            self._add_event(self.knowledge.RECKLESSNESS_CD, EventType.RECKLESSNESS_CD_END)
            self.log(f"{self._log_entry_beginning('recklessness')} activated\n")

            return True
        else:
            return False

    def _use_whirlwind(self):
        # When between 25 and 29 rage and both BT + WW are available, both my intuition and this sim tell us
        # it's slightly better to delay WW and wait until 30 rage are available to use BT instead.
        if (
            not self.state['on_gcd'] and not self.state['bloodthirst_available']
            and self.state['whirlwind_available'] and self.player.stance == Stance.BERSERKER and self.state[
            'rage'] >= self.knowledge.WHIRLWIND_RAGE_COST
        ):
            ability = 'whirlwind'
            self.state['whirlwind_available'] = False
            self._apply_melee_attack_effects(ability, self.calcs.whirlwind(), True, AttackType.YELLOW, Hand.MAIN,
                                             rage_cost=self.knowledge.WHIRLWIND_RAGE_COST)
            added_event = self._add_event(self.knowledge.WHIRLWIND_CD, EventType.WHIRLWIND_CD_END)
            self.state['next_whirlwind_available_at'] = added_event.time

            return True
        else:
            return False

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
            self.state['rage'] = min(self.knowledge.MAX_RAGE, self.state['rage'] + rage)
            self._add_event(0.0, EventType.RAGE_GAINED)
            self.log(f'{self._log_entry_beginning(ability)} generates {rage} rage\n')
            self.log(f"{self._log_entry_beginning()} Rage={self.state['rage']}\n")

    def _apply_melee_attack_effects(self, ability, attack_result_damage_rage_tuple, triggers_gcd, attack_type, hand,
                                    rage_cost=None, base_rage_cost=None, is_white_proc=False):
        attack_result, damage, rage_gained = attack_result_damage_rage_tuple
        if rage_cost is not None:
            self._consume_rage(ability, rage_cost, attack_result, base_rage_cost=base_rage_cost)
        self._apply_damage(ability, damage, attack_result)
        self._add_rage(ability, rage_gained)
        if attack_result == AttackResult.DODGE:
            self.state['overpower_available_till'] = self.current_time_seconds + self.knowledge.OVERPOWER_AVAILABILITY_DURATION
            self._add_event(0.0, EventType.ATTACK_DODGED)

        self._handle_flurry(attack_result, attack_type, hand, is_white_proc)

        if triggers_gcd:
            self._trigger_gcd()

        self._handle_procs(attack_result, hand)

        self.ability_log.append(AbilityLogEntry(ability, attack_result, damage))

    def _apply_damage(self, ability, damage, attack_result):
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
    def _handle_flurry(self, attack_result, attack_type, hand_current_white_hit, is_white_proc):
        def apply_flurry_to_event(event):
            if not event.has_flurry:
                event_str_before = str(event)
                event.time = self.current_time_seconds + (event.time - self.current_time_seconds) * self.knowledge.FLURRY_FACTOR
                event.has_flurry = True
                self.log(f'{self._log_entry_beginning()} Applying flurry, before={{{event_str_before}}}, after={{{event}}}\n')

                return True
            else:
                return False

        resort_events = False
        # New flurry proc, apply to swings of both hands
        if attack_result == AttackResult.CRIT:
            self.log(f'{self._log_entry_beginning()} Flurry proc\n')
            self.state['flurry_charges'] = 3
            flurry_applied_main = apply_flurry_to_event(self.next_white_hit_main)
            flurry_applied_off = apply_flurry_to_event(self.next_white_hit_off)
            resort_events = flurry_applied_main or flurry_applied_off
            self.state['flurry_charges'] = 1
        # Existing flurry charge, only apply to the new swing of the hand that just landed a hit since the existing swing (other hand)
        # will already have flurry at this point.
        elif (
            self.state['flurry_charges'] > 0
            and (
                (attack_type == AttackType.WHITE and not is_white_proc)
                or attack_type == AttackType.HEROIC_STRIKE
            )
        ):
            resort_events = apply_flurry_to_event(self.next_white_hit_off if hand_current_white_hit == Hand.OFF else self.next_white_hit_main)
            self.state['flurry_charges'] -= 1

        if resort_events:
            self.event_queue.sort()

    def _handle_procs(self, attack_result, hand):
        if attack_result != AttackResult.MISS and attack_result != AttackResult.DODGE:
            if Proc.HAND_OF_JUSTICE in self.player.procs:
                if random.random() < self.knowledge.HAND_OF_JUSTICE_PROC_CHANCE:
                    self._add_event(0.0, EventType.HAND_OF_JUSTICE_PROC)
            # Not implemented on-next-swing for simplicity, difference should be negligible
            if Proc.THRASH_BLADE_MAIN in self.player.procs:
                # ~1.2 PPM =~ 5% PPH
                if hand == Hand.MAIN and random.random() < self.knowledge.THRASH_BLADE_PROC_CHANCE:
                    self._add_event(0.0, EventType.THRASH_BLADE_PROC)
            if Proc.THRASH_BLADE_OFF in self.player.procs:
                # ~1.2 PPM =~ 5% PPH
                if hand == hand.OFF and random.random() < self.knowledge.THRASH_BLADE_PROC_CHANCE:
                    self._add_event(0.0, EventType.THRASH_BLADE_PROC)
            if Proc.IRONFOE in self.player.procs:
                if hand == Hand.MAIN and random.random() < self.knowledge.IRONFOE_PROC_CHANCE:
                    self._add_event(0.0, EventType.IRONFOE_PROC)

            # PPM converted to PPH in the interval [0, 1]
            if Proc.CRUSADER_MAIN in self.player.procs or Proc.CRUSADER_OFF in self.player.procs:
                current_stats = self.calcs.current_stats()
                if Proc.CRUSADER_MAIN in self.player.procs:
                    if hand == Hand.MAIN and random.random() < (self.knowledge.CRUSADER_PPM * current_stats['speed_main_hand'] / 60):
                        self._add_event(0.0, EventType.CRUSADER_MAIN_PROC)
                if Proc.CRUSADER_OFF in self.player.procs:
                    if hand == Hand.OFF and random.random() < (self.knowledge.CRUSADER_PPM * current_stats['speed_off_hand'] / 60):
                        self._add_event(0.0, EventType.CRUSADER_OFF_PROC)

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

    def _trigger_gcd(self):
        self.state['on_gcd'] = True
        self._add_event(self.knowledge.GCD_DURATION, EventType.GCD_END)
