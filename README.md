# Wx

Standalone HTML/JS weather and climate visualization tools. No build step — open a file in a browser, or serve the folder statically.

## Pages

### [swe_dashboard.html](swe_dashboard.html)
Snow Water Equivalent (SWE) dashboard for the Wasatch Mountains, pulling live data from the [NRCS SNOTEL network](https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/data). Search by zip code, station, lat/lon, place name, or current location; automatically determines the current water year.

### [japow_dashboard.html](japow_dashboard.html)
Hokkaido snow season tracker for a ski trip. Japan publishes snow depth rather than SWE, so each [JMA AMeDAS](https://www.jma.go.jp/bosai/amedas/) station shows this season's daily depth against the 1991–2020 median, plus the deepest, shallowest and median past seasons and daily new-snow bars. Station dots on the map, and the card swatches, use the NRCS iMap % of median colors and bins. A shaded trip window (editable, kept in the browser) shows on every chart. Mid-mountain forecasts for Furano, Tomamu, Kamui and Pippu come from [Open-Meteo](https://open-meteo.com/), and each area links to the [Japan Avalanche Network](https://nadare.jp/) bulletins. Past seasons are baked into `japow_history.js` by `node tools/build_japow_history.js` (rerun each summer); the running season loads live from JMA's past-data pages and hourly AMeDAS feed. Station metadata and the JMA page parser are in `japow.js`. Add `?mock` to the URL for synthetic example data. The stations sit in valleys (20–540 m), so read them as an index of the season, not on-mountain depth.

### [day_length_change.html](day_length_change.html)
Plots the rate of change of day length (minutes of daylight gained/lost per day) across the year, with day length and local sunrise/sunset times on linked charts below (sunrise/sunset can follow each place's actual clock, standard time, or DST all year, using a bundled offline [tz-lookup](https://github.com/darkskyapp/tz-lookup) time zone lookup), for up to four locations, using [NOAA's solar calculator formulas](https://gml.noaa.gov/grad/solcalc/calcdetails.html).

### [wx_dashboard.html](wx_dashboard.html)
Overview of up to 30 places, as a Graphic, Table or Map view. Graphic (default): one timeline strip per place with cloud-cover and temperature tints, rain/snow bars, a rolling 24-hour precipitation line, night shading and a wind marker, plus daily high/low, precipitation and new snow; row height adjustable from 40 to 120 px. Table: a grid by day with icon, high/low, rain/snow, wind, new snow, freezing level, colored to flag problems. Map: places on a [Leaflet](https://leafletjs.com/)/[OpenStreetMap](https://www.openstreetmap.org/) map, where Climb places get a sun-path arch of three Climbing Index pills (morning, midday, afternoon) around their rank, a day picker is shared with the other views, a popup shows tag chips and Open forecast, and right-click or long-press adds a place. You can rename, rank for a day or weekend, tag (Climb, Ski, Run, Bike), filter and group; click a place to open its full meteogram, a replica of meteoblue's All-in-One chart: weather icons, temperature and feels-like, humidity and dew point, rain/snow precipitation with chance and a rolling 24-hour total, freezing level, low/mid/high cloud cover with sunshine, and wind with direction arrows. Data come from the [Open-Meteo](https://open-meteo.com/) forecast API (3 to 16 days, imperial or metric, hourly refresh), with a 10th-90th percentile band from the Open-Meteo ensemble API at 14 and 16 days. A crosshair is synced across all places by the same instant, and charts scroll together on narrow screens. Places are kept in the browser's local storage; **Share places** makes a link (the list packed into the URL fragment, never sent to the server) that loads the same list on another device.

### [avy_map.html](avy_map.html)
Prototype avalanche danger map for the Salt Lake zone. It paints the [Utah Avalanche Center](https://utahavalanchecenter.org/) overall danger rose onto a topographic map: each spot is colored by the rating for its elevation band and aspect, computed in the browser from [AWS Terrain Tiles](https://registry.opendata.aws/terrain-tiles/). Switch between Slope-weighted and All terrain, change the danger opacity, pick one of three basemaps, and step through forecast days. Hover (or tap) the map to see the matching rose cell. It runs on a few sample archived forecasts, not live data, and is not for travel decisions. See [Avalanche forecast data](#avalanche-forecast-data) for how to run it.

## Avalanche forecast data

`avy_map.html` loads its forecasts with `fetch()`, so it must be served over http. Opening it as a `file://` page shows "Serve over http (see README)". From the repo root:

```
python3 -m http.server 8765
```

Then open http://localhost:8765/avy_map.html.

Forecasts are static JSON files, one folder per forecast center and zone:

- `data/avy/{center}/{zone}/{YYYY-MM-DD}.json` is one forecast day, for example `data/avy/uac/salt-lake/2025-02-11.json`. The date is the center's forecast date in Mountain time.
- `data/avy/{center}/{zone}/index.json` lists the days that have a file, oldest first. The newest day is the last entry.

A day file has the fields `schema`, `center`, `zone`, `zone_name`, `date`, `sample`, `source`, `source_url`, `issued_at`, `fetched_at`, `overall_danger_rose` and `problems`.

- `overall_danger_rose` is the UAC overall danger rose as 24 integers: the upper, mid and low elevation bands in that order, each running N, NE, E, SE, S, SW, W, NW clockwise. Values are 0 (no rating), 2 (Low), 4 (Moderate), 6 (Considerable), 8 (High) and 10 (Extreme). An odd value means pockets of the next level up, so 3 is Low with pockets of Moderate. Anything that isn't 24 integers from 0 to 10 shows "Forecast data malformed".
- `sample` is `true` for hand-entered archived days. The page shows "Sample data" for them.
- `problems` is reserved for per-problem roses. The page ignores it.

A day with no forecast has no file and isn't in the index. The date switcher skips it, and picking it shows "No forecast for this date".

Add `?date=YYYY-MM-DD` to the URL to open a specific day, for example `avy_map.html?date=2025-02-11`. The switcher keeps it up to date. A missing or invalid date opens the newest day.

`deploy.sh` also ships the git-tracked `data/avy` JSON files, so commit new day files and the updated `index.json` before deploying. The page is deployed but not linked from the site.

## Location lookup

All pages except `avy_map.html` resolve place names and coordinates via the free [Nominatim](https://nominatim.openstreetmap.org/) and [Zippopotam.us](https://api.zippopotam.us/) APIs.

## Live

Hosted at [www.petewilk.com](https://www.petewilk.com).

## License

MIT — see [LICENSE](LICENSE).
