# The World in One Day — Thursday 19 November 2026

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Astarya1104/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Astarya1104/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

An entry for [make.fun's news-image-20261119 bounty](https://make.fun/bounty/news-image-20261119):
sum up the world's news of Thursday 19 November 2026 in one image.

`main.py` is a pure-Python (standard library only) program that draws a
dense newspaper front page — 1024×1024 PNG — and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png`. It needs no network and no third-party
packages: the PNG is encoded by hand (zlib + struct) and all text is
rendered with a hand-written 5×7 bitmap font. Two runs write identical
bytes.

## What the page shows

- A dated masthead: **Thursday 19 November 2026**, with a deck naming the
  day's four biggest threads.
- A region strip counting all 41 stories: Europe 11, the Americas 10,
  Asia-Pacific 8, Middle East 6, Africa 3, Oceania 1, World 2.
- A six-number KPI strip ($81.3bn Anthropic IPO, 15.9m GTA VI pre-orders,
  200,000 evacuated ahead of Cyclone Akvan, $120bn COP31 finance,
  730,000 Rohingya, 13-year GTA wait).
- Three illustrated hero stories: the first Trump–Xi–Putin three-way
  summit in Shenzhen, GTA VI's global release day, and Anthropic's
  record IPO.
- Ten illustrated secondary stories, from the ICJ's Rohingya judgment
  and COP31's final 48 hours to the Crimean Bridge strike and the
  Benghazi drug seizure.
- A dotted world map with numbered markers for the lead stories, and
  28 numbered briefs covering the rest of the day.
- A **DATE CHECK** box: stories first reported on Wednesday 18 November
  (the House Democrats' 251–11 vote nominating Hakeem Jeffries, Voyager 1
  crossing one light-day, the EU's proposed EUR 45bn Ukraine loan, Pew's
  Islam projection, and others) are explicitly excluded from the page's
  news, so the image sums up Thursday alone.

Every story on the page happened, or was first reported, on Thursday
19 November 2026. Disputed claims are attributed, not stated as fact.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py
```

This writes `out/entry.png` (1024×1024, about 45 KB).

## License

MIT — see `LICENSE`.
