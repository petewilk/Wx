# Context

Glossary of terms used by the Best climbing ranking in `wx_dashboard.html`.

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
