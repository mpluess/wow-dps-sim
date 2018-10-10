from flask import Flask, jsonify, render_template, request

from scraper import Scraper
from sim.sim import do_sim
import stats

app = Flask(__name__)
scraper = Scraper()


@app.route('/', methods=['GET'])
def show_form():
    return render_template('vanilla_utils.html')


@app.route('/', methods=['POST'])
def calc_stats():
    request_data = request.json

    race = request_data['race']
    class_ = request_data['class']
    spec = request_data[f"spec_{request_data['class']}"]
    items = _scrape_items(request_data)
    unbuffed_stats = stats.calc_unbuffed_stats(race, class_, spec, items)

    # faction = request_data['faction']
    # buffed_stats = stats.finalize_buffed_stats(
    #     faction, race, class_, spec,
    #     stats.calc_partial_buffed_permanent_stats(faction, race, class_, spec, items)
    # )

    stats_to_display = {
        'base_stats': [
            ('Items', ', '.join([item['name'] for item in items])),
            ('Health', unbuffed_stats['health']),
            ('Armor', unbuffed_stats['armor']),
        ],
        'primary_stats': [
            ('Agility', unbuffed_stats['agi']),
            ('Intelligence', unbuffed_stats['int']),
            ('Spirit', unbuffed_stats['spi']),
            ('Stamina', unbuffed_stats['sta']),
            ('Strength', unbuffed_stats['str']),
        ],
        'secondary_stats': [
            ('Attack Power', unbuffed_stats['ap']),
            ('Crit', unbuffed_stats['crit']),
            ('Hit', unbuffed_stats['hit']),
            ('Haste', unbuffed_stats['haste']),
            ('Axes', unbuffed_stats['Axe']),
            ('Daggers', unbuffed_stats['Dagger']),
            ('Maces', unbuffed_stats['Mace']),
            ('Swords', unbuffed_stats['Sword']),
        ],
    }

    return jsonify(stats_to_display)


@app.route('/sim', methods=['POST'])
def sim():
    request_data = request.json
    faction = request_data['faction']
    race = request_data['race']
    class_ = request_data['class']
    spec = request_data[f"spec_{request_data['class']}"]
    items = _scrape_items(request_data)
    partial_buffed_permanent_stats = stats.calc_partial_buffed_permanent_stats(faction, race, class_, spec, items)

    avg_dps, stat_weights = do_sim(faction, race, class_, spec, items, partial_buffed_permanent_stats)
    print(f'Average DPS: {avg_dps}')
    print(f'Stat weights: {stat_weights}')


@app.route('/stats', methods=['POST'])
def show_stats():
    return render_template('stats_stub.html', stats_label_value_tuples=request.json)


def _scrape_items(request_data):
    item_slot_id_tuples = [(form_key.replace('item_', ''), form_value) for form_key, form_value in request_data.items()
                           if form_key.startswith('item_') and form_value != '']
    items = [scraper.scrape_item(item_slot, item_id) for item_slot, item_id in item_slot_id_tuples]

    return items
