import random

from wow_dps_sim.enums import Ability, AttackResult, AttackType, EventType, Hand, PlayerBuffs, Proc, Stance
import wow_dps_sim.expansion.sim


class Sim(wow_dps_sim.expansion.sim.Sim):
    def __init__(self, expansion, player, fight_duration, logging=False, run_nr=None):
        super().__init__(expansion, player, fight_duration, logging, run_nr)

        self.state['rampage_stacks'] = 0
        self.state['rampage_available_till'] = 0.0
        self.state['hourglass_of_the_unraveller_on_icd'] = False

        self.rampage_end_event = None
        self.drakefist_hammer_proc_end_event = None
        self.blackout_truncheon_proc_end_event = None
        self.executioner_proc_end_event = None
        self.mongoose_main_proc_end_event = None
        self.mongoose_off_proc_end_event = None

        self._add_event(self.knowledge.ANGER_MANAGEMENT_TIME_BETWEEN_TICKS, EventType.ANGER_MANAGEMENT_TICK)

    def handle_event(self, event):
        super().handle_event(event)

        event_type = event.event_type
        if event_type == EventType.RAMPAGE_END:
            self.player.buffs.remove(PlayerBuffs.RAMPAGE)
            self.state['rampage_stacks'] = 0
            self.rampage_end_event = None
            self.log(f"{self._log_entry_beginning(Ability.RAMPAGE)} fades\n")
        elif event_type == EventType.ATTACK_CRIT:
            self._do_rota()
        elif event_type == EventType.ANGER_MANAGEMENT_TICK:
            self._add_rage(Ability.ANGER_MANAGEMENT, self.knowledge.ANGER_MANAGEMENT_TICK_RAGE)
            self._add_event(self.knowledge.ANGER_MANAGEMENT_TIME_BETWEEN_TICKS, EventType.ANGER_MANAGEMENT_TICK)
        elif event_type == EventType.DRAKEFIST_HAMMER_PROC:
            if self.drakefist_hammer_proc_end_event is None:
                self.drakefist_hammer_proc_end_event = self._add_event(self.knowledge.DRAKEFIST_HAMMER_DURATION, EventType.DRAKEFIST_HAMMER_PROC_END)
                self.log(f"{self._log_entry_beginning()} Drakefist Hammer Proc\n")
            else:
                self.drakefist_hammer_proc_end_event.time = self.current_time_seconds + self.knowledge.DRAKEFIST_HAMMER_DURATION
                self.event_queue.sort()
                self.log(f"{self._log_entry_beginning()} Drakefist Hammer Proc refreshed\n")
            self.player.buffs.add(PlayerBuffs.DRAKEFIST_HAMMER)
        elif event_type == EventType.DRAKEFIST_HAMMER_PROC_END:
            self.drakefist_hammer_proc_end_event = None
            self.player.buffs.remove(PlayerBuffs.DRAKEFIST_HAMMER)
            self.log(f"{self._log_entry_beginning()} Drakefist Hammer Proc fades\n")
        elif event_type == EventType.BLACKOUT_TRUNCHEON_PROC:
            if self.blackout_truncheon_proc_end_event is None:
                self.blackout_truncheon_proc_end_event = self._add_event(self.knowledge.BLACKOUT_TRUNCHEON_DURATION, EventType.BLACKOUT_TRUNCHEON_PROC_END)
                self.log(f"{self._log_entry_beginning()} Blackout Truncheon Proc\n")
            else:
                self.blackout_truncheon_proc_end_event.time = self.current_time_seconds + self.knowledge.BLACKOUT_TRUNCHEON_DURATION
                self.event_queue.sort()
                self.log(f"{self._log_entry_beginning()} Blackout Truncheon Proc refreshed\n")
            self.player.buffs.add(PlayerBuffs.BLACKOUT_TRUNCHEON)
        elif event_type == EventType.BLACKOUT_TRUNCHEON_PROC_END:
            self.blackout_truncheon_proc_end_event = None
            self.player.buffs.remove(PlayerBuffs.BLACKOUT_TRUNCHEON)
            self.log(f"{self._log_entry_beginning()} Blackout Truncheon Proc fades\n")
        elif event_type == EventType.HOURGLASS_OF_THE_UNRAVELLER_PROC:
            # Additional check is necessary for rare cases where attack A procs hourglass and WF and that WF
            # procs the hourglass again, with the WF event coming in before the first proc event, leading to
            # 2 proc events.
            if not self.state['hourglass_of_the_unraveller_on_icd']:
                self.player.buffs.add(PlayerBuffs.HOURGLASS_OF_THE_UNRAVELLER)
                self.state['hourglass_of_the_unraveller_on_icd'] = True
                self._add_event(self.knowledge.HOURGLASS_OF_THE_UNRAVELLER_DURATION, EventType.HOURGLASS_OF_THE_UNRAVELLER_PROC_END)
                self._add_event(self.knowledge.HOURGLASS_OF_THE_UNRAVELLER_ICD_DURATION, EventType.HOURGLASS_OF_THE_UNRAVELLER_ICD_END)
                self.log(f"{self._log_entry_beginning(Ability.HOURGLASS_OF_THE_UNRAVELLER)} activated\n")
        elif event_type == EventType.HOURGLASS_OF_THE_UNRAVELLER_PROC_END:
            self.player.buffs.remove(PlayerBuffs.HOURGLASS_OF_THE_UNRAVELLER)
            self.log(f"{self._log_entry_beginning(Ability.HOURGLASS_OF_THE_UNRAVELLER)} fades\n")
        elif event_type == EventType.HOURGLASS_OF_THE_UNRAVELLER_ICD_END:
            self.state['hourglass_of_the_unraveller_on_icd'] = False
        elif event_type == EventType.EXECUTIONER_PROC:
            if self.executioner_proc_end_event is None:
                self.executioner_proc_end_event = self._add_event(self.knowledge.EXECUTIONER_DURATION, EventType.EXECUTIONER_PROC_END)
                self.log(f"{self._log_entry_beginning()} Executioner Proc\n")
            else:
                self.executioner_proc_end_event.time = self.current_time_seconds + self.knowledge.EXECUTIONER_DURATION
                self.event_queue.sort()
                self.log(f"{self._log_entry_beginning()} Executioner Proc refreshed\n")
            self.player.buffs.add(PlayerBuffs.EXECUTIONER)
        elif event_type == EventType.EXECUTIONER_PROC_END:
            self.executioner_proc_end_event = None
            self.player.buffs.remove(PlayerBuffs.EXECUTIONER)
            self.log(f"{self._log_entry_beginning()} Executioner Proc fades\n")
        elif event_type == EventType.MONGOOSE_MAIN_PROC:
            if self.mongoose_main_proc_end_event is None:
                self.mongoose_main_proc_end_event = self._add_event(self.knowledge.MONGOOSE_DURATION, EventType.MONGOOSE_MAIN_PROC_END)
                self.log(f"{self._log_entry_beginning()} Mongoose Main Hand Proc\n")
            else:
                self.mongoose_main_proc_end_event.time = self.current_time_seconds + self.knowledge.MONGOOSE_DURATION
                self.event_queue.sort()
                self.log(f"{self._log_entry_beginning()} Mongoose Main Hand Proc refreshed\n")
            self.player.buffs.add(PlayerBuffs.MONGOOSE_MAIN)
        elif event_type == EventType.MONGOOSE_MAIN_PROC_END:
            self.mongoose_main_proc_end_event = None
            self.player.buffs.remove(PlayerBuffs.MONGOOSE_MAIN)
            self.log(f"{self._log_entry_beginning()} Mongoose Main Hand Proc fades\n")
        elif event_type == EventType.MONGOOSE_OFF_PROC:
            if self.mongoose_off_proc_end_event is None:
                self.mongoose_off_proc_end_event = self._add_event(self.knowledge.MONGOOSE_DURATION, EventType.MONGOOSE_OFF_PROC_END)
                self.log(f"{self._log_entry_beginning()} Mongoose Off Hand Proc\n")
            else:
                self.mongoose_off_proc_end_event.time = self.current_time_seconds + self.knowledge.MONGOOSE_DURATION
                self.event_queue.sort()
                self.log(f"{self._log_entry_beginning()} Mongoose Off Hand Proc refreshed\n")
            self.player.buffs.add(PlayerBuffs.MONGOOSE_OFF)
        elif event_type == EventType.MONGOOSE_OFF_PROC_END:
            self.mongoose_off_proc_end_event = None
            self.player.buffs.remove(PlayerBuffs.MONGOOSE_OFF)
            self.log(f"{self._log_entry_beginning()} Mongoose Off Hand Proc fades\n")
        elif event_type == EventType.BLOODLUST_BROOCH_CD_END:
            self.player.buffs.add(PlayerBuffs.BLOODLUST_BROOCH)
            self._add_event(self.knowledge.BLOODLUST_BROOCH_DURATION, EventType.BLOODLUST_BROOCH_END)
            self._add_event(self.knowledge.BLOODLUST_BROOCH_CD, event_type)
            self.log(f"{self._log_entry_beginning(Ability.BLOODLUST_BROOCH)} activated\n")
        elif event_type == EventType.BLOODLUST_BROOCH_END:
            self.player.buffs.remove(PlayerBuffs.BLOODLUST_BROOCH)
            self.log(f"{self._log_entry_beginning(Ability.BLOODLUST_BROOCH)} fades\n")
        elif event_type == EventType.DRUMS_OF_BATTLE_CD_END:
            self.player.buffs.add(PlayerBuffs.DRUMS_OF_BATTLE)
            self._add_event(self.knowledge.DRUMS_OF_BATTLE_DURATION, EventType.DRUMS_OF_BATTLE_END)
            self._add_event(self.knowledge.DRUMS_OF_BATTLE_CD, event_type)
            self.log(f"{self._log_entry_beginning(Ability.DRUMS_OF_BATTLE)} activated\n")
        elif event_type == EventType.DRUMS_OF_BATTLE_END:
            self.player.buffs.remove(PlayerBuffs.DRUMS_OF_BATTLE)
            self.log(f"{self._log_entry_beginning(Ability.DRUMS_OF_BATTLE)} fades\n")
        elif event_type == EventType.DRUMS_OF_WAR_CD_END:
            self.player.buffs.add(PlayerBuffs.DRUMS_OF_WAR)
            self._add_event(self.knowledge.DRUMS_OF_WAR_DURATION, EventType.DRUMS_OF_WAR_END)
            self._add_event(self.knowledge.DRUMS_OF_WAR_CD, event_type)
            self.log(f"{self._log_entry_beginning(Ability.DRUMS_OF_WAR)} activated\n")
        elif event_type == EventType.DRUMS_OF_WAR_END:
            self.player.buffs.remove(PlayerBuffs.DRUMS_OF_WAR)
            self.log(f"{self._log_entry_beginning(Ability.DRUMS_OF_WAR)} fades\n")
        elif event_type == EventType.HASTE_POTION_CD_END:
            self.player.buffs.add(PlayerBuffs.HASTE_POTION)
            self._add_event(self.knowledge.HASTE_POTION_DURATION, EventType.HASTE_POTION_END)
            self._add_event(self.knowledge.HASTE_POTION_CD, event_type)
            self.log(f"{self._log_entry_beginning(Ability.HASTE_POTION)} activated\n")
        elif event_type == EventType.HASTE_POTION_END:
            self.player.buffs.remove(PlayerBuffs.HASTE_POTION)
            self.log(f"{self._log_entry_beginning(Ability.HASTE_POTION)} fades\n")
        elif event_type == EventType.HEROISM_CD_END:
            self.player.buffs.add(PlayerBuffs.HEROISM)
            self._add_event(self.knowledge.HEROISM_DURATION, EventType.HEROISM_END)
            self._add_event(self.knowledge.HEROISM_CD, event_type)
            self.log(f"{self._log_entry_beginning(Ability.HEROISM)} activated\n")
        elif event_type == EventType.HEROISM_END:
            self.player.buffs.remove(PlayerBuffs.HEROISM)
            self.log(f"{self._log_entry_beginning(Ability.HEROISM)} fades\n")

    def _do_rota(self):
        if self.state['execute_phase']:
            if self._use_recklessness():
                pass
            # elif self._use_rampage(has_priority=True):
            #     pass
            elif self._use_bloodthirst():
                pass
            elif self._use_execute():
                pass
        else:
            if self._use_bloodthirst():
                pass
            elif self._use_whirlwind():
                pass
            elif self._use_rampage():
                pass
            elif self._use_recklessness():
                pass

    def _use_rampage(self, has_priority=False):
        if (
            not self.state['on_gcd']

            and (
                has_priority or (
                    (self.state['next_bloodthirst_available_at'] - self.current_time_seconds) > self.rotation_config.RAMPAGE_MIN_BLOODTHIRST_CD_LEFT
                    and
                    (self.state['next_whirlwind_available_at'] - self.current_time_seconds) > self.rotation_config.RAMPAGE_MIN_WHIRLWIND_CD_LEFT
                )
            )

            # TODO One could argue that for the sake of completeness, there should be a "rampage runs out in 5 sec" event
            # that leads to _do_rota being called.
            and (
                PlayerBuffs.RAMPAGE not in self.player.buffs
                or (self.rampage_end_event.time - self.current_time_seconds) < self.rotation_config.RAMPAGE_REFRESH_THRESHOLD
            )
            and self.state['rage'] >= self.knowledge.RAMPAGE_RAGE_COST
            and (self.state['rampage_available_till'] - self.current_time_seconds) > self.epsilon
        ):
            ability = Ability.RAMPAGE
            self._consume_rage(ability, self.knowledge.RAMPAGE_RAGE_COST, None)
            self.state['rampage_stacks'] = max(1, self.state['rampage_stacks'])
            self._trigger_gcd()
            if PlayerBuffs.RAMPAGE in self.player.buffs:
                self.log(f"{self._log_entry_beginning(ability)} refreshed, stacks={self.state['rampage_stacks']}\n")
                self.rampage_end_event.time = self.current_time_seconds + self.knowledge.RAMPAGE_DURATION
                self.event_queue.sort()
            else:
                self.log(f"{self._log_entry_beginning(ability)} activated, stacks={self.state['rampage_stacks']}\n")
                self.player.buffs.add(PlayerBuffs.RAMPAGE)
                self.rampage_end_event = self._add_event(self.knowledge.RAMPAGE_DURATION, EventType.RAMPAGE_END)

            return True
        else:
            return False

    def _use_whirlwind(self):
        # When between 25 and 29 rage and both BT + WW are available, both my intuition and this sim tell us
        # it's slightly better to delay WW and wait until 30 rage are available to use BT instead.
        if (
            not self.state['on_gcd'] and not self.state['bloodthirst_available']
            and self.state['whirlwind_available'] and self.player.stance == Stance.BERSERKER and self.state['rage'] >= self.knowledge.WHIRLWIND_RAGE_COST
        ):
            self.state['whirlwind_available'] = False
            self._apply_melee_attack_effects(Ability.WHIRLWIND_MAIN, self.calcs.whirlwind(Hand.MAIN), True, AttackType.YELLOW, Hand.MAIN,
                                             rage_cost=self.knowledge.WHIRLWIND_RAGE_COST)
            self._apply_melee_attack_effects(Ability.WHIRLWIND_OFF, self.calcs.whirlwind(Hand.OFF), False, AttackType.YELLOW, Hand.OFF)
            added_event = self._add_event(self.knowledge.WHIRLWIND_CD, EventType.WHIRLWIND_CD_END)
            self.state['next_whirlwind_available_at'] = added_event.time

            return True
        else:
            return False

    def _apply_melee_attack_effects(self, ability, attack_result_damage_rage_tuple, triggers_gcd, attack_type, hand,
                                    rage_cost=None, base_rage_cost=None, is_white_proc=False):
        super()._apply_melee_attack_effects(ability, attack_result_damage_rage_tuple, triggers_gcd, attack_type, hand,
                                            rage_cost, base_rage_cost, is_white_proc)

        attack_result, _, _ = attack_result_damage_rage_tuple
        if attack_result == AttackResult.CRIT:
            self.state['rampage_available_till'] = self.current_time_seconds + self.knowledge.RAMPAGE_AVAILABILITY_DURATION
            self._add_event(0.0, EventType.ATTACK_CRIT)

        if (
            PlayerBuffs.RAMPAGE in self.player.buffs
            and attack_result != AttackResult.MISS and attack_result != AttackResult.DODGE
            and random.random() < self.knowledge.RAMPAGE_PROC_CHANCE
        ):
            self.state['rampage_stacks'] = min(self.knowledge.RAMPAGE_MAX_STACKS, self.state['rampage_stacks'] + 1)

    def _handle_procs(self, ability, attack_result, hand):
        super()._handle_procs(ability, attack_result, hand)

        if attack_result != AttackResult.MISS and attack_result != AttackResult.DODGE:
            if Proc.DRAKEFIST_HAMMER_MAIN in self.player.procs or Proc.DRAKEFIST_HAMMER_OFF in self.player.procs:
                current_stats = self.calcs.current_stats()
                if Proc.DRAKEFIST_HAMMER_MAIN in self.player.procs:
                    if hand == Hand.MAIN and random.random() < (self.knowledge.DRAKEFIST_HAMMER_PPM * current_stats['speed_main_hand'] / 60):
                        self._add_event(0.0, EventType.DRAKEFIST_HAMMER_PROC)
                if Proc.DRAKEFIST_HAMMER_OFF in self.player.procs:
                    if hand == Hand.OFF and random.random() < (self.knowledge.DRAKEFIST_HAMMER_PPM * current_stats['speed_off_hand'] / 60):
                        self._add_event(0.0, EventType.DRAKEFIST_HAMMER_PROC)

            if Proc.BLACKOUT_TRUNCHEON_MAIN in self.player.procs or Proc.BLACKOUT_TRUNCHEON_OFF in self.player.procs:
                current_stats = self.calcs.current_stats()
                if Proc.BLACKOUT_TRUNCHEON_MAIN in self.player.procs:
                    if hand == Hand.MAIN and random.random() < (self.knowledge.BLACKOUT_TRUNCHEON_PPM * current_stats['speed_main_hand'] / 60):
                        self._add_event(0.0, EventType.BLACKOUT_TRUNCHEON_PROC)
                if Proc.BLACKOUT_TRUNCHEON_OFF in self.player.procs:
                    if hand == Hand.OFF and random.random() < (self.knowledge.BLACKOUT_TRUNCHEON_PPM * current_stats['speed_off_hand'] / 60):
                        self._add_event(0.0, EventType.BLACKOUT_TRUNCHEON_PROC)

            if Proc.EXECUTIONER_MAIN in self.player.procs or Proc.EXECUTIONER_OFF in self.player.procs:
                current_stats = self.calcs.current_stats()
                if Proc.EXECUTIONER_MAIN in self.player.procs:
                    if hand == Hand.MAIN and random.random() < (self.knowledge.EXECUTIONER_PPM * current_stats['speed_main_hand'] / 60):
                        self._add_event(0.0, EventType.EXECUTIONER_PROC)
                if Proc.EXECUTIONER_OFF in self.player.procs:
                    if hand == Hand.OFF and random.random() < (self.knowledge.EXECUTIONER_PPM * current_stats['speed_off_hand'] / 60):
                        self._add_event(0.0, EventType.EXECUTIONER_PROC)

            if Proc.MONGOOSE_MAIN in self.player.procs or Proc.MONGOOSE_OFF in self.player.procs:
                current_stats = self.calcs.current_stats()
                if Proc.MONGOOSE_MAIN in self.player.procs:
                    if hand == Hand.MAIN and random.random() < (self.knowledge.MONGOOSE_PPM * current_stats['speed_main_hand'] / 60):
                        self._add_event(0.0, EventType.MONGOOSE_MAIN_PROC)
                if Proc.MONGOOSE_OFF in self.player.procs:
                    if hand == Hand.OFF and random.random() < (self.knowledge.MONGOOSE_PPM * current_stats['speed_off_hand'] / 60):
                        self._add_event(0.0, EventType.MONGOOSE_OFF_PROC)

        if attack_result == AttackResult.CRIT:
            if Proc.HOURGLASS_OF_THE_UNRAVELLER in self.player.procs:
                if not self.state['hourglass_of_the_unraveller_on_icd'] and random.random() < self.knowledge.HOURGLASS_OF_THE_UNRAVELLER_PROC_CHANCE:
                    self._add_event(0.0, EventType.HOURGLASS_OF_THE_UNRAVELLER_PROC)
