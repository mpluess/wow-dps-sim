from .enums import BossDebuffs


class Boss:
    def __init__(self, armor=4691, base_miss=0.086, base_dodge=0.056, debuffs=None):
        self.armor = armor
        self.base_miss = base_miss
        self.base_dodge = base_dodge
        self.debuffs = debuffs if debuffs is not None else {BossDebuffs.SUNDER_ARMOR_X5, BossDebuffs.FAERIE_FIRE, BossDebuffs.CURSE_OF_RECKLESSNESS}


class Config:
    def __init__(self, n_runs=1, logging=True, fight_duration_seconds_mu=180.0, fight_duration_seconds_sigma=20.0,
                 stat_increase_tuples=None):
        self.n_runs = n_runs
        self.logging = logging
        self.fight_duration_seconds_mu = fight_duration_seconds_mu
        self.fight_duration_seconds_sigma = fight_duration_seconds_sigma

        # [('hit', 1), ('crit', 1), ('agi', 20), ('ap', 30), ('str', 15), ('haste', 1), ('Sword', 1)]
        self.stat_increase_tuples = stat_increase_tuples if stat_increase_tuples is not None else []


class Event:
    def __init__(self, time_, count, event_type):
        self.time = time_
        self.count = count
        self.event_type = event_type

    def __lt__(self, other):
        # Comparing float equality here is not really optimal, but the actual game code probably does the same.
        # Best option would probably be to discretize time and use ints.
        if self.time != other.time:
            return self.time < other.time
        elif self.count != other.count:
            return self.count < other.count
        else:
            raise ValueError(f'__lt__: compared objects have the same time and count')

    def __repr__(self):
        return f'time={self.time}, count={self.count}, event_type={self.event_type}'


class WhiteHitEvent(Event):
    def __init__(self, time_, count, event_type):
        super().__init__(time_, count, event_type)

        self.has_flurry = False

    def __repr__(self):
        return super().__repr__() + f', has_flurry={self.has_flurry}'


class Player:
    def __init__(self, faction, race, class_, spec, items, partial_buffed_permanent_stats):
        self.faction = faction
        self.race = race
        self.class_ = class_
        self.spec = spec
        self.items = items
        self.partial_buffed_permanent_stats = partial_buffed_permanent_stats

        self.buffs = set()
