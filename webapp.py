from flask import Flask, jsonify, render_template, request

from stats import Stats

app = Flask(__name__)
stats = Stats()


@app.route('/', methods=['GET'])
def show_form():
    return render_template('character_planner.html')


@app.route('/', methods=['POST'])
def calc_stats():
    request_data = request.json
    print(request_data)

    race = request_data['race']
    class_ = request_data['class']
    spec = request_data[f"spec_{request_data['class']}"]
    merged_stats = stats.base_stats(race, class_)
    for stat_key, stat_value in stats.spec_stats(class_, spec).items():
        merged_stats[stat_key] += stat_value
    for stat_key, stat_value in stats.enchant_stats(class_, spec).items():
        merged_stats[stat_key] += stat_value
    item_ids = [form_value for form_key, form_value in request_data.items()
                if form_key.startswith('item_') and form_value != '']
    for stat_key, stat_value in stats.item_stats(item_ids).items():
        merged_stats[stat_key] += stat_value
    merged_stats = stats.apply_primary_stats_effects(race, class_, spec, merged_stats)
    merged_stats = stats.add_tertiary_stats(race, class_, spec, merged_stats)
    print(merged_stats)

    split_up_stats = {
        'base_stats': [
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
            ('Axes', merged_stats['axes']),
            ('Daggers', merged_stats['daggers']),
            ('Maces', merged_stats['maces']),
            ('Swords', merged_stats['swords']),
        ],
    }
    print(split_up_stats)

    return jsonify(split_up_stats)


@app.route('/stats', methods=['POST'])
def show_stats():
    return render_template('stats_stub.html', stats_label_value_tuples=request.json)
