# Friday 20 November 2026 — the world in one image

A front page that sums up Friday 20 November 2026 in one picture:
35 stories from 7 regions, every one of them happened, or was first
reported, on that day.

## The day, in short

- **Kyiv:** Russia fired about 110 missiles and 400 drones at Ukraine
  overnight — one of the largest barrages of the war. Three bridges
  across the Dnipro in Kyiv were damaged; at least nine people were
  killed; debris also came down in Poland and NATO jets scrambled.
- **India:** Severe Cyclonic Storm Akvan crossed the coast near
  Gopalpur, Odisha, after more than 370,000 people were moved to
  shelters. No deaths were reported.
- **Markets:** An AI sell-off sank Asia's stock markets. Taiwan's index
  fell 6.2% to end its worst week since 1991; Seoul lost 5.2% and
  Tokyo 5.1%. Anthropic's record $81bn IPO could not stop the slide.
- **Europe:** Britain and the EU sealed a reset deal in Brussels —
  easier food trade, 100,000 youth visas a year, and linked carbon
  markets from 2028.
- **Climate:** COP31 in Antalya reached its last day with no deal; the
  draft text dropped the fossil-fuel phase-out and the $120bn
  adaptation finance target.

Plus 30 more stories on the page, numbered 4–35, with the source named
beside each one, and a world map showing where each of the 13 lead and
feature stories happened.

## Deliberately left out

The DATE CHECK box on the page names the big stories that were first
reported on Thursday 19 November and are therefore NOT shown as
Friday's news: the World Court's ruling on Myanmar, the three-leader
declaration in Shenzhen, Tonga's drought emergency, the migrant boat
lost off Senegal, BepiColombo's entry into orbit round Mercury, and
any final COP31 text.

## How it is made

`main.py` (Python 3.13, standard library only) draws the whole page
with the engine in `render.py` — an 8x8 bitmap font designed for this
entry, flat vector illustrations, and a palette-PNG writer built on
`struct` + `zlib`. No Pillow, no network, no clock: two runs write
byte-identical output.

Run it:

```
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

It writes `entry.png`, 1024x1024, under 1 MiB.

## Sources

Reuters, CNN, BBC, Al Jazeera, Anadolu, DW, Morningstar, Xinhua, PTI,
IMD, Deccan Herald, Kyiv Independent, Korea Herald, allAfrica, AP, ICC,
UKMTO, Autosport, Channels TV, Sky News, RTE — each named beside the
story it supports.
