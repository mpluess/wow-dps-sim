from flask import Flask, jsonify, render_template, request

from scraper import Scraper
from sim import do_sim
import stats

app = Flask(__name__)
scraper = Scraper()


@app.route('/', methods=['GET'])
def show_form():
    return render_template('vanilla_utils.html')


@app.route('/', methods=['POST'])
def calc_stats():
    request_data = request.json
    print(request_data)

    race = request_data['race']
    class_ = request_data['class']
    spec = request_data[f"spec_{request_data['class']}"]
    items = _scrape_items(request_data)
    merged_stats = _calc_stats(race, class_, spec, items)
    print(merged_stats)

    stats_to_display = {
        'base_stats': [
            ('Items', ', '.join([item['name'] for item in items])),
            ('Health', merged_stats['health']),
            ('Armor', merged_stats['armor']),
        ],
        'primary_stats': [
            ('Agility', merged_stats['agi']),
            ('Intelligence', merged_stats['int']),
            ('Spirit', merged_stats['spi']),
            ('Stamina', merged_stats['sta']),
            ('Strength', merged_stats['str']),
        ],
        'secondary_stats': [
            ('Attack Power', merged_stats['ap']),
            ('Crit', merged_stats['crit']),
            ('Hit', merged_stats['hit']),
            ('Haste', merged_stats['haste']),
            ('Axes', merged_stats['axes']),
            ('Daggers', merged_stats['daggers']),
            ('Maces', merged_stats['maces']),
            ('Swords', merged_stats['swords']),
        ],
    }
    print(stats_to_display)

    return jsonify(stats_to_display)


@app.route('/sim', methods=['POST'])
def sim():
    request_data = request.json
    race = request_data['race']
    class_ = request_data['class']
    spec = request_data[f"spec_{request_data['class']}"]
    items = _scrape_items(request_data)
    merged_stats = _calc_stats(race, class_, spec, items)

    avg_dps, stat_weights = do_sim(merged_stats)


@app.route('/stats', methods=['POST'])
def show_stats():
    return render_template('stats_stub.html', stats_label_value_tuples=request.json)


def _scrape_items(request_data):
    item_slot_id_tuples = [(form_key.replace('item_', ''), form_value) for form_key, form_value in request_data.items()
                           if form_key.startswith('item_') and form_value != '']
    items = [scraper.scrape_item(item_slot, item_id) for item_slot, item_id in item_slot_id_tuples]

    return items


def _calc_stats(race, class_, spec, items):
    merged_stats = stats.base_stats(race, class_)
    for stat_key, stat_value in stats.spec_stats(class_, spec).items():
        if stat_key in merged_stats:
            merged_stats[stat_key] += stat_value
        else:
            merged_stats[stat_key] = stat_value
    for stat_key, stat_value in stats.enchant_stats(class_, spec).items():
        if stat_key in merged_stats:
            merged_stats[stat_key] += stat_value
        else:
            merged_stats[stat_key] = stat_value

    for stat_key, stat_value in stats.item_stats(items).items():
        if stat_key in merged_stats:
            merged_stats[stat_key] += stat_value
        else:
            merged_stats[stat_key] = stat_value
    merged_stats = stats.apply_primary_stats_effects(race, class_, spec, merged_stats)
    merged_stats = stats.add_tertiary_stats(race, class_, spec, merged_stats)

    return merged_stats
