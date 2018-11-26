import random

from wow_dps_sim.enums import AttackResult, AttackTableModification, AttackType, Hand, PlayerBuffs
import wow_dps_sim.expansion.calcs


class Calcs(wow_dps_sim.expansion.calcs.Calcs):
    def _apply_temporary_buffs_flat(self, stats):
        stats = super()._apply_temporary_buffs_flat(stats)

        if PlayerBuffs.RAMPAGE in self.player.buffs:
            stats['ap'] += self.knowledge.RAMPAGE_ADDITIONAL_AP_PER_STACK * self.sim_state['rampage_stacks']

        if PlayerBuffs.DRAKEFIST_HAMMER in self.player.buffs:
            stats['haste_rating'] += self.knowledge.DRAKEFIST_HAMMER_ADDITIONAL_HASTE_RATING

        return stats

    def _apply_attack_table_roll(self, damage, attack_result, hand, attack_type):
        if attack_result == AttackResult.MISS or attack_result == AttackResult.DODGE:
            return 0
        elif attack_result == AttackResult.GLANCING:
            return round(damage * 0.7)
        elif attack_result == AttackResult.CRIT:
            meta_socket_crit_damage_multiplier = self.knowledge.META_SOCKET_CRIT_DAMAGE_MULTIPLIER if self.player.meta_socket_active else 1.0
            # Impale only works on abilities, not auto attacks
            if attack_type == AttackType.WHITE:
                modifier = self.knowledge.CRIT_DAMAGE_MULTIPLIER * meta_socket_crit_damage_multiplier
            else:
                modifier = self.knowledge.CRIT_WITH_IMPALE_DAMAGE_MULTIPLIER * meta_socket_crit_damage_multiplier
            return round(damage * modifier)
        elif attack_result == AttackResult.HIT:
            return damage
        else:
            raise ValueError(attack_result)

    def _apply_boss_armor(self, damage):
        boss_armor = self._current_boss_armor()

        # http://web.archive.org/web/20130810120034/http://elitistjerks.com/f81/t22705-dps_compendium/
        damage_reduction = boss_armor / (boss_armor + 10557.5)

        return round(damage * (1 - damage_reduction))

    def _attack_table_roll(self, attack_type, hand, attack_table_modification):
        assert isinstance(attack_type, AttackType)
        assert isinstance(hand, Hand)
        current_stats = self.current_stats()
        minus_dodge_bonus = current_stats[('minus_dodge_bonus_off_hand' if hand == Hand.OFF else 'minus_dodge_bonus_main_hand')]

        miss_chance = max(
            0.0,
            (self.boss_config.BASE_MISS if (attack_type == AttackType.YELLOW or attack_type == AttackType.HEROIC_STRIKE) else self.boss_config.BASE_MISS + 0.19)
            - current_stats['hit']/100
        )
        dodge_chance = max(0.0, self.boss_config.BASE_DODGE - current_stats['minus_dodge']/100 - minus_dodge_bonus/100)
        glancing_chance = (0.0 if (attack_type == AttackType.YELLOW or attack_type == AttackType.HEROIC_STRIKE) else 0.25)
        crit_chance = max(0.0, current_stats['crit']/100)

        if attack_table_modification is None:
            pass
        elif attack_table_modification == AttackTableModification.OVERPOWER:
            dodge_chance = 0.0
            crit_chance += 0.5

        roll = random.random()
        if roll < miss_chance:
            attack_result = AttackResult.MISS
        elif roll < miss_chance + dodge_chance:
            attack_result = AttackResult.DODGE
        elif roll < miss_chance + dodge_chance + glancing_chance:
            attack_result = AttackResult.GLANCING
        elif roll < miss_chance + dodge_chance + glancing_chance + crit_chance:
            attack_result = AttackResult.CRIT
        else:
            attack_result = AttackResult.HIT

        return attack_result

    def _rage_from_damage(self, damage, hand, attack_result):
        def rage_generation_factor(hand, attack_result):
            if hand == Hand.MAIN:
                if attack_result == AttackResult.CRIT:
                    return 5.0
                else:
                    return 2.5
            elif hand == Hand.OFF:
                if attack_result == AttackResult.CRIT:
                    return 2.5
                else:
                    return 1.25

        current_stats = self.current_stats()
        weapon_speed = current_stats[('speed_off_hand' if hand == Hand.OFF else 'speed_main_hand')]

        return round((damage/274.7*7.5 + weapon_speed*rage_generation_factor(hand, attack_result)) / 2.0)

    def _unbridled_wrath(self, hand):
        current_stats = self.current_stats()
        speed_key = 'speed_off_hand' if hand == Hand.OFF else 'speed_main_hand'
        procced = random.random() < (self.knowledge.UNBRIDLED_WRATH_PPM * current_stats[speed_key] / 60)

        return 1 if procced else 0
