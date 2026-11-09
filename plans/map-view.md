# Map view for wx_dashboard.html

A third overview style (Graphic | Table | **Map**) that puts every visible place on a Leaflet map. Climb-tagged places get three Climbing Index pills (morning, midday, afternoon) in a sun-path arch around their rank number.

## Batches

Each batch runs in its own new Claude Code session. Batches run **in order**, because every one of them edits `wx_dashboard.html`. Running two at once would cause conflicts.

| # | Batch | Agents | Description | Status |
|---|-------|--------|-------------|--------|
| 1 | Design seams | architect | Decide the map module's state, functions and hooks into the existing render, ordering and ranking code. Write them into this file. | Not started |
| 2 | Map shell | implementer | Add the Map option to View, load Leaflet, set up the full-height map and dark tiles, define when it fits, and show places as plain dots. | Not started |
| 3 | Day picker and ranking | implementer, qa-validator | Add a day picker that shares the selected day with the other views, default to today, rank across tag groups on Map, and average the thirds over a span. | Not started |
| 4 | Arch markers | implementer | Draw the sun-path pill arch, rank centers, numbered badges, loading and error states, and the overlap collapse. | Not started |
| 5 | Popup and map adds | implementer | Add the popup with tag chips and Open forecast, Retry, and adding a place with right-click or long-press. A new place shows until it is tagged. | Not started |
| 6 | Review and QA | ux-reviewer, qa-validator, implementer | Review usability, check edge cases on phone and in dark mode, and fix what they find. | Not started |
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

_Filled in by batch 1._

## Batch notes

_Each batch adds anything the next ones need to know here: deviations, open issues, gotchas._
