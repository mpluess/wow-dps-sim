import copy
import random

from wow_dps_sim.enums import AttackResult, AttackTableModification, AttackType, BossDebuffs, Hand, PlayerBuffs, Stance
from wow_dps_sim.helpers import from_module_import_x
from wow_dps_sim.stats import Stats


class Calcs:
    def __init__(self, expansion, player, sim_state):
        self.stats = Stats(expansion)

        expansion_module = 'wow_dps_sim.expansion.' + expansion
        self.boss_config = from_module_import_x(expansion_module, 'boss_config')
        self.knowledge = from_module_import_x(expansion_module, 'knowledge')
        self.ExpansionSpecificStats = from_module_import_x(expansion_module + '.stats', 'Stats')

        self.player = player

        self.sim_state = sim_state

    # TODO Not sure if this is correct for Vanilla
    # https://wowpedia.fandom.com/wiki/Haste
    # https://us.forums.blizzard.com/en/wow/t/haste-calculation-question/1159479
    # https://tbc.wowhead.com/item=32837/warglaive-of-azzinoth#comments
    def current_speed(self, hand):
        assert isinstance(hand, Hand)
        current_stats = self.current_stats()
        return (
            current_stats[('speed_off_hand' if hand == Hand.OFF else 'speed_main_hand')]
            / (
                (1 + current_stats['haste']/100)
                * current_stats['speed_multiplier']
            )
        )

    def current_stats(self, extra_flat_stats=None):
        if self.sim_state['execute_phase']:
            stats = self.player.partial_buffed_permanent_stats_execute
        else:
            stats = self.player.partial_buffed_permanent_stats
        if extra_flat_stats is not None:
            stats = self.stats.merge_stats(stats, extra_flat_stats)
        stats = self._apply_temporary_buffs_flat(stats)
        stats = self._apply_temporary_buffs_percentage(stats)
        stats = self.stats.finalize_buffed_stats(self.player.faction, self.player.race, self.player.class_, self.player.spec, stats)

        return stats

    def _apply_temporary_buffs_flat(self, stats):
        stats = copy.copy(stats)

        if self.player.stance == Stance.BERSERKER:
            stats = self.ExpansionSpecificStats.apply_berserker_stance_flat_effects(stats)
        if PlayerBuffs.RECKLESSNESS in self.player.buffs:
            stats['crit'] += self.knowledge.RECKLESSNESS_ADDITIONAL_CRIT

        if PlayerBuffs.CRUSADER_MAIN in self.player.buffs:
            stats['str'] += self.knowledge.CRUSADER_ADDITIONAL_STRENGTH
        if PlayerBuffs.CRUSADER_OFF in self.player.buffs:
            stats['str'] += self.knowledge.CRUSADER_ADDITIONAL_STRENGTH

        if PlayerBuffs.SLAYERS_CREST in self.player.buffs:
            stats['ap'] += self.knowledge.SLAYERS_CREST_ADDITIONAL_AP

        if PlayerBuffs.JUJU_FLURRY in self.player.buffs:
            stats['haste'] += self.knowledge.JUJU_FLURRY_ADDITIONAL_HASTE
        if PlayerBuffs.MIGHTY_RAGE_POTION in self.player.buffs:
            stats['str'] += self.knowledge.MIGHTY_RAGE_POTION_ADDITIONAL_STRENGTH

        return stats

    def _apply_temporary_buffs_percentage(self, stats):
        stats = copy.copy(stats)

        if self.player.stance == Stance.BERSERKER:
            stats = self.ExpansionSpecificStats.apply_berserker_stance_percentage_effects(stats)
        if PlayerBuffs.DEATH_WISH in self.player.buffs:
            stats['damage_multiplier'] *= self.knowledge.DEATH_WISH_DAMAGE_MULTIPLIER

        if PlayerBuffs.KISS_OF_THE_SPIDER in self.player.buffs:
            stats['speed_multiplier'] *= self.knowledge.KISS_OF_THE_SPIDER_SPEED_MULTIPLIER

        return stats

    def bloodthirst(self):
        current_stats = self.current_stats()
        base_damage = round(self.knowledge.BLOODTHIRST_AP_FACTOR * current_stats['ap'])

        return self._calc_attack_result_damage_rage(base_damage, AttackType.YELLOW, Hand.MAIN)

    def execute(self, rage):
        base_damage = self.knowledge.EXECUTE_BASE_DAMAGE + (rage - self.knowledge.EXECUTE_BASE_RAGE_COST)*self.knowledge.EXECUTE_DAMAGE_PER_RAGE

        return self._calc_attack_result_damage_rage(base_damage, AttackType.YELLOW, Hand.MAIN)

    def heroic_strike(self):
        current_stats = self.current_stats()
        base_damage = self._calc_weapon_damage(
            current_stats['damage_range_main_hand'],
            current_stats['speed_main_hand']
        )
        base_damage += self.knowledge.HEROIC_STRIKE_ADDITIONAL_DAMAGE

        return self._calc_attack_result_damage_rage(base_damage, AttackType.HEROIC_STRIKE, Hand.MAIN)

    def overpower(self):
        current_stats = self.current_stats()
        base_damage = self._calc_weapon_damage(
            current_stats['damage_range_main_hand'],
            self.knowledge.NORMALIZED_WEAPON_SPEED_LOOKUP[current_stats['weapon_type_main_hand']]
        )
        base_damage += self.knowledge.OVERPOWER_ADDITIONAL_DAMAGE

        return self._calc_attack_result_damage_rage(base_damage, AttackType.YELLOW, Hand.MAIN, AttackTableModification.OVERPOWER)

    def whirlwind(self, hand=Hand.MAIN):
        current_stats = self.current_stats()
        base_damage = self._calc_weapon_damage(
            current_stats[('damage_range_off_hand' if hand == Hand.OFF else 'damage_range_main_hand')],
            self.knowledge.NORMALIZED_WEAPON_SPEED_LOOKUP[
                current_stats[('weapon_type_off_hand' if hand == Hand.OFF else 'weapon_type_main_hand')]
            ]
        )

        return self._calc_attack_result_damage_rage(base_damage, AttackType.YELLOW, hand)

    def white_hit(self, hand, extra_flat_stats=None):
        assert isinstance(hand, Hand)
        current_stats = self.current_stats(extra_flat_stats)
        base_damage = self._calc_weapon_damage(
            current_stats[('damage_range_off_hand' if hand == Hand.OFF else 'damage_range_main_hand')],
            current_stats[('speed_off_hand' if hand == Hand.OFF else 'speed_main_hand')],
            current_stats=current_stats
        )

        return self._calc_attack_result_damage_rage(base_damage, AttackType.WHITE, hand)

    def _calc_attack_result_damage_rage(self, base_damage, attack_type, hand, attack_table_modification=None):
        assert isinstance(hand, Hand)
        assert base_damage >= 0
        damage = base_damage

        attack_result = self._attack_table_roll(attack_type, hand, attack_table_modification)
        damage = self._apply_attack_table_roll(damage, attack_result, hand, attack_type)
        rage = 0
        if damage > 0:
            damage = self._apply_boss_armor(damage)

            if hand == Hand.OFF:
                damage = round(damage * self.knowledge.OFF_HAND_FACTOR)

            current_stats = self.current_stats()
            damage = round(damage * current_stats['damage_multiplier'])

            # https://blue.mmo-champion.com/topic/18325-the-new-rage-formula-by-kalgan/
            if attack_type == AttackType.WHITE:
                rage += self._rage_from_damage(damage, hand, attack_result)

            if attack_type == AttackType.WHITE or attack_type == AttackType.HEROIC_STRIKE:
                rage += self._unbridled_wrath(hand)

        return attack_result, damage, rage

    def _apply_attack_table_roll(self, damage, attack_result, hand, attack_type):
        if attack_result == AttackResult.MISS or attack_result == AttackResult.DODGE:
            return 0
        elif attack_result == AttackResult.GLANCING:
            current_stats = self.current_stats()
            weapon_skill_bonus = current_stats[('weapon_skill_bonus_off_hand' if hand == Hand.OFF else 'weapon_skill_bonus_main_hand')]
            glancing_factor = 0.7 + min(10, weapon_skill_bonus) * 0.03
            return round(damage * glancing_factor)
        elif attack_result == AttackResult.CRIT:
            # Impale only works on abilities, not auto attacks
            if attack_type == AttackType.WHITE:
                modifier = self.knowledge.CRIT_DAMAGE_MULTIPLIER
            else:
                modifier = self.knowledge.CRIT_WITH_IMPALE_DAMAGE_MULTIPLIER
            return round(damage * modifier)
        elif attack_result == AttackResult.HIT:
            return damage
        else:
            raise ValueError(attack_result)

    def _apply_boss_armor(self, damage):
        boss_armor = self._current_boss_armor()

        # See http://wowwiki.wikia.com/wiki/Armor
        damage_reduction = boss_armor / (boss_armor + 5882.5)

        return round(damage * (1 - damage_reduction))

    def _current_boss_armor(self):
        return max(
            0,

            self.boss_config.ARMOR
            - (1 if BossDebuffs.SUNDER_ARMOR_X5 in self.boss_config.DEBUFFS else 0) * self.knowledge.SUNDER_ARMOR_REDUCTION_PER_STACK * 5
            - (1 if BossDebuffs.FAERIE_FIRE in self.boss_config.DEBUFFS else 0) * self.knowledge.FAERIE_FIRE_ARMOR_REDUCTION
            - (1 if BossDebuffs.CURSE_OF_RECKLESSNESS in self.boss_config.DEBUFFS else 0) * self.knowledge.CURSE_OF_RECKLESSNESS_ARMOR_REDUCTION
            - self.current_stats()['arp']
        )

    def _attack_table_roll(self, attack_type, hand, attack_table_modification):
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
            (self.boss_config.BASE_MISS if (attack_type == AttackType.YELLOW or attack_type == AttackType.HEROIC_STRIKE) else self.boss_config.BASE_MISS + 0.19)
            - current_stats['hit'] / 100
            - weapon_skill_bonus * 0.0004
        )
        dodge_chance = max(0.0, self.boss_config.BASE_DODGE - weapon_skill_bonus * 0.0004)
        glancing_chance = (0.0 if (attack_type == AttackType.YELLOW or attack_type == AttackType.HEROIC_STRIKE) else 0.4)
        crit_chance = max(0.0, current_stats['crit'] / 100 - (15 - weapon_skill_bonus) * 0.0004)

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
        return round(damage / 230.6 * 7.5)

    def _unbridled_wrath(self, hand):
        return 1 if random.random() < 0.4 else 0

    def _calc_weapon_damage(self, base_damage_range, speed, current_stats=None):
        base_weapon_min, base_weapon_max = base_damage_range
        base_weapon_damage = random.randint(base_weapon_min, base_weapon_max)

        if current_stats is None:
            current_stats = self.current_stats()
        weapon_damage = base_weapon_damage + round(current_stats['ap'] / 14 * speed)

        return weapon_damage
