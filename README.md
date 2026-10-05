# Wx

Standalone HTML/JS weather and climate visualization tools. No build step — open a file in a browser, or serve the folder statically.

## Pages

### [swe_dashboard.html](swe_dashboard.html)
Snow Water Equivalent (SWE) dashboard for the Wasatch Mountains, pulling live data from the [NRCS SNOTEL network](https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/data). Search by zip code, station, lat/lon, place name, or current location; automatically determines the current water year.

### [day_length_change.html](day_length_change.html)
Plots the rate of change of day length (minutes of daylight gained/lost per day) across the year, with day length and local sunrise/sunset times on linked charts below (sunrise/sunset can follow each place's actual clock, standard time, or DST all year, using a bundled offline [tz-lookup](https://github.com/darkskyapp/tz-lookup) time zone lookup), for up to four locations, using [NOAA's solar calculator formulas](https://gml.noaa.gov/grad/solcalc/calcdetails.html).

### [meteogram_dashboard.html](meteogram_dashboard.html)
Overview of up to 30 places, as a Graphic view (default: one timeline strip per place with cloud-cover and temperature tints, rain/snow bars, a rolling 24-hour precipitation line, night shading and a wind marker, plus daily high/low, precipitation and new snow) or a Table view (a grid by day with icon, high/low, rain/snow, wind, new snow, freezing level, colored to flag problems), that you can rename, rank for a day or weekend, tag (Climb, Ski, Run, Bike), filter and group; click a place to open its full meteogram, a replica of meteoblue's All-in-One chart: weather icons, temperature and feels-like, humidity and dew point, rain/snow precipitation with chance and a rolling 24-hour total, freezing level, low/mid/high cloud cover with sunshine, and wind with direction arrows. Data come from the [Open-Meteo](https://open-meteo.com/) forecast API (3 to 16 days, imperial or metric, hourly refresh), with a 10th-90th percentile band from the Open-Meteo ensemble API at 14 and 16 days. A crosshair is synced across all places by the same instant, and charts scroll together on narrow screens.

## Location lookup

All pages resolve place names and coordinates via the free [Nominatim](https://nominatim.openstreetmap.org/) and [Zippopotam.us](https://api.zippopotam.us/) APIs.

## Live

Hosted at [www.petewilk.com](https://www.petewilk.com).

## License

MIT — see [LICENSE](LICENSE).
