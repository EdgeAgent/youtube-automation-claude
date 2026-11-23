# The Packaging Playbook

*The strategy this repo's code enforces, written out in full.
Inspired by the Decoded Genius / Jake Bryant packaging system and by
outlier research across top clip channels, rewritten here in original
wording for any niche.*

---

## 1. Videos fail on packaging, not on quality

The title, the thumbnail, and the first seconds decide whether the
rest of the video exists at all. A great moment with a flat title is
invisible; a mediocre moment with perfect packaging still
underperforms a great one — so the order of work is fixed:

**Title first. Thumbnail frame second. Video third.**

If you cannot write a clickable title for a moment, the moment is
wrong. Go find a better moment instead of polishing a weak one.

## 2. The metrics that actually matter

Forget raw view counts and don't worship CTR. The three numbers that
tell you the truth:

- **APV — average percentage viewed.** How much of the video people
  watch. For Shorts this is close to the whole game.
- **AVD — average view duration.** The long-form compounding metric;
  it's why compilations and countdowns outperform single scenes.
- **Impressions.** How often YouTube chose to show your packaging at
  all. Packaging earns impressions; retention earns more of them.

A video people click and abandon in five seconds is worse than a
slower-clicked video people finish. Optimize for finishing.

## 3. Outlier theory

Channels don't grow evenly — they grow in jumps, from individual
videos that massively outperform the channel's own average. Your job
is not "make more videos." Your job is:

1. Find your outliers (yours, and your niche's top channels').
2. Name the repeatable pattern in one sentence.
3. Make more of THAT — not more of everything.

Weekly habit: pull your top video by APV, write its pattern in one
line, and source the next batch from that line.

## 4. Upload less, package harder

Every upload is a bet. Channels that grow make fewer, bigger bets:
each video gets a real title, a real thumbnail, and a real hook —
or it doesn't go up. A slot stays empty rather than shipping a video
you already know is weak. Volume of *good bets* wins; volume of
uploads doesn't.

Long-form is where duration compounds: ranked countdowns and numbered
series (best entry saved for last) are the proven shapes. Shorts are
the funnel that feeds them, not the product.

## 5. Moment selection — the four winners

Across clip niches, almost every outlier is one of four moment types:

- **FAIL** — the plan goes wrong: crashes, botched escapes, chaos.
- **FUNNY** — absurd behaviour, glitches, unexpected outcomes.
- **REACTION** — a genuine high-energy human response.
- **SECRET WITH STEPS** — a hidden thing, shown with the exact steps
  to find or trigger it. The steps in the description are the search
  value.

And the dead categories, which produce essentially zero outliers no
matter how they're packaged: menus and settings screens, shopping,
inventory/loadout, travel between the action, story beats with no
payoff moment. Reject them on sight. Your niche will have its own
names for the winners and the dead — that's what the niche config is
for — but every niche has both lists.

**The self-score** (the pipeline's `select.py`): five questions, 0–2
each — winning type? hook in frame one? title curious without
spoiling? would a stranger finish? better than your average? Ship
only at 8+. Below that, rebuild or drop, and say which.

## 6. Title craft

- Front-load the most intriguing element; withhold the resolution.
- Rhythm matters — read it aloud. Short and punchy beats complete.
- Never give away the ending. The click is bought with the question,
  not the answer.
- Numbered/countdown promises ("Top 10…", "#3 in…") are the proven
  long-form shape, with the strongest entry named in the title.
- For Shorts: say what happens, add at most one emoji, and use the
  words your niche actually searches ("funny", "fails", "takedown",
  "secret") when the moment honestly is one.

## 7. Thumbnails

- The base is the **rawest real frame** from the video itself — the
  moment of peak tension. Not a designed graphic, not AI key art,
  not stock. The frame is a promise; the video must keep it.
- Treatment is grade + type: saturated, high-contrast grade; 2–4
  words of bold display text with a heavy outline; text inside a
  safe margin on every edge; nothing important covered.
- The text is NOT the title repeated. It's the sharpest true beat of
  the story, the thing the title couldn't say.
- Legibility test: shrink it to ~320px wide. If you can't read it
  instantly, it fails.

## 8. Descriptions and tags

Description order is fixed: **hook line** (never the title repeated) →
**subscribe line** → body → **exact steps** for secret/how-to videos →
**source credit** → **disclaimer** → hashtags.

Tags: video-specific first (4–6, the search intent of THIS video),
then the niche's canonical set, filled to ~490–500 characters of
YouTube's 500 limit, trimming generics from the end only. Specific
tags are never sacrificed to make room for generic ones.

## 9. The standing rules

1. No video gets made before its title and thumbnail frame exist.
2. Weekly: top video by APV → one-line pattern → next batch sourced
   from that line.
3. Titles never give away the ending.
4. A slot stays empty rather than shipping a QC-failed video.
5. Compilations and longs are the AVD plays; Shorts feed them.
6. Every upload is verified by read-back after saving — never trust
   the upload screen.

## 10. Production — the pipeline makes the video

Selection decides what deserves to exist; production is where it
gets made. The rules are mechanical on purpose:

- **Cut at the winner's timestamps, frame-accurately.** A clip that
  starts two seconds late has already lost its hook.
- **Shorts are vertical 9:16.** Blur-pad keeps the whole frame —
  the source scaled to fit over a blurred zoom of itself. Crop only
  when the subject is big and centred enough to survive it.
- **Captions are burned in**, timed to the clip. Most Shorts are
  watched on mute first; the caption is the hook's second chance.
- **Compilations run countdown order: weakest winner first, best
  clip last.** The ending is what gets remembered and shared.
- **Audio stays honest.** Keep the source audio, or normalise it
  toward -14 LUFS — never bury the moment under music it didn't
  have.
- **Footage is supplied, never taken.** Production works on files
  the user owns or has rights to, sourced the way their niche
  preset describes. Nothing is downloaded or scraped, ever.
