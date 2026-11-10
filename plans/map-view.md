# Map view for wx_dashboard.html

A third overview style (Graphic | Table | **Map**) that puts every visible place on a Leaflet map. Climb-tagged places get three Climbing Index pills (morning, midday, afternoon) in a sun-path arch around their rank number.

## Batches

Each batch runs in its own new Claude Code session. Batches run **in order**, because every one of them edits `wx_dashboard.html`. Running two at once would cause conflicts.

| # | Batch | Agents | Description | Status |
|---|-------|--------|-------------|--------|
| 1 | Design seams | architect | Decide the map module's state, functions and hooks into the existing render, ordering and ranking code. Write them into this file. | Done |
| 2 | Map shell | implementer | Add the Map option to View, load Leaflet, set up the full-height map and dark tiles, define when it fits, and show places as plain dots. | Done |
| 3 | Day picker and ranking | implementer, qa-validator | Add a day picker that shares the selected day with the other views, default to today, rank across tag groups on Map, and average the thirds over a span. | Done |
| 4 | Arch markers | implementer | Draw the sun-path pill arch, rank centers, numbered badges, loading and error states, and the overlap collapse. | Done |
| 5 | Popup and map adds | implementer | Add the popup with tag chips and Open forecast, Retry, and adding a place with right-click or long-press. A new place shows until it is tagged. | Done |
| 6 | Review and QA | ux-reviewer, qa-validator, implementer | Review usability, check edge cases on phone and in dark mode, and fix what they find. | Done |
| 7 | Docs and ship | doc-writer | Write the README and in-page notes, update CONTEXT.md, and merge to main. Deploying waits for your OK. | Not started |

Status values: `Not started` · `In progress` · `Done` · `Blocked: <reason>`.

## How to run a batch

1. Start a new session in `/Users/peterwilk/Documents/repos/Wx`, without a worktree, and paste the batch's **Kickoff** line.
2. The session checks out `feature/map-view`, which already holds this plan. It reads this whole file and sets its row to `In progress`.
3. It sends the work to the batch's agents through the Agent tool, checks their output, and verifies the result in the browser preview with the `swe-dashboard` static server from `.claude/launch.json`, which serves the whole folder on port 8765. Open `/wx_dashboard.html`.
4. It commits to `feature/map-view`, sets its row to `Done`, and adds anything later batches need to know under **Batch notes**. It doesn't push, merge or deploy, except in batch 7 and only with your OK.

## Agreed design (spec)

These decisions came out of the design interview on 2026-11-08 and 2026-11-09. Don't change them without asking the user.

### Placement and frame
- **View option:** Map is a third button in `#viewSeg`, with `VIEWS = ['graphic', 'table', 'map']`. Like the other views, it's saved in prefs.
- **Map replaces the grid:** in Map view, the map takes the grid's place. The row-height control and **Group by tag** are hidden. Activity filter, Rank by, Span, the Climb controls and Days all stay.
- **Size and zoom:** the map fills the rest of the window height, at least 400 px. The scroll wheel and trackpad zoom it, and on phones one finger pans.
- **Tiles:** OpenStreetMap tiles. Dark mode inverts them with the same filter as `japow_dashboard.html`, `html:not(.light) .leaflet-tile-pane{filter:invert(1) hue-rotate(180deg) brightness(.9) contrast(.85)}`. Load Leaflet 1.9.4 from cdnjs, as Japow does.
- **Viewport:**
  - The map fits all visible places when Map opens, when the Activity filter changes, and when a place is added by search or with the location button.
  - It doesn't refit when a place is added from the map itself.
  - Pan and zoom are kept only while you stay in Map view.

### Which places appear
- **Visible places:** all places that pass the Activity filter (`placeVisible`).
- **Climb-tagged places:** shown with the pill arch.
- **Other places:** a plain dot with their name. When the current ranking gives the place a number, the dot becomes a small numbered badge.

### Day selection and ranking
- **Day picker:** a picker strip above the map with one button per shown day. It reads and writes the same `TARGET` as the day headings in Graphic and Table, so changing it in one view changes all three. Shift-click and the Span toggle extend it to a span.
- **Default day:** opening Map with no `TARGET` sets it to today (index 0) for real, so the rows stay ranked when you return to Graphic or Table. **Clear ranking** is hidden in Map view.
- **Pills for a span:** each pill is the mean of that third (`climbThirds[t]`) across the days in the span, skipping nulls. The value is null if every day is null.
- **Rank number:** the same rank the rows show, following Rank by and with ties sharing a number. In Map view, ranking ignores `GROUP` and ranks all visible places as one list, so each number appears once.

### Markers
- **Shape:** a sun-path arch of about 200° over the top. Morning is on the left, midday at the top and afternoon on the right. The marker is about 50 px across, the rank sits in the center and the name goes below.
- **Pill colors:** the same five `CLIMB_BANDS` colors for the active theme. A missing score uses the `none` color.
- **Pill hover:** shows a tooltip such as "Morning: 72", with no number on the pill itself.
- **Loading:** three grey pills and no number.
- **Error:** grey pills with "!" in the center.
- **Overlap:** going from #1 down, then unranked places, a place keeps its full marker if it doesn't collide with one already placed. Otherwise it shrinks to a small rank badge, or a dot if it has no rank. Recompute on zoom and move. Hovering a badge shows its full marker on top.

### Popup
Clicking or tapping a place opens a popup with:
- the place name and its rank
- Climb, Ski, Run and Bike tag chips that call `toggleTag`. Tagging Climb turns the dot into an arch right away.
- the selected day or span's high and low, precipitation and wind, in the current units
- morning, midday and afternoon scores
- an **Open forecast** button that switches to Graphic, opens that place's meteogram (`toggleOpen`) and scrolls to it
- **Retry**, when the place's forecast failed to load

### Adding places from the map
- **Gesture:** right-click, or a long press on touch, shows "Add place here".
- **Adding:** the label comes from `reverseLabel`, then `addPlace`. The new place starts untagged and the view doesn't move.
- **Filter exception:** a place added this way stays visible with its popup open even if the Activity filter would hide it. It follows the filter normally once it is tagged or the filter changes.

## Batch details

### Batch 1: Design seams (architect)
- **Goal:** a short design of how the map code fits into `wx_dashboard.html`, written under **Design seams** below. No production code.
- **Questions to settle:**
  - Map state: the map instance, markers by place, whether a fit is pending, and the place exempt from the filter.
  - Where `setView`, `renderAll`, `applyOrder`, `setTarget`, `addPlace`, `removePlace`, `toggleTag` and the place load callbacks call into the map.
  - How ranking ignores `GROUP` in Map view without changing what the rows do.
  - A helper that returns span-averaged thirds.
  - Where the overlap collapse is computed.
  - A function list with signatures.
- **Done when:** the Design seams section is filled in and you have reviewed it.
- **Kickoff:** `Run batch 1 of plans/map-view.md.`

### Batch 2: Map shell (implementer)
- **Scope:** Map in `VIEWS` and `#viewSeg`, the Leaflet include, a `#map` container and CSS with full height, wheel zoom and dark-mode tiles.
- **Show and hide:** hide the grid, legend, row-height and Group controls in Map view. Leave the shared controls visible.
- **Viewport:** the fit rules from the spec.
- **Markers:** a plain dot and name for every visible place, updated on add, remove, rename, filter change and data load.
- **Done when:**
  - switching between all three views works and the choice survives a reload
  - the map fits places correctly
  - dark mode inverts the tiles
  - there are no console errors
- **Kickoff:** `Run batch 2 of plans/map-view.md.`

### Batch 3: Day picker and ranking (implementer, then qa-validator)
- **Scope:** the day picker strip tied to `TARGET`, including shift-click and Span, and today as the default when Map opens.
- **Ranking:** rank across groups in Map view and expose each place's rank to the map.
- **Thirds helper:** the span-averaged thirds helper.
- **Markers:** dot markers temporarily show their rank.
- **QA:** qa-validator hand-checks span averaging against `climbThirds` for 2 or 3 places, including null thirds (polar night, missing data) and ties.
- **Done when:**
  - the day and ranking agree across all three views
  - the averages match the hand calculation
- **Kickoff:** `Run batch 3 of plans/map-view.md.`

### Batch 4: Arch markers (implementer)
- **Scope:** an SVG `divIcon` for the arch, theme-aware colors that re-render on theme change, pill tooltips, the rank center, numbered badges for other places, and the loading and error states.
- **Overlap:** the greedy collapse on `zoomend` and `moveend`, with full markers shown on hover.
- **Done when:**
  - markers are correct in light and dark mode at 3, 7 and 16 days
  - nearby places collapse in rank order
- **Kickoff:** `Run batch 4 of plans/map-view.md.`

### Batch 5: Popup and map adds (implementer)
- **Scope:** the popup content per the spec, with tag chips, Open forecast and Retry.
- **Adding:** "Add place here" on right-click and long-press, using `reverseLabel` and `addPlace` without refitting.
- **Filter exception:** a newly added place is exempt from the filter until it's tagged or the filter changes.
- **Done when:**
  - every popup action works
  - adding a place from the map works on desktop and with mobile emulation
- **Kickoff:** `Run batch 5 of plans/map-view.md.`

### Batch 6: Review and QA (ux-reviewer, qa-validator, then implementer)
- **ux-reviewer:** checks the Map view workflow at desktop and phone width, 375 px.
- **qa-validator edge cases:**
  - 0 places, 1 place, 30 places
  - no Climb places
  - every place filtered out
  - a forecast that fails to load
  - 16 days with a span
  - switching units
  - removing a place while its popup is open
  - no horizontal scroll at phone width
- **Fixes:** the implementer fixes what they confirm.
- **Done when:** no open findings, or the remaining ones are listed under Batch notes with your OK.
- **Kickoff:** `Run batch 6 of plans/map-view.md.`

### Batch 7: Docs and ship (doc-writer)
- **Docs:**
  - the README entry for wx_dashboard.html
  - in-page notes for Map view, next to `noteGfx` and `noteTbl`
  - CONTEXT.md terms if new ones appear, such as "pill arch"
- **Ship:**
  - with your OK, merge `feature/map-view` into `main`
  - deploy only on a separate OK, using the `deploy` skill
- **Kickoff:** `Run batch 7 of plans/map-view.md.`

## Design seams

Line numbers refer to `wx_dashboard.html` at commit 37ce9e6. They will drift as batches land, so search by function name.

### Decisions (spec conflicts; all recommendations accepted by the user on 2026-11-09)

| # | Conflict | Where | Recommendation |
|---|---|---|---|
| D1 | Clicking a day that is already selected clears `TARGET` (`onHeaderClick` 2911-2912). On Map this would leave no day, and the spec hides Clear ranking there. | `onHeaderClick` 2906 | The Map picker uses its own `mapPickDay`: clicking a selected day narrows the selection to that one day. It never sets `TARGET` to null. |
| D2 | A place added from the map is shown on Map even when the filter would hide it. **Open forecast** switches to Graphic, where `placeVisible` (2820) hides that row, so it opens and scrolls to a hidden row. | `toggleOpen` 2969, `applyOrder` 2859 | Hide **Open forecast** for that place until it is tagged. The other choice is to clear `TAGFILTER` first. |
| D3 | Does that place get a rank? The rows never rank it, and the spec says "the same rank the rows show". | `applyOrder` 2849-2853 | It gets no number, so Map numbers match the rows. |
| D4 | Pills skip null days (spec), but the rank does not. `sortKey` (2796) and `climbSpan` (2761) return null if any day in the span is null. A place can show coloured pills and no rank number. | 2756, 2788 | Accept and document it. Don't change the ranking. |
| D5 | "Recompute on zoom and move": a pan doesn't change pixel distances between markers, so the `moveend` recompute is redundant. | none | Keep both listeners as the spec says. The cost is small with 30 or fewer places. |

### 1. Map state and lifecycle

```js
var MAPS = {
  ok: typeof L !== 'undefined', // Leaflet loaded (CDN can fail)
  map: null,       // L.Map, created on first entry to Map view (container must be visible)
  layer: null,     // L.layerGroup holding every place marker
  fitPending: true,// fit visible places at the next mapSync
  exempt: null,    // place added from the map, shown even when TAGFILTER would hide it
  ghost: null,     // non-interactive full marker shown while hovering a collapsed one
  press: null      // long-press state {id, x, y, timer, latlng}
};
```

Fields on each place, initialised in `makePlace` (922-925), following the existing `p.el` pattern:
- `mk`: an `L.Marker` or null.
- `mkHtml`: the last icon HTML. `setIcon` runs only when it changes, which avoids flicker and keeps hover and tooltips working.
- `mkMode`: `'full' | 'badge' | 'dot'`.
- `mapRank`: a number or null.

Lifecycle:
- **Create:** `mapInit()` runs on the first `mapEnter()`. It creates the map with `scrollWheelZoom: true` (Japow uses false; the spec differs on purpose), the OSM tile layer like Japow (689-693), `zoomend`/`moveend` → `mapCollapse`, and `contextmenu` plus long-press → add menu.
- **Never destroyed.** Leaving Map hides `#map`, closes the popup, removes the ghost and sets `fitPending = true`.
- **Viewport:** not saved or stored in prefs. The Leaflet instance keeps pan and zoom while you stay in Map view, and every entry fits again. That meets "kept only while you stay in Map view".
- **Exemption:** in memory only. `MAPS.exempt` is cleared by the filter-chip handler and by `toggleTag(p)` when `p === MAPS.exempt`. Leaving Map does **not** clear it (see D2).
- **Hidden container:** Leaflet can't size or fit inside a hidden container. Order: unhide → `mapSize()` → `invalidateSize()` → fit.

### 2. Call-in points

Every map hook does nothing unless `VIEW === 'map' && MAPS.ok`. One hook in `applyOrder` covers most triggers.

| Caller | Line | Change |
|---|---|---|
| `applyOrder` | 2826 | Call `mapSync()` after `showEmpty` (2870) and **before** the early return at 2873. Placed lower, it is skipped when nothing moved. |
| `renderAll` | 3156 | Start with `syncViewChrome()`. If `VIEW==='map'`: `renderLegend(); syncNotes(); syncViewBar(); applyOrder(); return;`. This skips grid sizing (width is 0 while hidden) and row rendering. |
| `renderRow` | 2720 | After `if (!e) return;`, add `if (VIEW === 'map') return;`. It currently treats every non-graphic view as Table (2726), and `loadPlace` calls it at 1216/1241. |
| `setView` | 3244 | Order: `if (v==='map') { mapEnsureTarget(); MAPS.fitPending = true; } else if (VIEW==='map') mapLeave();`, then set VIEW, `savePrefs()`, `clearCursor()`, then `if (VIEW==='map') mapEnter();` before `renderAll()`. `mapEnsureTarget` assigns `TARGET` directly instead of calling `setTarget`, to avoid a second `applyOrder`. `renderAll` restores the header, cells and band highlights on return. |
| `setTarget` | 2894 | No direct hook. It reaches `applyOrder(true)` at 2903, which runs `mapSync` (ranks, picker, pills). |
| `setDays` | 3203 | After the `TARGET` adjustment at 3207-3208, call `mapEnsureTarget()`. Switching to fewer days can set `TARGET` to null. |
| `addPlace` | 894 | Return `p` instead of `true`. It is still truthy, and the caller at 711 still works. Its `applyOrder` (907) shows the marker. |
| `onAdd` / `useMyLocation` | 711 / 736 | `if (addPlace(loc)) mapRequestFit();`. The flag goes here, not in `addPlace`, because a map add must not refit. |
| `removePlace` | 912 | `mapDrop(p)` before `renderAll()` (918). The place has already left `PLACES`, so `mapSync` can't sweep its marker. |
| `toggleTag` | 2983 | `if (p === MAPS.exempt) MAPS.exempt = null;` before rendering. Climb → `renderAll` and other tags → `applyOrder` both reach `mapSync`, so the dot becomes an arch right away. |
| Filter chips | 3293-3302 | `MAPS.exempt = null; mapRequestFit();` before `applyOrder()` (3301). |
| Group button | 3303 | No hook. Map ignores `GROUP`, and the button is hidden in Map. |
| Rename `finish` | 3111-3115 | No hook. Rename can't be reached in Map view because the rows are hidden, and `mapSync` rebuilds labels on entry. |
| `loadPlace` start | 1215-1216 | `mapUpdatePlace(p)`, so a Retry shows the loading pills right away. |
| `loadPlace` done or failed | 1235-1249 | No hook. `applyOrder(true)` (1244) runs on both success and failure. |
| Theme | 3367, 3374 | No hook. `renderAll` → `mapSync` rebuilds icons from `pal().climb`. The tile invert is CSS only. |
| `setUnits` | 3252 | No hook. `renderAll` → `mapSync` refreshes an open popup. |
| `syncViewBar` | 2955 | `clearBtn.hidden = !TARGET \|\| VIEW==='map'`. The Map `rankInfo` text (2958-2966) must drop the "day heading" and "Drag reorder" wording. |
| Resize | 3355-3363 | Call `mapSize()` on every resize, outside the width-only check at 3359. Otherwise the map height ignores vertical resizes. |
| Init | 3395-3407 | Replace the copied chrome lines 3398-3400 with `syncViewChrome()`, and add `if (VIEW==='map') { mapEnsureTarget(); mapEnter(); }` before `applyOrder()` (3407). This handles a page that loads with Map saved in prefs. |
| HTML | 287-304 | Add a third `#viewSeg` button, give the Group `.grp` an id (`groupGrp`; it has none at 302), and add `#mapDays` + `#map` after `#grid` (328-333). |

### 3. Ranking without GROUP in Map view

- **Extract a ranking function.** Lines 2849-2853 become a pure `rankList(list)`. `applyOrder` calls it once per bucket and copies `it.rank` into `p.rank`, so the rows behave exactly as before.
- **Map rank.** `mapRanks()` calls `rankList(PLACES.filter(placeVisible))` once over all visible places, ignoring buckets, and writes `p.mapRank`. Every other place gets `mapRank = null`, and so does `MAPS.exempt` (D3). Ties share a number, as before.
- **What reads which.** Markers, popup and collapse order read `mapRank`. `p.rank` stays as it is for the rows. It is still computed while in Map (the hidden rows keep their grouped order), so returning to Graphic or Table is unchanged.
- **QA check:** with `GROUP` off and no exempt place, `p.mapRank === p.rank` for every place.

### 4. Span-averaged thirds

```js
// Mean of daily[k].climbThirds[t] for k in [T.a, T.b], skipping null days and days beyond this place's data.
// Returns [morning, midday, afternoon]: each a number (unrounded) or null if every day is null.
// Returns null when p has no data or T is null. Tag-agnostic; callers check CLIMB_TAG.
function spanThirds(p, T) → Array<number|null>(3) | null
```
- Reads `p.data.daily[k].climbThirds` (built in `dayStats`, 1463-1467, 1479).
- Round only for display. Colour with `climbBg(v, P)` (2236).
- It is a sibling of `climbSpan` (2756), which drops the whole span when any day is null. That difference is D4.

### 5. Overlap collapse

`mapCollapse()` is in the batch 4 row of the function table.

**Triggers:** `zoomend` and `moveend`, and the end of every `mapSync` (for added places when the view hasn't moved).

**Inputs:**
- Places with `p.mk`, sorted by `mapRank` ascending. Unranked places come last, and ties keep their `PLACES` order.
- Each place's full-footprint rectangle from `mapFootprint(p)`, placed at `map.latLngToLayerPoint(p.mk.getLatLng())`.
- Full climb marker: about 56 × 72 px including the name. Other places: dot or badge plus the estimated name width.

**Greedy pass:**
- A place stays `'full'` if its rectangle misses every full rectangle already placed.
- Otherwise it becomes `'badge'` if it has a `mapRank`, or `'dot'` if not.
- Only full rectangles take up space.

**Output:**
- `p.mkMode`, applied through `setIcon` only when the mode or HTML changed.
- `zIndexOffset`: full markers stack above collapsed ones, with #1 on top.

**Hover:** mouseover on a collapsed marker adds `MAPS.ghost`, a non-interactive full marker with a high `zIndexOffset`. Mouseout removes it. Swapping the hovered marker's own icon would break its mouse events.

**Pill tooltips:** an SVG `<title>` per pill, e.g. "Morning: 72". Touch users get the scores in the popup.

### 6. Function list

| Function | Returns / purpose | Batch |
|---|---|---|
| `syncViewChrome()` | Shows or hides `#grid`, `#legend`, `#rowhGrp`, `#groupGrp`, `#map`, `#mapDays` for `VIEW` | 2 |
| `mapInit()` | Creates `MAPS.map` and `MAPS.layer`, tiles and event listeners | 2 |
| `mapEnter()` / `mapLeave()` | Show or hide; set `fitPending`, close popup, remove ghost | 2 |
| `mapSize()` | Sets `#map` height to `max(400, innerHeight − top − margin)`, then `invalidateSize` | 2 |
| `mapVisible(p) → bool` | `placeVisible(p) \|\| p === MAPS.exempt` | 2 |
| `mapSync()` | Order: `mapRanks` → add or remove markers → icons → `renderMapDays` → fit if pending → `mapCollapse` → refresh open popup | 2 (adds steps in 3-5) |
| `mapRequestFit()` | Sets `fitPending`; calls `mapFit` now if Map is showing | 2 |
| `mapFit()` | Fits visible places with `fitBounds(pts, {padding, maxZoom: 11})`. No points: leave the view. | 2 |
| `mapDrop(p)` | Removes the marker, closes its popup, clears `exempt` if it was this place | 2 |
| `mapUpdatePlace(p)` | Rebuilds one marker's icon | 2 |
| `mapIconHtml(p, mode, P) → string` | Dot and name (2); arch, badge and state variants (4) | 2, 4 |
| `rankList(list) → [{p, k, rank}]` | Pulled out of `applyOrder` | 3 |
| `mapRanks()` | Writes `p.mapRank` | 3 |
| `spanThirds(p, T)` | See §4 | 3 |
| `mapEnsureTarget()` | `if (VIEW==='map' && !TARGET) TARGET = {a:0, b:0, anchor:0}` | 3 |
| `renderMapDays()` | Picker buttons labelled from `refPlace()`, like `renderHeader` 2622-2629 | 3 |
| `mapPickDay(k, shift)` | Same as `onHeaderClick` but never sets `TARGET` to null (D1); respects `SPAN_MODE` | 3 |
| `placeFailed(p) → bool` | The expression at 3148, shared with `renderCardState` | 4 |
| `mapMarkerState(p) → 'loading'\|'error'\|'ok'` | loading: `status==='loading' && !data`; error: `status==='error'` | 4 |
| `archSvg(thirds, P, state, rank) → string` | About 200° arch, morning on the left; `climbBg` colours, `P.climb.none` for missing | 4 |
| `mapFootprint(p, mode) → {w, h, ax, ay}` | Size and anchor; the anchor is the arch centre | 4 |
| `mapCollapse()` | See §5 | 4 |
| `mapHoverOn(p)` / `mapHoverOff()` | Adds or removes the ghost | 4 |
| `spanStats(p, T) → {hi, lo, total, prob, ws}` | Max hi, min lo, summed total, max prob and ws. A field is null if any day is null, as in `sortKey`. | 5 |
| `mapPopupEl(p) → HTMLElement` | Contents; delegated clicks on `data-act` (tag, open, retry) | 5 |
| `mapOpenForecast(p)` | `setView('graphic')`, `toggleOpen(p)` if closed, `scrollIntoView` | 5 |
| `mapAddMenu(latlng)` / `mapAddHere(latlng)` | `reverseLabel`, falling back to a coordinate label like 732-733, then `addPlace`, then `MAPS.exempt = p`, `mapSync()`, open its popup. No fit. | 5 |
| `mapPressStart(ev)` / `mapPressCancel()` | Touch long-press after 550 ms. Cancel on a move over 10 px, a second pointer, or pointerup. | 5 |

### 7. Risks and gotchas
- **Leaflet CDN failure:** `mapSync` runs from `applyOrder`, so a missing `L` would break every view. Check `MAPS.ok` in every hook and show a message in `#map`.
- **Hidden grid in Map:** `renderAll` sizing (3158-3164) reads width 0. The Map early return avoids this. `loadPlace` still runs `PLACES.forEach(renderCard)` (1242) for open meteograms at minimum width. That is harmless because `setView` → `renderAll` redraws them, but it is wasted work.
- **Empty states:** `showEmpty` (929) writes into the hidden `#cards`, so Map needs its own "no places" and "none match the filter" overlay (batch 2, checked in 6).
- **iOS Safari:** it fires no `contextmenu` on long-press, and Leaflet 1.9 dropped its Tap handler. A custom long-press is required; ignore native `contextmenu` for touch so it doesn't fire twice.
- **Single place:** `fitBounds` on one point zooms to tile max zoom, so `maxZoom` is needed.
- **Day index:** `TARGET` indices are each place's own local day k, as in the rows (`sortKey` 2790). Picker labels follow `refPlace` like the headings.
- **Popup during removal:** the batch 6 case "removing a place while its popup is open" can't really be reached, because rows are hidden in Map and leaving Map closes the popup. `mapDrop` covers it anyway.
- **Duplicate check:** `validPlace` rounds map adds to 4 dp, and the duplicate check (898) is exact lat/lon equality, so two clicks a few metres apart make two places.

## Batch notes

_Each batch adds anything the next ones need to know here: deviations, open issues, gotchas._

- **Batch 1:** D1–D5 in Design seams are settled as recommended and override the spec where they differ: the Map picker never clears `TARGET` (D1), **Open forecast** is hidden for an untagged map-added place (D2), that place has no rank number (D3), pills skip null days while rank doesn't (D4), overlap recomputes on both `zoomend` and `moveend` (D5).
- **Batch 2:** Map shell is in. Deviations and notes for later batches:
  - The map sits in a wrapper `#mapBox` (holds `#map` and the `#mapMsg` overlay); `syncViewChrome` shows and hides it. `#mapDays` exists, empty and hidden, for batch 3.
  - `mapEnter` calls `syncViewChrome` and `mapSize` itself. `mapInit` sets a default view (`MAP_DEFAULT_VIEW`) so markers work before the first fit. Tiles use `maxZoom: 18`.
  - `mapRequestFit` fits immediately and clears `fitPending`; `mapSync` fits only when the flag is pending (set by `setView`).
  - `mapEnsureTarget` and the `setDays` hook are not done yet (batch 3). Until then Clear ranking is hidden in Map, so a `TARGET` set in Graphic or Table can only be cleared there.
  - Not yet checked visually: dot-and-name styling, Leaflet-load-failure message, refit on a filtered subset. Map-tile rendering was blank in the preview pane; markers rendered and there were no console errors.
- **Batch 3:** Day picker, map-wide ranking and `spanThirds` are in; qa-validator hand-checked them (span means incl. null/polar-night/beyond-data days, ties, GROUP on/off, exempt place, `mapPickDay`) with no defects. Notes:
  - `mapEnsureTarget` runs in `setView` after `VIEW = v` (it checks `VIEW==='map'`), not before as Design seams says.
  - Opening Map sets TARGET to day 0 for real and it stays when returning to Graphic or Table, per spec.
  - `#mapDays` buttons are `.mdb` (rebuilt on every `mapSync`, so don't hold references). Ranked dots show a `.mkb` number badge until batch 4. Climb places are still dots; `spanThirds` isn't used by any marker yet.
  - Checked in the browser with one place only (single rank, picker, shift-click, no console errors). Not checked visually: dark mode, 375 px, multi-place ranking with GROUP on.
  - `syncViewChrome` has an odd `legend.hidden = map || legend.hidden` (batch 2 code), left alone.
- **Batch 4:** Arch markers and overlap collapse are in (`archSvg`, `mapMarkerState`, `mapFootprint`, `mapCollapse`, `mapHoverOn/Off`, `MAP_ARCH`). Notes:
  - Each pill has a thin `var(--text)` outline under it, so grey (none/loading/error) pills stay visible on light tiles. Added beyond the spec.
  - Collapsed markers (`badge`, `dot`) drop the name label; hovering shows the full marker as a non-interactive ghost. Non-climb places also collapse, so their name goes too.
  - Marker modes start at `'full'`; `mapSync` ends with `mapCollapse()`, which also runs on `zoomend` and `moveend`. z-order: full above collapsed, lower rank on top.
  - `placeFailed` wasn't extracted; `mapMarkerState` tests `status` directly (error: `status==='error'`).
  - Checked in the browser: arch colours, rank center, loading and error states, collapse order by rank at zoom 6 vs 11, hover ghost, light and dark, 16-day span, no console errors. Not checked: 375 px phone width, and touch (tooltips don't show on touch; the batch 5 popup carries the scores). OSM tiles render in light mode only in the preview pane.
- **Batch 5:** Popup and map adds are in (`mapPopupEl`, `spanStats`, `mapOpenForecast`, `mapAddMenu`, `mapAddHere`, `mapPressStart/Move/Cancel`). Notes:
  - Popup refreshes at the end of `mapSync` and closes on `mapLeave`, `mapDrop`, or when its marker disappears. Scores show for Climb-tagged places only. Retry shows on `status==='error'`.
  - Popup and menu click handlers call `stopPropagation`: `toggleTag` rebuilds the buttons, and Leaflet otherwise treats the click as a map click and closes the popup.
  - Tagging the map-added place with a tag the filter excludes (e.g. Run under a Climb filter) hides it and closes its popup, per the exemption rule.
  - If you leave Map while the name lookup is in flight, the place is still added but no exempt is set and no popup opens.
  - Checked with headless Chrome over synthetic events (right-click, long-press, cancel paths, light and dark, unit switch) and a final browser-pane check with no console errors. Not checked: real touch, iOS Safari, 375 px width, the 30-place cap message in the add menu (for batch 6).
- **Batch 6:** ux-reviewer and qa-validator found no blocking defects; the implementer fixed what they confirmed. Notes:
  - QA edge cases all passed (0/1/30 places, no Climb, all filtered, forecast failure, 16-day span, `setDays` shrink, unit switch, Leaflet blocked, Map saved in prefs, 375 px with no horizontal scroll).
  - Fixed: map height after the day picker fills (M1), Retry feedback in the popup (M2), failed refresh with old data now shows an error and Retry via a shared `placeFailed` (M3), no-Leaflet strip and help text (M4), `mapDrop` only closes its own popup (M5), double-add guard, 40 px tap targets on touch/phone, single-row scrolling day strip on phones, badge contrast in dark mode, larger hit areas on dots and badges, error ring on non-climb markers, dark-mode Leaflet controls, tile-failure message, long-press cancel on drag and vibrate, add-place hint text, autoPan on map adds, `.mkn` max width.
  - **Open, for your call:** (1) at 375 px the controls take about 600 px, so the map starts below the first screen (the 400 px minimum is in the spec); (2) a place added by search or location that the Activity filter hides shows no marker, with no exemption (matches the rows); (3) markers aren't keyboard-focusable (`keyboard:false`).
  - Not exercised: real touch and iOS Safari, the tile-failure message, the red error ring on non-climb markers, the day strip scroll-into-view with an overflowing strip, autoPan near the bottom edge.
