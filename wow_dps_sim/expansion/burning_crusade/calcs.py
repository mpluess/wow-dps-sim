import random

from wow_dps_sim.enums import Hand, PlayerBuffs
import wow_dps_sim.expansion.calcs


class Calcs(wow_dps_sim.expansion.calcs.Calcs):
    def _apply_temporary_buffs_flat(self, stats):
        stats = super()._apply_temporary_buffs_flat(stats)

        if PlayerBuffs.RAMPAGE in self.player.buffs:
            stats['ap'] += self.knowledge.RAMPAGE_ADDITIONAL_AP_PER_STACK * self.sim_state['rampage_stacks']

        return stats

    def _unbridled_wrath(self, hand):
        current_stats = self.current_stats()
        speed_key = 'speed_off_hand' if hand == Hand.OFF else 'speed_main_hand'
        procced = random.random() < (self.knowledge.UNBRIDLED_WRATH_PPM * current_stats[speed_key] / 60)
        return 1 if procced else 0
