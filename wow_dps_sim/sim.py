import random

from .entities import Player, Result
from .helpers import from_module_import_x
from . import sim_config


def do_sim(expansion, player):
    Sim = from_module_import_x('wow_dps_sim.expansion.' + expansion + '.sim', 'Sim')

    def do_n_runs(expansion, player):
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
        for run_nr in range(sim_config.N_RUNS):
            # Call copy constructor to start with a fresh state
            player = Player.from_player(player)
            fight_duration = sample_fight_duration(sim_config.FIGHT_DURATION_SECONDS_MU, sim_config.FIGHT_DURATION_SECONDS_SIGMA)
            with Sim(expansion, player, fight_duration, logging=sim_config.LOGGING, run_nr=run_nr) as sim:
                while sim.current_time_seconds < fight_duration:
                    event = sim.get_next_event()
                    sim.handle_event(event)
                dps = sim.damage_done / sim.current_time_seconds
                result = Result.from_ability_log(dps, sim.ability_log)
                result_list.append(result)
                sim.log('\n')
                sim.log(str(result))

        return Result.get_merged_result(result_list)

    result_baseline = do_n_runs(expansion, player)
    stat_weights = dict()
    # for stat, increase in config.STAT_INCREASE_TUPLES:
    #     stats_copy = copy.copy(partial_buffed_permanent_stats)
    #     stats_copy[stat] += increase
    #     result = do_n_runs(faction, race, class_, spec, items, stats_copy, boss, config)
    #     stat_weights[stat] = (result.dps - result_baseline.dps) / increase

    return result_baseline, stat_weights
