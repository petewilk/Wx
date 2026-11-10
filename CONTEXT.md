# Context

Glossary of terms used by the Best climbing ranking and the Map view markers in `wx_dashboard.html`, and by the danger map in `avy_map.html`.

**Climbing Index**
A heuristic score from 0 to 100 for how good the weather is for rock climbing. It is computed for each hour, averaged over the daylight hours to give a daily value, and averaged over the ranked days to rank places. It is not a validated model and does not know a crag's aspect or local shade.

**Gate**
A factor from 0 to 1 that says whether climbing is plausible at all, regardless of how pleasant the temperature is. It falls with wet rock, a chance of precipitation, thunderstorms, ice on damp rock and strong wind.

**Quality**
A factor from 0 to 1 that says how pleasant the conditions are, given that climbing is possible. It combines how close the effective temperature is to the climber's ideal with how dry the air is.

**Effective temperature**
The air temperature adjusted for what it feels like on the rock: warmer in sun, cooler in wind. It is used in place of the raw air temperature when judging comfort.

**Wetness bucket**
A running estimate of how much water is still on the rock, in millimetres. Rain fills it; sun, wind and dry air drain it; dew can add a little.

**Sun knob**
A single global setting (Sunny, Mixed or Shady) for the kind of walls the climber is planning for. It sets how much the sun warms the effective temperature and stands in for aspect, which is not stored per place.

**Pill arch**
The sun-path arch of three pills drawn around a Climb place's rank on the Map view: morning on the left, midday on top, afternoon on the right. Each pill is colored by the Climbing Index for that third of the daylight hours.

**Collapse**
On the Map view, overlapping lower-ranked places shrink to a rank badge or dot so the best-ranked place keeps its full marker.

**Danger rose**
The avalanche center's diagram of danger by elevation band and aspect, stored as 24 values (upper, mid and low bands, each N to NW clockwise). The map uses only the overall rose, not the per-problem roses.

**Elevation band**
One of three height ranges that pick a ring of the rose: low below 8,000 ft, mid from 8,000 to 9,500 ft, upper above 9,500 ft. The edges are hard.

**Aspect**
The compass direction a slope faces downhill, in eight 45° slices centred on N, NE, E and so on. It picks the wedge of the rose.

**Danger level**
The rating of a rose cell: Low (2), Moderate (4), Considerable (6), High (8) or Extreme (10), with 0 for no rating. Colors follow the North American danger scale.

**Pockets of**
An odd rose value (1, 3, 5, 7, 9) meaning pockets of the next level up over the level below it. The map and rose draw it as the lower level's color with diagonal stripes of the higher level.

**Zone**
One forecast area of an avalanche center, such as Salt Lake for the Utah Avalanche Center. The map shows one zone and clips the colors to its outline.

**Slope-weighted mode**
A mode that fades the danger color in from none at 25° to full at 35°, so gentle ground stays clear. Compare All terrain.

**All terrain mode**
A mode that colors every spot except slopes under 5°, where aspect means nothing. It is the first-visit default.

**Sample day**
A forecast day whose rose was entered by hand from UAC's archive, marked `"sample": true` in its file. The panel shows "Sample data" for it.

**Gap day**
A date with no forecast file, so it isn't in the index. The date switcher skips it, and picking it shows "No forecast for this date".
