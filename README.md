# news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/christianfrancis162/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/christianfrancis162/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

One image summing up the world's news of Thursday 26 November 2026: 48
verified stories across 9 regions on a newspaper front page — a world map
with the regions marked, a UTC timeline of the day, 13 drawn scenes, a
Markets & Weather panel, a sports strip, a Quote of the Day box, and a
date check. The big stories: the US proposes new tariffs on 14 trading
partners; a fuel tanker fire kills 31 on a Cairo ring road; Russian
missiles hit a Kyiv shopping centre; judges in Netanyahu's corruption
trial doubt the bribery charge; Kim Jong Un vows a wider tactical nuclear
arsenal; the Macy's Thanksgiving Day Parade is postponed by a storm — the
first postponement in its 100-year history; India marks 18 years since
26/11; Gukesh–Sindarov Game 3 ends in a 60-move draw; tankers are hit
near the Strait of Hormuz as oil tops $96; and all three NFL Thanksgiving
games are decided in the final seconds — a first in NFL history.

`main.py` draws the whole front page itself with PIL and writes it to
the output directory as `entry.png` (JPEG, 1024x1024, under 1 MiB).
It is deterministic: two runs write identical bytes. Every story,
market value, temperature, score and quote is verified against a real
source for 26 November 2026; see `stories-v5.md` (in the workspace,
not the repo) for the 8 new stories and the new sections' sources.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/bounty/news-image-20261126)</sub>
