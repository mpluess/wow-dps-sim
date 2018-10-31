from flask import Flask, render_template, request

from scraper import Scraper
from sim.entities import Boss, Config
from sim.sim import do_sim
import stats

app = Flask(__name__)

# Northdale (Light's Hope) database
scraper = Scraper('https://vanillawowdb.com/?item=', path_to_cache='cache/items/vanillawowdb.com')

# 1.12 database
# scraper = Scraper('https://classicdb.ch/?item=', path_to_cache='cache/items/classicdb.ch')


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
    unbuffed_base_stats = [
        ('Items', ', '.join([item['name'] for item in items])),
        ('Health', unbuffed_stats['health']),
        ('Armor', unbuffed_stats['armor']),
    ]
    unbuffed_primary_stats = [
        ('Agility', unbuffed_stats['agi']),
        ('Intelligence', unbuffed_stats['int']),
        ('Spirit', unbuffed_stats['spi']),
        ('Stamina', unbuffed_stats['sta']),
        ('Strength', unbuffed_stats['str']),
    ]
    unbuffed_secondary_stats = [
        ('Attack Power', unbuffed_stats['ap']),
        ('Crit', unbuffed_stats['crit']),
        ('Hit', unbuffed_stats['hit']),
        ('Haste', unbuffed_stats['haste']),
        ('Axes', unbuffed_stats['Axe']),
        ('Daggers', unbuffed_stats['Dagger']),
        ('Maces', unbuffed_stats['Mace']),
        ('Swords', unbuffed_stats['Sword']),
    ]

    faction = request_data['faction']
    buffed_stats = stats.calc_partial_buffed_permanent_stats(faction, race, class_, spec, items)
    buffed_stats = stats.apply_berserker_stance_effects(buffed_stats)
    buffed_stats = stats.finalize_buffed_stats(faction, race, class_, spec, buffed_stats)

    return render_template(
        'stats.html',
        unbuffed_base_stats=unbuffed_base_stats,
        unbuffed_primary_stats=unbuffed_primary_stats,
        unbuffed_secondary_stats=unbuffed_secondary_stats,
        buffed_stats=str(buffed_stats),
    )


@app.route('/sim', methods=['POST'])
def sim():
    request_data = request.json
    faction = request_data['faction']
    race = request_data['race']
    class_ = request_data['class']
    spec = request_data[f"spec_{request_data['class']}"]
    items = _scrape_items(request_data)
    partial_buffed_permanent_stats = stats.calc_partial_buffed_permanent_stats(faction, race, class_, spec, items)

    # print(items)
    # print(partial_buffed_permanent_stats)

    result, stat_weights = do_sim(faction, race, class_, spec, items, partial_buffed_permanent_stats, boss=Boss(), config=Config())

    return f'{result}\nStat weights: {stat_weights}\n'


def _scrape_items(request_data):
    item_slot_id_tuples = [(form_key.replace('item_', ''), form_value) for form_key, form_value in request_data.items()
                           if form_key.startswith('item_') and form_value != '']
    items = [scraper.scrape_item(item_slot, item_id) for item_slot, item_id in item_slot_id_tuples]

    return items
