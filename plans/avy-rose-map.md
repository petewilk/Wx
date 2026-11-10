# Avalanche rose map (avy_map.html)

Paints the Utah Avalanche Center (UAC) danger rose onto a topographic map. Each spot's elevation and aspect pick the matching rose cell, and the spot is colored by that cell's danger rating. The first area is the Salt Lake zone. Other UAC zones and other states come later.

## Batches

Batch 2 settled the design on 2026-11-10. The live data source is parked until the user has read UAC's Data Access Policy (see **Open decisions**), so batches 3–7 build everything that doesn't need it, on hand-entered sample days in the same file format a future server job would write.

| # | Batch | Agents | Description | Status |
|---|-------|--------|-------------|--------|
| 1 | Prototype | implementer, qa-validator | Single-file page that paints a hardcoded archived rose (Salt Lake, 2025-02-11) on terrain computed in the browser. | Done (`8db65c6`) |
| 2 | Grill on open topics | web-fetch (facts), architect (data layout) | Settled every open topic except the live data source; rewrote batches 3 onward. | Done |
| 3 | UAC link and remembered settings | implementer, ux-reviewer | "Archived forecast on UAC ↗" under the date; All terrain as first-visit default; remember mode, basemap and opacity in localStorage. | Done |
| 4 | Forecast data files | implementer, qa-validator | Move `FORECAST` into `data/avy/uac/salt-lake/*.json` plus `index.json`, add sample days, load them with the agreed failure handling, extend deploy.sh to ship `data/avy/`. | Done |
| 5 | Date switcher | implementer, qa-validator, ux-reviewer | Prev/next + date input over the index, `?date=` in the URL, "No forecast" states, link follows the day. | Done |
| 6 | Pockets hatching, tile seams, zone fallback | implementer, qa-validator | Hatch odd rose values on map and rose; fetch neighbour tiles for seam-free edges; fall back to zone id 1738. | Not started |
| 7 | Review, docs and ship | ux-reviewer, qa-validator, doc-writer | Phone and dark-mode check, README section, in-page note, CONTEXT.md terms, then merge. Deploy unlinked only with the user's OK. | Not started |
| — | Live data pipeline | architect, implementer, qa-validator | UAC token + DreamHost cron job writing the same files for all 9 UAC zones. | Blocked: user reading UAC Data Access Policy |

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

Every batch's kickoff is `Run batch N of plans/avy-rose-map.md.` Follow **How to run a batch** above and the **Agreed design** below.

### Batch 3: UAC link and remembered settings (implementer, ux-reviewer)
- **Kickoff:** `Run batch 3 of plans/avy-rose-map.md.`
- Add "Archived forecast on UAC ↗" (was "Full forecast"; changed 2026-11-10) on its own line under the forecast date in the rose panel, `target="_blank" rel="noopener"`. Build the URL from zone slug and date with the archive pattern (see **UAC link**), not from `FORECAST.source`.
- First-visit defaults: All terrain mode, OSM + hillshade, 50% opacity. Save mode, basemap and opacity to localStorage on change and restore them on load. Wrap every localStorage read and write in try/catch; ignore unknown stored values.
- Check in the browser preview: link URL for 2025-02-11, settings survive a reload, a private window falls back to defaults.

### Batch 4: Forecast data files (implementer, qa-validator)
- **Kickoff:** `Run batch 4 of plans/avy-rose-map.md.`
- **Sample days:** the main session reads the rose PNGs from UAC's archive pages in the built-in browser (Cloudflare blocks curl and agents), checks each against that day's bottom line, and hands the 24 values to the implementer. Pick from the 2024/25 season: keep 2025-02-11, add a contrasting Low/Moderate day, a day with odd "pockets of" values, and leave at least one gap day inside the range with no file.
- Write the files in the format under **Forecast data files**, with `"sample": true`.
- Replace the inline `FORECAST` constant with the loader and failure handling under **Page loading**. Show "Sample data" in the panel when `sample` is true. Until batch 5, the page shows the newest day in the index.
- Extend deploy.sh as described under **Deploy**. Test with `./deploy.sh -n` on main only after merge; on this branch just review the diff.
- qa-validator: malformed rose, 404 day, failed index, file:// notice, stale response dropped.

### Batch 5: Date switcher (implementer, qa-validator, ux-reviewer)
- **Kickoff:** `Run batch 5 of plans/avy-rose-map.md.`
- Build the switcher under **Date switcher** on top of batch 4's index. Changing the day repaints from the terrain cache and updates the rose, readout, UAC link and URL.
- qa-validator: stepping skips gap days, the input picking a gap day shows "No forecast for this date", bad `?date=` falls back to newest, rapid switching shows the last pick.
- ux-reviewer: phone layout of the panel with the switcher.

### Batch 6: Pockets hatching, tile seams, zone fallback (implementer, qa-validator)
- **Kickoff:** `Run batch 6 of plans/avy-rose-map.md.`
- **Pockets:** draw odd values as the lower level's color with diagonal stripes of the next level up, both on the map overlay and in the rose wedge (an SVG pattern). The readout says "Pockets of Considerable". The batch 4 pockets sample day is the test case.
- **Tile seams:** compute slope and aspect at tile edges from the 8 neighbouring Terrarium tiles (cached like the others) instead of copied edge pixels. Missing neighbours fall back to the current copy.
- **Zone fallback:** find the Salt Lake polygon by name, then by id 1738.
- qa-validator: no seam line at tile edges on a synthetic slope across a tile boundary; hatch pattern scales with zoom without moiré.

### Batch 7: Review, docs and ship (ux-reviewer, qa-validator, doc-writer)
- **Kickoff:** `Run batch 7 of plans/avy-rose-map.md.`
- ux-reviewer on phone and dark mode; qa-validator full pass; doc-writer writes the README section (including serving over http, and the data layout), in-page note and CONTEXT.md terms.
- Merge to main with the user's OK. Deploy with `./deploy.sh` only with the user's OK; the page stays unlinked from the site.

### Live data pipeline (parked)
- **Kickoff:** `Run the live data pipeline batch of plans/avy-rose-map.md.` Only after the user has read the Data Access Policy and has a token.
- Settle first: cron job vs PHP proxy, where the token lives on DreamHost, the User-Agent string, and whether sample files are deleted or kept on the server.
- The job writes the files under **Forecast data files** for all 9 UAC zones, polling every 15 minutes from 5 to 8 AM Mountain time until that day's forecast is in.

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

## Agreed design, batch 2 (2026-11-10)

These came out of the batch 2 grilling. Don't change them without asking the user. Where they differ from the 2026-11-09 spec above, these win.

### Settings and defaults
- **Danger mode, basemap and opacity are remembered** per browser in localStorage. First visit: All terrain, OSM + hillshade, 50%. A saved 0% opacity restores as 50%, so the map never reopens with no visible overlay (user, 2026-11-10). The date is never remembered.

### UAC link
- **"Archived forecast on UAC ↗"** on its own line under the forecast date in the rose panel, opening in a new tab. The user changed it from "Full forecast" on 2026-11-10 so it doesn't read as today's forecast. Revisit the label once live data shows today's forecast.
- **Always the archive URL** `https://utahavalanchecenter.org/forecast/{slug}/{M}/{D}/{YYYY}` (no leading zeros), built from the zone slug and the selected date. Use `/forecast/{slug}` only if the archive URL turns out not to work for the current day.
- It doubles as UAC's attribution, and follows the date switcher.

### "Pockets of" ratings
- **Hatched:** the lower level's color with diagonal stripes of the next level up, on the map and in the rose. The readout says "Pockets of {level}". This replaces rounding down.

### Forecast data files
- **Static JSON in the repo**, laid out as a future server job would write it:
  - `data/avy/{center}/{zone}/{YYYY-MM-DD}.json`, e.g. `data/avy/uac/salt-lake/2025-02-11.json`. Lowercase UAC slugs. The date is UAC's forecast date in Mountain time.
  - `data/avy/{center}/{zone}/index.json`: `{ "schema": 1, "center": "uac", "zone": "salt-lake", "updated_at": "…Z", "dates": [ascending] }`. The newest day is the last entry. Gap days have no file and aren't listed.
- **Day file:**
  ```
  { "schema": 1, "center": "uac", "zone": "salt-lake", "zone_name": "Salt Lake",
    "date": "2025-02-11", "sample": true,
    "source": "hand-entered from archived rose PNG" | "uac-api",
    "source_url": "https://utahavalanchecenter.org/forecast/salt-lake/2/11/2025",
    "issued_at": null | "<ISO 8601>", "fetched_at": null | "<ISO 8601 Z>",
    "overall_danger_rose": [24 ints 0–10, UAC order, odd values kept],
    "problems": [] }
  ```
  `problems` is reserved for per-problem roses (`[{ "rank", "name", "rose": [24] }]`) and ignored by the page.
- **Sample days for now:** 2025-02-11 plus about 3 more from 2024/25, including a "pockets of" day and a gap day.
- **All 9 UAC zones** go into the data once a pipeline exists; the page shows Salt Lake only. A zone picker and other states come later.

### Page loading
- Fetch the index and day files with `{cache: 'no-cache'}`; no `?v=` cache-busting.
- `?date=` must match `^\d{4}-\d{2}-\d{2}$`, otherwise use the newest day.
- **Date not in the index:** "No forecast for this date", no overlay, no day fetch.
- **Index fetch fails:** a notice, prev/next disabled; if `?date=` was given, still try that day's file.
- **Listed day file 404s:** "Forecast file missing for {date}", no overlay.
- **Rose isn't 24 integers 0–10:** "Forecast data malformed", no overlay. Never fall back to another day's rose.
- **Fast switching:** tag each request and drop any response that isn't the latest.
- **file://:** show "Serve over http (see README)".
- **`sample: true`:** the panel shows "Sample data".

### Date switcher
- **Prev/next buttons** step through the days in the index only, plus a **native date input** with min/max from the first and last dates. Picking a day not in the index shows "No forecast for this date".
- **Range:** whatever the index lists, all seasons.
- **URL:** `?date=YYYY-MM-DD`, updated with `history.replaceState`; no parameter means the newest day.
- Changing the day repaints from the terrain cache. The rose panel, overlay, readout and UAC link follow it.

### Tile seams and zone lookup
- Fix seams by reading the 8 neighbouring Terrarium tiles. Find the zone by name, falling back to id 1738.

### Deploy
- deploy.sh also sends git-tracked `data/avy/**/*.json` with `rsync -tvzR` (paths kept, no `--delete`), day files first, then `index.json` files, then the existing JS and HTML. The data files join the uncommitted-changes warning. `petewilk.com/data/` doesn't exist on the server yet (checked 2026-11-10), so nothing clashes.
- **After batch 7, deploy unlinked** with the user's OK: reachable by URL, disclaimer kept, no link from the site until live data exists and the user says so.
- When a cron job goes live, deploy.sh and the job would overwrite each other's files. The job rebuilds `index.json` from its directory on every run, and the sample files are removed or deploy uses `--update`. Decide in the pipeline batch.

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

## Research findings (2026-11-10)

- **UAC API docs** (read in the built-in browser; Cloudflare blocks curl): `GET https://utahavalanchecenter.org/forecast/{region}/json` for logan, ogden, uintas, salt-lake, provo, skyline, moab, abajos, southwest. Today's forecast only; no past-date parameter is documented. Set a User-Agent with contact info or the request may get a 400. Poll every 15 minutes from 5 to 8 AM.
- **Rose values** confirmed: 0 no rating, odd = "pockets of" the next even level (1 pockets of Low … 9 pockets of Extreme). `danger_rose_1..3` (problem roses) only mark location; their values mean nothing since 2018/19.
- **Data Access Policy** is shown only inside the token request form, so it can't be read in advance without starting a request.
- **CORS:** the 401 response has no `Access-Control-Allow-Origin`. A tokened response is untested, so assume a server-side fetch is needed.
- **avalanche.org** `map-layer/UAC?day=YYYY-MM-DD` serves past dates with open CORS, but only one danger level per zone. UAC sends avalanche.org no rose, elevation bands or problems. No public archive of UAC roses exists, so history starts the day our own collection does.

## Open decisions

Only what the user put off on 2026-11-10.

1. **Live data source.** The user will read UAC's Data Access Policy (in the token request form) first. Leading option: a UAC token plus a DreamHost cron job that writes the files under **Forecast data files**. Also open: a PHP proxy instead, and what happens to the sample files.
2. **Per-problem roses:** later. The data format reserves `problems` for them.
3. **Zone picker and other states:** later. Data paths already include center and zone.
4. **Linking the page from the site:** after live data exists.

## Known limitations of the prototype

- **Blocky above zoom 15:** that's the terrain data's native limit.
- **Tile seams:** a faint 1-pixel line can show at tile edges, because the edge pixels are copied rather than read from neighbouring tiles. The fix is to fetch the 8 neighbouring tiles.
- **Band edges:** elevation is stored as Float32, so the exact band boundaries can be off by up to about 0.004 m. This can't happen with real Terrarium values.
- **Zone lookup:** the zone is found by the name "Salt Lake" only, with no fallback to id 1738. Fixed in batch 6, as are tile seams.

## Batch notes

- **Batch 1:**
  - The qa-validator passed all 8 math checks on synthetic test slopes: elevation decoding, slope and aspect, sector edges, band edges, how the rose is indexed, the slope ramp, the tile-to-pixel lookup, and the zone clip.
  - Browser checks covered all three basemaps, both modes, the slider and the hover readout.
  - After review, the 1° gap between rose wedges was fixed, the default basemap was changed to OSM + hillshade, the opacity slider was added, and Low was set to the same opacity as the other levels.
- **Batch 2:**
  - UAC's docs and api-access pages load in the built-in browser but not via curl or WebFetch (Cloudflare). Use the built-in browser to read archived rose PNGs in batch 4.
  - deploy.sh refuses to run off main, so sample data can't be deployed from this branch.
- **Batch 3:**
  - The rose link's href is set in `buildRose()` from `uacForecastUrl(FORECAST.slug, FORECAST.date)`. The attribution link uses the same helper. Batch 5 re-points both when the day changes. `FORECAST.url` is no longer used, and batch 4 can drop it.
  - Settings are stored under `avyMap.mode`, `avyMap.basemap` (`osmHill` | `topo` | `cyclo`) and `avyMap.opacity`. Invalid values fall back to the defaults.
  - Checked in the browser: link URL for 2025-02-11, settings survive a reload, invalid stored values fall back, a sandboxed frame with storage blocked renders with defaults, and the link fits the 150px phone panel.
  - After the ux-reviewer's review, the user had the link relabelled "Archived forecast on UAC ↗" (it wraps at phone width) and a saved 0% opacity restored as 50%.
- **Batch 4:**
  - Sample days in `data/avy/uac/salt-lake/`: 2024-12-24 (Low, upper W–N–E coded 3 = pockets of Moderate), 2025-01-30 (all Low), 2025-02-11 (as before), 2025-02-13 (Moderate, upper N/NE/E Considerable). 2025-02-12 is the gap day. Each was read from the archived rose PNG and checked against the bottom line.
  - The archive PNG draws "pockets of" cells in the plain next-level color, so odd values can only come from the bottom-line text. Only 2024-12-24 has them.
  - The upper-ring cells of the PNG can be sampled by pixel (centre 200,155 in the 400×440 image, radius 22), but the mid and low rings are drawn in 3D perspective, so read them by eye.
  - `loadDay(date)` and `setDay(day, date, msg)` are the entry points for batch 5. `loadDay` checks the loaded index, tags requests and drops stale ones, and treats a file whose `date` doesn't match as malformed. The page already honours a valid `?date=` (no switcher or `replaceState` yet).
  - `repaint()` clears tiles when there is no rose and reloads terrain for tiles evicted from the cache, so day changes never leave old colors.
  - Checked in the browser: newest day by default, gap day, bad `?date=`, 404, bad JSON, short, non-integer and out-of-range roses, mislabeled file, stale response, index missing with and without `?date=`. The qa-validator checked file://, repaint ordering and the data files by reading the code.
  - deploy.sh was reviewed but not run (it refuses off main). `./deploy.sh -n` on main after the merge is the first real check.
- **Batch 5:**
  - The switcher row (`#datePrev`, `#dateInput`, `#dateNext`) sits under the panel title. `syncSwitcher()` is the single sync point, called from `showDay()` and after the index load. `pickDate(date)` writes `?date=` via `setUrlDate()` and then calls `loadDay`. Prev/next go to the nearest index date strictly before or after the shown one, so they work from gap days.
  - `#roseDate` is now a status line ("Sample data" or the error message), since the input shows the date. It collapses when empty.
  - `initForecast` skips its default `loadDay` if the user picked a date while the index was still loading (found by the qa-validator).
  - After the ux-reviewer's review: the phone panel is 168px wide with 36px-tall controls, disabled buttons show a reason in `title`, and `color-scheme` is set on `:root`.
  - Checked in the browser (Chromium): default newest day, stepping across the 2025-02-12 gap, the gap day picked in the input, rapid prev clicks, `?date=bad&x=1#h` (becomes `?x=1#h`), a pick while the index loads, and the phone layout. Not checked on a real iOS Safari or Android device.
