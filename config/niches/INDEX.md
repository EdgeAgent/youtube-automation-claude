# The niche library

**28 built-in presets.** At setup you pick one, copy it into
`config/` under your own name, and tune it — or write a custom niche
from [`../niche.example.yaml`](../niche.example.yaml). Three presets
are also worked end-to-end in [`../examples/`](../examples/).

Every preset carries the fields the pipeline reads (winning/reject
types, ship bar, cadence, tag seeds, subscribe line) **plus** the
guidance that keeps a channel legal: title and thumbnail style,
**where source footage for that niche comes from**, how you feed it
into the pipeline, the rights note, and the niche's cautions.

> **The global sources rule, over every preset:** this toolkit never
> downloads, scrapes, or rips other people's videos. You supply
> footage you own or have the right to use — your recordings, your
> licensed material, public-records releases, community submissions
> with releases. Every preset's `sources` list stays inside that
> line; if a source isn't in your preset, the answer is to get the
> right, not to take the video.

| Niche | What wins there | Format lean | First source to look at |
|---|---|---|---|
| [animals / pets](animals-pets.yaml) | Rescues, reunions, and animals being unexpectedly brilliant. | shorts-first | Your own pets and your own filming |
| [bodycam / police footage](bodycam-police.yaml) | Chases, takedowns, and K9 tracks from publicly released bodycam footage. | both | Official police department YouTube/social channels that publish bodycam releases |
| [cars / automotive](cars-automotive.yaml) | Builds, saves, sound checks, and garage problem-solving. | both | Your own garage, your own cars, your own filming |
| [comedy / fails](comedy-fails.yaml) | Harmless fails, bloopers, and perfect-timing comedy. | shorts-first | Your own and your community's submitted clips (with a signed submission release) |
| [cooking / food](cooking-food.yaml) | Transformations, one-pan saves, and recipes with a twist. | shorts-first | Your own kitchen, your own cooking, your own filming |
| [courtroom moments](courtroom.yaml) | Judge moments, testimony turns, and verdict reactions from public proceedings. | both | Publicly streamed/recorded proceedings where recording and reuse are permitted |
| [dashcam moments](dashcam.yaml) | Close calls, instant karma, and lessons from the road. | shorts-first | Your own dashcam footage |
| [DIY / builds / maker](diy-builds.yaml) | Builds, restorations, and the step everyone gets wrong. | both | Your own workshop, your own projects, your own filming |
| [finance / business](finance-business.yaml) | Money lessons, business breakdowns, and market explainers. | both | Your own screen recordings, spreadsheets, and presentations |
| [fishing / outdoors](fishing-outdoors.yaml) | Catches, misses, and the spot logic behind them. | shorts-first | Your own trips, your own cameras (boat, bank, kayak) |
| [fitness / training](fitness-training.yaml) | Form fixes, transformations, and training mistakes corrected. | shorts-first | Your own training footage and your own clients (with written consent) |
| [gaming highlights](gaming-highlights.yaml) | Clutch plays, fails, and reactions from gameplay footage. | shorts-first | Your own gameplay captures (console/PC recording, OBS, capture card) |
| [history / stories](history-stories.yaml) | Forgotten events, primary sources, and the detail that changes the story. | long-form-first | Public-domain archives (libraries, national archives, expired-copyright material) |
| [interviews / talk](interviews-talk.yaml) | The answer nobody expected, from conversations you host or license. | both | Interviews you host and record yourself |
| [kids / family](kids-family.yaml) | Family moments, kid logic, and parenting wins (and fails). | shorts-first | Your own family's footage, filmed by you |
| [live stream moments](live-stream-moments.yaml) | The unscripted peak of a live broadcast — from streams you run or partner on. | shorts-first | Your own streams (your VODs, your channel) |
| [luxury / high-end lifestyle](luxury-lifestyle.yaml) | Craft, access, and the details that justify the price — or don't. | both | Items you own or were loaned, filmed by you |
| [movie / TV moments](movie-tv-moments.yaml) | Scene breakdowns, details you missed, and ending explainers. | both | Short clips used for commentary/criticism under your own narration and analysis |
| [music performances](music-performances.yaml) | Live moments, covers, and the note nobody expected. | shorts-first | Your own performances and your own recordings |
| [news explainers](news-explainers.yaml) | What happened, why it matters, in under a minute. | shorts-first | Your own narration and graphics built from primary sources (official statements, data, filings) |
| [podcast clips](podcast-clips.yaml) | The sharpest 60 seconds from long conversations. | shorts-first | Your own podcast's episode files |
| [real estate / property](real-estate.yaml) | Tours with a twist, price reveals, and renovation payoffs. | shorts-first | Properties you list, own, or were invited to film |
| [satisfying / process](satisfying-process.yaml) | Restorations, deep cleans, and processes shown end to end. | shorts-first | Your own workshop, jobs, and projects, filmed by you |
| [science / facts](science-facts.yaml) | Countdowns, myth-busting, and the fact that rewires your brain. | shorts-first | Your own narration, graphics, and demonstrations |
| [sports highlights](sports-highlights.yaml) | Impossible plays, buzzer beaters, and comebacks. | shorts-first | Your own recordings from events you filmed |
| [tech reviews / gadgets](tech-reviews.yaml) | Real tests, honest flaws, and comparisons that pick a winner. | both | Products you bought or were sent, filmed and tested by you |
| [travel / adventure](travel-adventure.yaml) | Hidden places, travel mistakes, and moments the brochure skipped. | both | Your own trips, your own filming |
| [true crime](true-crime.yaml) | Case timelines, interrogation moments, and solved-case breakdowns. | long-form-first | Court records and publicly released case documents |

Load one from Python:

```python
from pipeline.niches import list_niches, load_preset

for entry in list_niches():
    print(entry["slug"], "—", entry["summary"])

niche = load_preset("bodycam-police")   # a plain config dict
```
