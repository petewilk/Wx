# Wx

Standalone HTML/JS weather and climate visualization tools. No build step — open a file in a browser, or serve the folder statically.

## Pages

### [swe_dashboard.html](swe_dashboard.html)
Snow Water Equivalent (SWE) dashboard for the Wasatch Mountains, pulling live data from the [NRCS SNOTEL network](https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/data). Search by zip code, station, lat/lon, place name, or current location; automatically determines the current water year.

### [day_length_change.html](day_length_change.html)
Plots the rate of change of day length (minutes of daylight gained/lost per day) across the year, with day length itself on a linked chart below, for up to four locations, using [NOAA's solar calculator formulas](https://gml.noaa.gov/grad/solcalc/calcdetails.html).

## Location lookup

Both pages resolve place names and coordinates via the free [Nominatim](https://nominatim.openstreetmap.org/) and [Zippopotam.us](https://api.zippopotam.us/) APIs.

## Live

Hosted at [www.petewilk.com](https://www.petewilk.com).

## License

MIT — see [LICENSE](LICENSE).
