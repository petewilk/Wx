# Avalanche map replay (avy_map.html)

Adds a timeline bar to `avy_map.html` for playing the forecast days in a date range, at an adjustable speed, with a day slider for stepping back and forth between days of interest. The design was settled in a grilling session on 2026-11-22.

## Batches

| # | Batch | Agents | Description | Status |
|---|-------|--------|-------------|--------|
| 1 | Timeline bar and playback | architect, implementer, qa-validator | Bar below the map with play/pause, dwell time, loop and the day slider over all forecast days; wait-then-dwell playback; no blanking between days; hover readout kept across days. | Not started |
| 2 | Range, URL and saved settings | implementer, qa-validator | Start/End pickers and All; slider limited to the range; `?from=&to=`; dwell and loop in localStorage. | Not started |
| 3 | Review, docs and ship | ux-reviewer, qa-validator, doc-writer | Phone and dark-mode check, keyboard and a11y, README and CONTEXT.md, About note, then merge with the user's OK. | Not started |

Status values: `Not started` · `In progress` · `Done` · `Blocked: <reason>`.

## How to run a batch

1. Start a new session in `/Users/peterwilk/Documents/repos/Wx`, without a worktree, and paste the batch's **Kickoff** line.
2. The session creates or checks out `feature/avy-replay` (branched from `main`), reads this whole file, and sets the batch's row to `In progress`.
3. **Use the agents named in the batch row** through the Agent tool. Facts come from `librarian` / `web-fetch`, never from the user. Check each agent's output before using it.
4. **Verify in the browser preview** with the `swe-dashboard` server from `.claude/launch.json` (port 8765) at `/avy_map.html`. On localhost the page uses `data/avy-local/uac/salt-lake/` (5 days, big gaps: 2018-11-22, 2026-04-01, 2026-11-20…22); the samples in `data/avy/uac/salt-lake/` have 4 days with a gap on 2025-02-12. Test with both.
5. **Finish the batch:** commit to `feature/avy-replay`, set the row to `Done`, and add what later batches need under **Batch notes**. Don't push, merge or deploy without the user's OK.

## Batch details

Every batch's kickoff is `Run batch N of plans/avy-replay.md.` Follow **How to run a batch** and the **Agreed design** below.

### Batch 1: Timeline bar and playback (architect, implementer, qa-validator)
- **Kickoff:** `Run batch 1 of plans/avy-replay.md.`
- `architect` first: decide how the replay state (day list, current index, playing, dwell, loop) sits beside the existing `loadDay` / `setDay` / `pickDate` / `syncSwitcher` flow, so there is still one place that decides the shown day.
- Build the bar with play/pause, dwell select, loop toggle, the day slider and a current-date label. The slider spans every index date for now (batch 2 adds the range).
- Playback: wait for the day to be loaded and painted, then dwell. Prefetch the next day's file while dwelling. See **Playback**.
- Make day changes from the slider and from playback keep the previous day's colors until the new day is ready (no "Loading forecast…" blank). This also fixes the clear-then-repaint flash noted in batch 7 of `plans/avy-rose-map.md`.
- Keep the hover/tap readout: after each day change, re-run `lookup()` on the last queried point instead of resetting to "Hover the map".
- Check in the browser: play through local and sample data at every dwell time, loop on and off, scrub fast both ways, arrow keys, space, the switcher and slider staying in sync, a slow network (devtools throttling) still showing each day for the full dwell.

### Batch 2: Range, URL and saved settings (implementer, qa-validator)
- **Kickoff:** `Run batch 2 of plans/avy-replay.md.`
- Add Start and End date inputs and an **All** button. Apply the rules under **Range**.
- `?from=` / `?to=` in the URL; `avyMap.replayDwell` and `avyMap.replayLoop` in localStorage. See **URL and saved settings**.
- Check in the browser: a range with gap dates at both ends, start after end, a one-day range, a range with no forecasts, the ‹ › switcher leaving the range, bad `?from=` / `?to=`, reload keeps range, dwell and loop, a private window falls back to defaults.

### Batch 3: Review, docs and ship (ux-reviewer, qa-validator, doc-writer)
- **Kickoff:** `Run batch 3 of plans/avy-replay.md.`
- ux-reviewer: phone layout (bar must not hide the rose panel or attribution), dark mode, touch targets, keyboard focus, screen-reader labels and an `aria-live` date label that doesn't chatter during fast playback.
- qa-validator: stale-response handling under fast scrubbing, timer cleanup on pause, file:// behaviour, regressions in the switcher and `?date=`.
- doc-writer: README `avy_map.html` entry (replay, `?from=&to=`), CONTEXT.md terms (**Replay range**, **Dwell time**), one line in the "About this map" note.
- Merge to `main` and deploy only with the user's OK.

## Agreed design (2026-11-22)

### Steps
- Replay steps through **forecast days only**, the dates in `index.json`, like the ‹ › buttons. Gap days are skipped.

### Layout
- A **timeline bar below the map, always shown**, holds: Start, End, All · play/pause · dwell time · loop · day slider · current-date label.
- The existing ‹ date › switcher in the rose panel stays. The switcher and the slider always show the same day.
- When the page is opened as a local file (file://), or the index can't be loaded, the bar is disabled with the same `title` reason as the switcher.

### Range
- **Start and End date inputs plus an All button.** All runs from the first forecast to the last and is the default.
- A Start or End that falls on a gap moves inward to the nearest forecast day inside the range. Start after End: swap them. A range with no forecast days: keep the previous range and show a short message.
- The **slider spans only the range**. Choosing a day outside it with the ‹ › switcher or the date input resets the range to All.

### Slider
- **One equal notch per forecast day**, so gaps don't show on the track. The track is **plain**, with no danger colors.
- **Live scrubbing:** the map and rose follow the thumb day by day. Only the latest requested day is applied (reuse the `reqToken` pattern).
- Touching the slider **pauses** playback. Arrow keys step one day, as native range inputs do.

### Playback
- Play starts from the current day. If the current day is the end of the range, it starts from the range start.
- **Dwell time** (seconds per day): 2, 1, 0.5 or 0.25 s. Default 1 s.
- **Wait, then dwell:** the dwell timer starts only once the day is loaded and its visible tiles are painted, so every day shows for the full dwell. While dwelling, prefetch the next day's file.
- `repaint()` should report when it's done (for example, return a promise covering tiles whose terrain had to be reloaded), so playback knows when the day is painted.
- **Loop toggle**, default off. Off: stop on the last day; pressing play again restarts from the range start. On: go back to the range start and keep playing.
- **Space** plays and pauses when focus isn't in a text or date input.
- Every step updates `?date=` with `history.replaceState`, as the switcher does now.
- A day that fails to load (missing file or malformed data) shows its normal message for one dwell, then playback moves on.

### Hover readout
- If a spot was hovered or tapped, the readout and rose highlight **refresh for that spot on each new day** instead of resetting. Moving the mouse off the map still clears it.

### URL and saved settings
- **Range in the URL:** `?from=YYYY-MM-DD&to=YYYY-MM-DD`, alongside `?date=`, validated with `isDate`. Missing or invalid values mean All and are removed from the URL. A `?date=` outside the range resets the range to All.
- **Dwell time and loop in localStorage:** `avyMap.replayDwell` (`2` | `1` | `0.5` | `0.25`) and `avyMap.replayLoop` (`true` | `false`), read and written with the existing `loadSetting` / `saveSetting` helpers. Invalid values fall back to the defaults.
- The page **always opens paused**.

## Code entry points (as of `cb662cb`)

- `loadDay(date)` loads one day and drops stale responses via `reqToken`. It currently blanks the day first with `setDay(null, date, 'Loading forecast…')`.
- `setDay(newDay, date, msg)` sets the day, repaints and resets the readout to "Hover the map".
- `pickDate(date)` writes `?date=` and calls `loadDay`. `syncSwitcher()` keeps the switcher in sync, and `prevIndexDate` / `nextIndexDate` step over gaps.
- `DangerLayer.repaint()` repaints painted tiles synchronously, except tiles whose terrain was evicted from the cache, which repaint after `loadDem` resolves.
- `lookup(latlng)` / `schedule(ll)` run the hover/tap readout. `pending` is cleared on `mouseout` and `zoomend`.

## Open decisions

None.

## Batch notes

(none yet)
