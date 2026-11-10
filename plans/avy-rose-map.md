# Avalanche rose map (avy_map.html)

Paints the Utah Avalanche Center (UAC) danger rose onto a topographic map. Each spot's elevation and aspect pick the matching rose cell, and the spot is colored by that cell's danger rating. The first area is the Salt Lake zone. Other UAC zones and other states come later.

## Batches

Batch 2 comes first in the next session: it grills the user on every open topic before any more code is written. The later batches are tentative, and batch 2 rewrites them from the user's answers.

| # | Batch | Agents | Description | Status |
|---|-------|--------|-------------|--------|
| 1 | Prototype | implementer, qa-validator | Single-file page that paints a hardcoded archived rose (Salt Lake, 2025-02-11) on terrain computed in the browser. | Done (`8db65c6`) |
| 2 | Grill on open topics | librarian / web-fetch (facts), architect (data pipeline) | Use the `grilling` skill to settle everything under **Open decisions** and the *open* items under **Planned features**. Agents look up facts while the user answers. Write the answers into this file and rewrite batches 3 onward. | Not started |
| 3 | UAC forecast link | implementer, ux-reviewer | Add "Full forecast on UAC ↗" to the rose panel for the hardcoded day. It doesn't depend on the data decision. | Not started |
| 4 | Live data pipeline | architect, implementer, qa-validator | Build whatever batch 2 chose, e.g. a server-side job that writes forecast JSON per day, and have the page load it in place of `FORECAST`. | Not started |
| 5 | Date switcher | implementer, qa-validator, ux-reviewer | Add the day picker on top of the batch 4 data, with the link following the selected day. | Not started |
| 6 | Other open items | per batch 2 | Per-problem roses, "pockets of" ratings, default mode, tile seams, and anything else batch 2 schedules. | Not started |
| 7 | Review, docs and ship | ux-reviewer, qa-validator, doc-writer | Check on phone and in dark mode, write the README section, the in-page note and CONTEXT.md terms, then merge. Deploying waits for the user's OK. | Not started |

Status values: `Not started` · `In progress` · `Done` · `Blocked: <reason>`.

## How to run a batch

1. Start a new session in `/Users/peterwilk/Documents/repos/Wx`, without a worktree, and paste the batch's **Kickoff** line.
2. The session checks out `feature/avy-rose-map`, reads this whole file, and sets the batch's row to `In progress`.
3. **Use the agents named in the batch row,** through the Agent tool:
   - `architect` designs structure before code is written.
   - `librarian` and `web-fetch` look up APIs and pages. Facts are never asked of the user.
   - `implementer` writes the code.
   - `qa-validator` checks the math and edge cases.
   - `ux-reviewer` reviews the layout and workflow.
   - `doc-writer` writes the docs.
   The session checks each agent's output before using it.
4. **Verify in the browser preview** with the `swe-dashboard` static server from `.claude/launch.json` (port 8765), at `/avy_map.html`. If another session's server already holds port 8765, use it.
5. **Finish the batch:** commit to `feature/avy-rose-map`, set the row to `Done`, and add anything later batches need to know under **Batch notes**. Don't push, merge or deploy without the user's OK.

## Batch details

### Batch 2: Grill on open topics (grilling skill, plus agents for facts)
- **Kickoff:** `Run batch 2 of plans/avy-rose-map.md.`
- **How it runs:**
  - Invoke the `grilling` skill.
  - Ask each question with the AskUserQuestion tool, with up to 4 questions per round and the recommended option first. Don't ask them as a numbered text list.
  - Work the frontier in rounds, as the skill describes.
- **Topics, in rough dependency order:**
  1. **Live data source** (open decision 1). Before asking, send `librarian` or `web-fetch` to read UAC's Data Access Policy if it's visible, and to check whether the tokened API serves past dates and what its CORS headers are. Then ask about the token, the server-side piece (DreamHost cron or a PHP proxy) and how often to poll. Once the user chooses, have `architect` sketch the pipeline: where JSON files live, the file naming, failure handling, and how the page finds the latest day.
  2. **Date switcher details:** the control style, the date range, whether the date goes in the URL, and whether to use a stand-in sample day before the pipeline exists. These depend on 1.
  3. **UAC link:** confirm its placement and text, and whether to always use the archive URL.
  4. **Per-problem roses** (open decision 2).
  5. **"Pockets of" rendering** (open decision 3).
  6. **Default mode** (open decision 4). The user leaned toward All terrain on 2026-11-09.
  7. **Other zones and states** (open decision 5): only whether they shape the data design now, or wait.
  8. **Deploy and site link** (open decision 6).
- **Done means:**
  - Every open item is answered and moved into **Agreed design**.
  - **Open decisions** holds only what the user explicitly put off.
  - Batches 3 onward are rewritten with agents and kickoff lines.
  - The user has confirmed the shared understanding, and the change is committed.

### Batches 3–7
- **Kickoff:** `Run batch N of plans/avy-rose-map.md.`
- Details are written by batch 2.

## Agreed design (spec)

These decisions came out of the design interview on 2026-11-09. Don't change them without asking the user.

### Page and stack
- **New standalone page** `avy_map.html`, single file with inline CSS and JS, like the other Wx apps.
- **Leaflet 1.9.4** from cdnjs. No build step, no API keys.
- Title "Avalanche Rose Map", with a visible disclaimer: prototype, archived forecast, not for travel decisions.
- **Initial view:** the Cottonwoods at [40.60, -111.65], zoom 12. Map zoom runs from 9 to 17.

### Forecast data
- **Overall danger rose only.** Per-problem roses (wind slab, persistent slab and so on) come later.
- **UAC encoding:**
  - 24 values. `[0..7]` is the upper band, `[8..15]` the mid band, `[16..23]` the low band.
  - Each band runs N, NE, E, SE, S, SW, W, NW, clockwise.
  - Values: 0 = no rating, 2 = Low, 4 = Moderate, 6 = Considerable, 8 = High, 10 = Extreme. Odd values mean "pockets of" the next level up.
- **Prototype data:** the `FORECAST` constant holds Salt Lake 2025-02-11, `[6,6,6,4,4,4,4,6, 6,6,6,4,2,2,4,6, 4,4,4,2,2,2,2,4]`. It was read from the archived rose PNG and checked against that day's bottom line. Keep it in one constant so a live source can replace it.
- **"Pockets of" values round down for now.** The sample day has none.

### Terrain
- **Computed in the browser** from AWS Terrarium tiles, `https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png`. They allow cross-origin use and go up to native zoom 15.
  - Elevation in metres = `R*256 + G + B/256 − 32768`.
  - Slope and aspect use a Horn kernel. Pixel size uses the latitude of each row.
  - Above zoom 15, Leaflet upscales the zoom-15 tiles.
- **Aspect** is the direction the slope faces downhill, in 8 slices of 45° centred on N, NE and so on. N runs from 337.5° to 22.5°.
- **Elevation bands, hard edges:** low below 8,000 ft (2,438.4 m), mid from 8,000 to 9,500 ft, upper above 9,500 ft (2,895.6 m).
- **Decoded terrain tiles are cached**, so changing the mode repaints without fetching again.

### Coloring
- **Standard North American danger colors:** Low #50B848, Moderate #FFF200, Considerable #F7941E, High #ED1C24, Extreme #231F20. No rating is transparent.
- **Every level paints at the same opacity**, Low included, so a Low rating doesn't read as green from the basemap. This was changed from the original plan of a fainter Low.
- **Danger opacity slider,** from 0% (hidden) to 100% (fully covers the basemap), in steps of 5%, default 50%. It sets the layer's opacity and works the same in both modes.
- **Two modes, with a toggle:**
  - **Slope-weighted** (the default): no color below 25°, rising in a straight line to full color at 35°.
  - **All terrain:** colors everything except slopes under 5°, where aspect means nothing.

### Extent
- **Clipped to the Salt Lake zone polygon,** with its outline drawn. The polygon is the feature named "Salt Lake" from `https://api.avalanche.org/v2/public/products/map-layer/UAC`.
- **If that fetch fails,** the overlay is unclipped and a notice shows.

### Rose panel
- **An SVG rose in a corner.** The inner ring is upper, the middle ring mid and the outer ring low, with N at the top. It shows the forecast date and a legend.
- **Hovering the map** highlights the matching rose cell and shows a readout, for example "NE · 8,940 ft · 34° · Considerable". On a phone, a tap does the same.
- **The readout also covers these cases:** outside the zone, flat ground, and slopes too shallow to be shaded in Slope-weighted mode.

### Basemaps
- **Switcher with three choices:**
  - **OSM Standard + hillshade** (the default). The hillshade is computed from the same Terrarium terrain and multiply-blended over the map.
  - **OpenTopoMap.**
  - **CyclOSM.**
- **Attribution** for each basemap, plus "Elevation: AWS Terrain Tiles (Mapzen)" and "Forecast: Utah Avalanche Center".

## Planned features

Added at the user's request on 2026-11-09. Details marked *open* are settled in batch 2.

### Date switcher
- **Purpose:** a control on the page that picks which day's rose is painted. The rose panel, the map overlay and the hover readout all follow the selected day.
- **Depends on batch 2.** The days it can offer depend on where the data comes from: a token API that serves past dates, a stored file per day written by a server-side job, or something else.
- **Default:** the newest forecast available. In the prototype that's the hardcoded 2025-02-11.
- **Changing the day repaints from the terrain cache,** like the mode toggle does, so no terrain is fetched again.
- **Days with no forecast** (early and late season, or a missing day) show a clear "No forecast for this date" message and no overlay, not a stale rose.
- *Open:*
  - **Control style:** previous/next day buttons plus a date input, or a calendar.
  - **Date range:** the current season only, or every season the data source has.
  - **Saving the day in the URL:** e.g. `?date=2025-02-11`, so a view can be shared or bookmarked.
  - **Prototype stand-in:** whether to hardcode a second sample day so the switcher can be built before batch 2.

### Link to the UAC forecast
- **What it is:** a link in the rose panel, next to the forecast date, to that day's full forecast on the UAC site. It opens in a new tab.
- **URL:**
  - Today's forecast is `https://utahavalanchecenter.org/forecast/salt-lake`.
  - Past days are `https://utahavalanchecenter.org/forecast/salt-lake/{M}/{D}/{YYYY}`, with no leading zeros, e.g. `/forecast/salt-lake/2/11/2025`.
  - The archive pattern also works for today, so always using it keeps the link simple. Use `/forecast/salt-lake` only if the archive URL turns out not to work for the current day.
- **The link follows the date switcher,** and the zone slug when more zones are added.
- **The link text names the source,** e.g. "Full forecast on UAC ↗". This is also UAC's attribution.
- **The prototype's `FORECAST.source` already holds this link for 2025-02-11.** It isn't shown in the panel yet.

## Research findings (2026-11-09)

- **UAC rose JSON:**
  - `https://utahavalanchecenter.org/forecast/salt-lake/json` has `overall_danger_rose`, but it needs an API token.
  - The token is requested at https://utahavalanchecenter.org/api-access. It lasts 12 months, and you must accept UAC's Data Access Policy, which we haven't seen.
  - Docs are at https://utahavalanchecenter.org/docs/api/forecast. They ask for a User-Agent with contact info, and suggest polling every 15 minutes between 5 and 8 AM.
  - Without a token it returns 401 with no CORS header. We haven't checked whether it serves past dates, or what CORS headers a tokened request gets.
- **avalanche.org public API** (`api.avalanche.org/v2/public/products?avalanche_center_id=UAC`): open, with CORS allowed, but UAC products give only the single overall rating, with no rose.
- **Archive:**
  - Old forecasts are at `https://utahavalanchecenter.org/forecast/salt-lake/{M}/{D}/{YYYY}`.
  - Cloudflare blocks non-browser clients.
  - The rose on those pages is a PNG, for example the 2025-02-11 one at `sites/default/files/forecast/202502/20250212-005607-14.png`.
- **Zone polygon:** the avalanche.org map-layer endpoint above, with CORS allowed. Salt Lake is feature id 1738.

## Open decisions

1. **Live data source** (batch 2). The token can't be put in the page's public JS, so a live feed needs something on the server side. Options:
   - Request a UAC token, then use a DreamHost cron job or a PHP proxy that writes a static JSON file.
   - Read the colors from the daily rose PNG. This is fragile, Cloudflare blocks it, and it likely goes around UAC's policy.
   - Something else.
   - The user chose to decide this after the prototype.
   - This choice also decides which days the date switcher can offer, so check that the chosen source covers past dates.
2. **Per-problem roses:** add a switcher to paint any of the day's problem roses.
3. **"Pockets of" ratings:** how to draw odd values, for example a lighter shade or hatching.
4. **Default mode:** the user currently prefers All terrain, because Low is hard to see in Slope-weighted. Make All terrain the default?
5. **Other zones and states:** zone picker, a band table per zone, and other avalanche centers.
6. **Deploy:** the page isn't linked from the site or deployed yet.

## Known limitations of the prototype

- **Blocky above zoom 15:** that's the terrain data's native limit.
- **Tile seams:** a faint 1-pixel line can show at tile edges, because the edge pixels are copied rather than read from neighbouring tiles. The fix is to fetch the 8 neighbouring tiles.
- **Band edges:** elevation is stored as Float32, so the exact band boundaries can be off by up to about 0.004 m. This can't happen with real Terrarium values.
- **Zone lookup:** the zone is found by the name "Salt Lake" only, with no fallback to id 1738.

## Batch notes

- **Batch 1:**
  - The qa-validator passed all 8 math checks on synthetic test slopes: elevation decoding, slope and aspect, sector edges, band edges, how the rose is indexed, the slope ramp, the tile-to-pixel lookup, and the zone clip.
  - Browser checks covered all three basemaps, both modes, the slider and the hover readout.
  - After review, the 1° gap between rose wedges was fixed, the default basemap was changed to OSM + hillshade, the opacity slider was added, and Low was set to the same opacity as the other levels.
