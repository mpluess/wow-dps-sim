from collections import defaultdict
from flask import Flask, render_template, request

from wow_dps_sim.entities import Player
from wow_dps_sim.helpers import from_module_import_x
from wow_dps_sim.scraper import Scraper
from wow_dps_sim.sim import do_sim
from wow_dps_sim.stats import Stats

app = Flask(__name__)


@app.route('/', methods=['GET'])
def show_init():
    return render_template('init.html')


@app.route('/main', methods=['GET'])
def show_main():
    return render_template('main.html', **(request.args.to_dict()))


@app.route('/main/calc_stats', methods=['POST'])
def calc_stats():
    request_data = request.json

    race = request_data['race']
    class_ = request_data['class']
    spec = request_data[f"spec_{request_data['class']}"]

    expansion = request_data['expansion']
    scraper = Scraper(request_data['scraper_item_db'], expansion)
    items = _fetch_items(scraper, request_data)

    socket_stats, _ = _fetch_socket_stats(request_data)

    ExpansionSpecificStats = from_module_import_x('wow_dps_sim.expansion.' + expansion + '.stats', 'Stats')
    stats = Stats(expansion)
    unbuffed_stats = stats.calc_unbuffed_stats(race, class_, spec, items, socket_stats)
    unbuffed_base_stats, unbuffed_primary_stats, unbuffed_secondary_stats = ExpansionSpecificStats.get_displayable_stats(items, unbuffed_stats)

    faction = request_data['faction']
    buffed_stats = stats.calc_partial_buffed_permanent_stats(faction, race, class_, spec, items, socket_stats)
    buffed_stats = ExpansionSpecificStats.apply_berserker_stance_flat_effects(buffed_stats)
    buffed_stats = ExpansionSpecificStats.apply_berserker_stance_percentage_effects(buffed_stats)
    buffed_stats = stats.finalize_buffed_stats(faction, race, class_, spec, buffed_stats)
    buffed_base_stats, buffed_primary_stats, buffed_secondary_stats = ExpansionSpecificStats.get_displayable_stats(items, buffed_stats)

    return render_template(
        'stats.html',
        unbuffed_stats=str(unbuffed_stats),
        unbuffed_base_stats=unbuffed_base_stats,
        unbuffed_primary_stats=unbuffed_primary_stats,
        unbuffed_secondary_stats=unbuffed_secondary_stats,
        buffed_stats=str(buffed_stats),
        buffed_base_stats=buffed_base_stats,
        buffed_primary_stats=buffed_primary_stats,
        buffed_secondary_stats=buffed_secondary_stats,
    )


@app.route('/main/sim', methods=['POST'])
def sim():
    request_data = request.json
    faction = request_data['faction']
    race = request_data['race']
    class_ = request_data['class']
    spec = request_data[f"spec_{request_data['class']}"]

    expansion = request_data['expansion']
    scraper = Scraper(request_data['scraper_item_db'], expansion)
    items = _fetch_items(scraper, request_data)
    items_execute = _fetch_items(scraper, request_data, execute=True)

    socket_stats, meta_socket_active = _fetch_socket_stats(request_data)

    player = Player(
        faction, race, class_, spec, items, items_execute, meta_socket_active,
        expansion=expansion, socket_stats=socket_stats
    )
    result = do_sim(expansion, player)
    results = {'baseline': (result, 0)}
    for k, stats_added in [
        ('str', 20),
        ('crit_rating', 20),
        ('hit_rating', 20),
        ('haste_rating', 20),
        ('exp_rating', 20),
        ('arp', 120),
    ]:
        socket_stats_copy = socket_stats.copy()
        socket_stats_copy[k] += stats_added
        player = Player(
            faction, race, class_, spec, items, items_execute, meta_socket_active,
            expansion=expansion, socket_stats=socket_stats_copy
        )
        result = do_sim(expansion, player)
        results[k] = (result, stats_added)

    result_strings = []
    for k, (result, stats_added) in results.items():
        if k == 'baseline':
            result_string = f'{k}\n{str(result)}'
        else:
            result_string = f"{k}\nstat_weight={(result.dps - results['baseline'][0].dps) / stats_added:.3f} DPS\n{str(result)}"
        result_strings.append(result_string)
    results_string = '\n\n\n'.join(result_strings)
    return htmlize(results_string)


def _fetch_items(scraper, request_data, execute=False):
    if execute and request_data['use_execute_weapon_set']:
        item_slot_id_tuples = [
            (form_key.replace('item_', '').replace('execute_', ''), form_value)
            for form_key, form_value in request_data.items()
            if (
                (form_key.startswith('item_') or form_key.startswith('execute_'))
                and form_key not in {'item_main_hand', 'item_off_hand'}
                and form_value != ''
            )
        ]
        items = [scraper.scrape_item(item_slot, item_id) for item_slot, item_id in item_slot_id_tuples]
    else:
        item_slot_id_tuples = [(form_key.replace('item_', ''), form_value) for form_key, form_value in request_data.items()
                               if form_key.startswith('item_') and form_value != '']
        items = [scraper.scrape_item(item_slot, item_id) for item_slot, item_id in item_slot_id_tuples]

    return items


def _fetch_socket_stats(request_data):
    stats = defaultdict(int)
    meta_socket_active = False
    for form_key, form_value in request_data.items():
        if form_key.startswith('sockets_'):
            stats[form_key.replace('sockets_', '')] = int(form_value)
        elif form_key == 'meta_socket_active':
            assert isinstance(form_value, bool)
            meta_socket_active = form_value

    return stats, meta_socket_active


def htmlize(text: str):
    return text.replace('\n', '<br />\n')
