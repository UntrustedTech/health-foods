"""Builds foods.json, the food database the Health app downloads.

Sources:
- USDA FoodData Central, SR Legacy and Foundation Foods (public domain,
  https://fdc.nal.usda.gov/download-datasets). Download the CSV zips,
  unzip them, and pass their folders.
- extra/*.json: foods added by hand (see extra/README.md).

  python3 build.py <sr_legacy_csv_dir> <foundation_csv_dir>

Each food: {"id", "name", "cat", "n": per 100 g, "p": [[portion, grams]]}.
"n" uses the app's keys: kcal, p (protein g), c (carbs g), f (fat g),
fi (fibre g), s (sugar g), sf (saturated fat g), na (sodium mg), and "m"
for vitamins and minerals (see MICROS for keys and units).
"""
import csv
import json
import pathlib
import re
import sys

csv.field_size_limit(10**9)
ROOT = pathlib.Path(__file__).resolve().parent

# FoodData Central nutrient ids → app key. Several ids give the same
# value; the first one present wins.
MACROS = {
    'kcal': ['1008', '2047', '2048'],
    'p': ['1003'],
    'c': ['1005', '1050'],
    'f': ['1004', '1085'],
    'fi': ['1079'],
    's': ['2000', '1063'],
    'sf': ['1258'],
    'na': ['1093'],
}
# key: (ids, unit) — units match the app's Micronutrient enum.
MICROS = {
    'a': (['1106'], 'µg'),   # vitamin A, RAE
    'c': (['1162'], 'mg'),   # vitamin C
    'd': (['1114'], 'µg'),   # vitamin D (D2 + D3)
    'e': (['1109'], 'mg'),   # vitamin E (alpha-tocopherol)
    'k': (['1185'], 'µg'),   # vitamin K (phylloquinone)
    'b1': (['1165'], 'mg'),  # thiamin
    'b2': (['1166'], 'mg'),  # riboflavin
    'b3': (['1167'], 'mg'),  # niacin
    'b6': (['1175'], 'mg'),
    'b9': (['1190', '1177'], 'µg'),  # folate, DFE (else total)
    'b12': (['1178'], 'µg'),
    'ca': (['1087'], 'mg'),  # calcium
    'fe': (['1089'], 'mg'),  # iron
    'mg': (['1090'], 'mg'),  # magnesium
    'k+': (['1092'], 'mg'),  # potassium
    'zn': (['1095'], 'mg'),  # zinc
}


def read(path):
    with open(path, newline='', encoding='utf-8') as f:
        yield from csv.DictReader(f)


def tidy(name):
    name = re.sub(r'\s+', ' ', name).strip()
    return name[:100]


def load(folder, kind):
    folder = pathlib.Path(folder)
    cats = {r['id']: r['description'] for r in read(folder / 'food_category.csv')}
    foods = {}
    for r in read(folder / 'food.csv'):
        if r['data_type'] != kind:
            continue
        foods[r['fdc_id']] = {
            'id': f'usda-{r["fdc_id"]}',
            'name': tidy(r['description']),
            'cat': cats.get(r['food_category_id'], ''),
            'raw': {},
            'p': [],
        }
    for r in read(folder / 'food_nutrient.csv'):
        food = foods.get(r['fdc_id'])
        if food is None or not r['amount']:
            continue
        try:
            food['raw'][r['nutrient_id']] = float(r['amount'])
        except ValueError:
            pass
    units = {r['id']: r['name'] for r in read(folder / 'measure_unit.csv')}
    for r in read(folder / 'food_portion.csv'):
        food = foods.get(r['fdc_id'])
        if food is None:
            continue
        try:
            grams = float(r['gram_weight'])
        except ValueError:
            continue
        if not 0 < grams < 5000:
            continue
        amount = r['amount'] or '1'
        unit = units.get(r['measure_unit_id'], '')
        unit = '' if unit in ('undetermined', '') else unit
        label = ' '.join(x for x in [
            amount.rstrip('0').rstrip('.') if '.' in amount else amount,
            unit, r['modifier'] or r['portion_description']] if x)
        label = re.sub(r'\s+', ' ', label).strip()[:60]
        if label and len(food['p']) < 6:
            food['p'].append([label, round(grams, 1)])
    return foods


def finish(food):
    raw = food.pop('raw')

    def pick(ids):
        for i in ids:
            if i in raw:
                return raw[i]
        return None

    n = {}
    for key, ids in MACROS.items():
        v = pick(ids)
        if v is not None and v > 0:
            n[key] = round(v, 2)
    if 'kcal' not in n:
        return None
    m = {}
    for key, (ids, _) in MICROS.items():
        v = pick(ids)
        if v is not None and v > 0:
            m[key] = round(v, 3)
    if m:
        n['m'] = m
    food['n'] = n
    if not food['p']:
        del food['p']
    return food


def extras():
    out = []
    for path in sorted((ROOT / 'extra').glob('*.json')):
        for food in json.loads(path.read_text(encoding='utf-8')):
            if not isinstance(food, dict) or 'kcal' not in food.get('n', {}):
                raise SystemExit(f'{path.name}: every food needs n.kcal')
            if not str(food.get('id', '')).startswith('extra-'):
                raise SystemExit(f'{path.name}: ids must start with "extra-"')
            out.append(food)
    return out


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    foods = {}
    for folder, kind in ((sys.argv[1], 'sr_legacy_food'),
                         (sys.argv[2], 'foundation_food')):
        foods.update(load(folder, kind))
    out = [f for f in (finish(f) for f in foods.values()) if f]
    out += extras()
    out.sort(key=lambda f: f['name'].lower())
    ids = [f['id'] for f in out]
    assert len(ids) == len(set(ids)), 'duplicate ids'
    data = {
        'format': 1,
        'source': 'USDA FoodData Central (SR Legacy, Foundation Foods); '
                  'Health contributors',
        'micros': {k: u for k, (_, u) in MICROS.items()},
        'foods': out,
    }
    (ROOT / 'foods.json').write_text(
        json.dumps(data, ensure_ascii=False, separators=(',', ':')),
        encoding='utf-8')
    print(f'{len(out)} foods')


if __name__ == '__main__':
    main()
