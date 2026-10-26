# Health food database

The food list the [Health](https://github.com/UntrustedTech/health) app
searches, with calories, macros and **16 vitamins and minerals** per 100 g.
The app downloads `foods.json` from this repository and keeps a copy, so
search works offline. Barcodes and branded products still come from Open
Food Facts.

## What's in it

- **USDA FoodData Central**, SR Legacy and Foundation Foods: about 8,000
  everyday foods (fruit, vegetables, meat, dairy, grains, …). Public domain.
- **`extra/`**: foods added by hand. Anyone can add more (below).

## Format

```json
{
  "format": 1,
  "micros": {"a": "µg", "c": "mg", "...": "..."},
  "foods": [
    {
      "id": "usda-171705",
      "name": "Avocados, raw, all commercial varieties",
      "cat": "Fruits and Fruit Juices",
      "n": {"kcal": 160, "p": 2, "c": 8.53, "f": 14.66, "fi": 6.7,
            "s": 0.66, "sf": 2.13, "na": 7,
            "m": {"c": 10, "k": 21, "b9": 81, "k+": 485}},
      "p": [["1 cup, cubes", 150]]
    }
  ]
}
```

`n` is per **100 g** (100 ml for drinks): `kcal`, `p` protein g, `c`
carbs g, `f` fat g, `fi` fibre g, `s` sugar g, `sf` saturated fat g, `na`
sodium mg. `m` holds vitamins and minerals in the units listed under
`micros`:

| Key | Nutrient | Unit |
|---|---|---|
| `a` | Vitamin A (RAE) | µg |
| `c` | Vitamin C | mg |
| `d` | Vitamin D | µg |
| `e` | Vitamin E | mg |
| `k` | Vitamin K | µg |
| `b1` | Thiamin (B1) | mg |
| `b2` | Riboflavin (B2) | mg |
| `b3` | Niacin (B3) | mg |
| `b6` | Vitamin B6 | mg |
| `b9` | Folate (DFE) | µg |
| `b12` | Vitamin B12 | µg |
| `ca` | Calcium | mg |
| `fe` | Iron | mg |
| `mg` | Magnesium | mg |
| `k+` | Potassium | mg |
| `zn` | Zinc | mg |

`p` lists common portions as `[label, grams]`. Leave out anything you
don't know; missing values count as unknown, not zero.

## Adding foods

Add them to a JSON file in `extra/` (a list of foods in the format above,
ids starting with `extra-`), then rebuild:

```sh
python3 build.py <sr_legacy_csv_folder> <foundation_csv_folder>
```

The two folders are the unzipped CSV downloads from
<https://fdc.nal.usda.gov/download-datasets> ("SR Legacy" and
"Foundation Foods"). Commit `foods.json` with your change.

## License

The USDA data is in the public domain. Everything else here is released
under [CC0 1.0](LICENSE): use it for anything, no permission needed.
