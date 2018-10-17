import copy
import random

from .enums import AttackResult, AttackType, BossDebuffs, Hand, PlayerBuffs
from stats import finalize_buffed_stats


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

    def execute(self, rage):
        base_damage = 600 + (rage - 10)*15

        return self._calc_attack_result_damage_rage(base_damage, AttackType.YELLOW, Hand.MAIN)

    def heroic_strike(self):
        current_stats = self.current_stats()
        base_damage = self._calc_weapon_damage(
            current_stats['damage_range_main_hand'],
            current_stats['speed_main_hand']
        )
        # Rank 8
        base_damage += 138

        return self._calc_attack_result_damage_rage(base_damage, AttackType.HEROIC_STRIKE, Hand.MAIN)

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
            if attack_result == AttackResult.MISS or attack_result == AttackResult.DODGE:
                return 0
            elif attack_result == AttackResult.GLANCING:
                current_stats = self.current_stats()
                weapon_skill_bonus = current_stats[('weapon_skill_bonus_off_hand' if hand == Hand.OFF else 'weapon_skill_bonus_main_hand')]
                glancing_factor = 0.7 + min(10, weapon_skill_bonus)*0.03
                return round(damage * glancing_factor)
            elif attack_result == AttackResult.CRIT:
                return round(damage * 2.2)
            elif attack_result == AttackResult.HIT:
                return damage
            else:
                raise ValueError(attack_result)

        def apply_boss_armor(damage):
            def current_boss_armor():
                # TODO further armor pen if available
                return max(
                    0,

                    self.boss.armor
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
            weapon_skill_bonus = current_stats[('weapon_skill_bonus_off_hand' if hand == Hand.OFF else 'weapon_skill_bonus_main_hand')]

            miss_chance = max(
                0.0,
                (self.boss.base_miss if (attack_type == AttackType.YELLOW or attack_type == AttackType.HEROIC_STRIKE) else self.boss.base_miss + 0.19)
                - current_stats['hit']/100
                - weapon_skill_bonus*0.0004
            )
            dodge_chance = max(0.0, self.boss.base_dodge - weapon_skill_bonus*0.0004)
            glancing_chance = (0.0 if (attack_type == AttackType.YELLOW or attack_type == AttackType.HEROIC_STRIKE) else 0.4)
            crit_chance = max(0.0, current_stats['crit']/100 - (15 - weapon_skill_bonus)*0.0004)

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
                damage = round(damage * 0.625)

            current_stats = self.current_stats()
            damage = round(damage * current_stats['damage_multiplier'])

            # https://forum.elysium-project.org/topic/22647-rage-explained-by-blizzard/
            # TODO not sure if I understood this correctly
            if attack_type == AttackType.WHITE:
                rage += round(damage / 230.6 * 7.5)

            if attack_type == AttackType.WHITE or attack_type == AttackType.HEROIC_STRIKE:
                rage += unbridled_wrath()

        return attack_result, damage, rage

    def _calc_weapon_damage(self, base_damage_range, speed):
        base_weapon_min, base_weapon_max = base_damage_range
        base_weapon_damage = random.randint(base_weapon_min, base_weapon_max)

        current_stats = self.current_stats()
        weapon_damage = base_weapon_damage + round(current_stats['ap'] / 14 * speed)

        return weapon_damage
