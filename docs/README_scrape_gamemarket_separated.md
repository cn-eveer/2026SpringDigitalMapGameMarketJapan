# Game Market Scraper — Separated Booth and Games Outputs

This scraper writes **booth-only** and **games-only** files directly.

## Run first 100

```bash
python scrape_gamemarket_booths.py \
  --input gamemarket_2026s_all_1318_booths_.csv \
  --start 1 \
  --limit 100 \
  --out-prefix gm2026s_batch_001 \
  --print-extracted
```

## Continue

```bash
python scrape_gamemarket_booths.py \
  --input gamemarket_2026s_all_1318_booths_.csv \
  --start 101 \
  --limit 100 \
  --out-prefix gm2026s_batch_101 \
  --print-extracted
```

## Run all booths

```bash
python scrape_gamemarket_booths.py \
  --input gamemarket_2026s_all_1318_booths_.csv \
  --start 1 \
  --limit 0 \
  --out-prefix gm2026s_all \
  --print-extracted
```

## Output files

For `--out-prefix gm2026s_all`, it creates:

- `gm2026s_all_booths_only.json`
- `gm2026s_all_games_only.json`
- `gm2026s_all_booths_only.csv`
- `gm2026s_all_games_only.csv`

## Optional nested / Markdown

```bash
python scrape_gamemarket_booths.py \
  --input gamemarket_2026s_all_1318_booths_.csv \
  --start 1 \
  --limit 0 \
  --out-prefix gm2026s_all \
  --write-nested \
  --write-markdown
```
