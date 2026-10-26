# Hand-added foods

Each `.json` file here is a list of foods, in the same format as
`foods.json` (see the main README). Ids must start with `extra-` and be
unique; `n.kcal` is required and values are per 100 g (or 100 ml).

```json
[
  {
    "id": "extra-acai-bowl",
    "name": "Açaí bowl, with granola and banana",
    "cat": "Breakfast",
    "n": {"kcal": 120, "p": 2.1, "c": 21, "f": 3.2, "fi": 3, "s": 12,
          "m": {"c": 6, "k+": 210}},
    "p": [["1 bowl", 350]]
  }
]
```
