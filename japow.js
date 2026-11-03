// JMA snow data helpers, shared by japow_dashboard.html and tools/build_japow_history.js.
// Classic script (no modules) so file:// works; also loadable in node via the guarded module.exports at the bottom.

// AMeDAS stations with a snow depth sensor. prec/block/kind address the JMA past-data (etrn) pages:
// kind 'a' = AMeDAS (daily_a1.php), 's' = staffed station (daily_s1.php), whose tables have different columns.
var JAPOW_STATIONS = {
  16126: { n: 'Akaigawa',   jp: '赤井川', e: 148, lat: 43.0833, lon: 140.8200, prec: 16, block: '1091',  kind: 'a' },
  16091: { n: 'Otaru',      jp: '小樽',   e: 25,  lat: 43.1817, lon: 141.0150, prec: 16, block: '47411', kind: 's' },
  16076: { n: 'Yoichi',     jp: '余市',   e: 20,  lat: 43.1817, lon: 140.7583, prec: 16, block: '0052',  kind: 'a' },
  14163: { n: 'Sapporo',    jp: '札幌',   e: 17,  lat: 43.0600, lon: 141.3283, prec: 14, block: '47412', kind: 's' },
  12411: { n: 'Kamikawa',   jp: '上川',   e: 324, lat: 43.8467, lon: 142.7533, prec: 12, block: '0015',  kind: 'a' },
  12471: { n: 'Sounkyo',    jp: '層雲峡', e: 540, lat: 43.7533, lon: 142.9300, prec: 12, block: '1049',  kind: 'a' },
  12551: { n: 'Biei',       jp: '美瑛',   e: 250, lat: 43.5883, lon: 142.4933, prec: 12, block: '1052',  kind: 'a' },
  12442: { n: 'Asahikawa',  jp: '旭川',   e: 120, lat: 43.7567, lon: 142.3717, prec: 12, block: '47407', kind: 's' },
  12626: { n: 'Furano',     jp: '富良野', e: 174, lat: 43.3333, lon: 142.4000, prec: 12, block: '0021',  kind: 'a' },
  12746: { n: 'Shimukappu', jp: '占冠',   e: 332, lat: 42.9783, lon: 142.3950, prec: 12, block: '1189',  kind: 'a' },
  15076: { n: 'Horokanai',  jp: '幌加内', e: 159, lat: 44.0100, lon: 142.1600, prec: 12, block: '1053',  kind: 'a' },
  15041: { n: 'Shumarinai', jp: '朱鞠内', e: 255, lat: 44.2817, lon: 142.1617, prec: 12, block: '1279',  kind: 'a' }
};

// A season runs Nov 1 to May 31 and is named by the year it starts; "day" is the 0-based index from Nov 1.
var SEASON_DAYS = 212;
var SEASON_MONTHS = [11, 12, 1, 2, 3, 4, 5];
var NORMAL_FIRST = 1991, NORMAL_LAST = 2020;   // seasons 1991-92 .. 2020-21, as NRCS uses 1991-2020
var NORMAL_MIN_YEARS = 20;                     // fewer seasons than this falls back to period of record
var POR_MIN_YEARS = 10;

function seasonStart(s) { return new Date(Date.UTC(s, 10, 1)); }
// y/m/d are calendar parts (m 1-12); computed in UTC so the viewer's time zone never shifts a day
function dayOfSeason(y, m, d, s) { return Math.round((Date.UTC(y, m - 1, d) - seasonStart(s)) / 864e5); }
function seasonOf(y, m) { return m >= 6 ? y : y - 1; }   // Jun-Dec belong to the season starting that year
function monthYear(s, m) { return m >= 11 ? s : s + 1; }

function etrnUrl(st, y, m) {
  return 'https://www.data.jma.go.jp/stats/etrn/view/daily_' + (st.kind === 's' ? 's1' : 'a1') +
    '.php?prec_no=' + st.prec + '&block_no=' + st.block + '&year=' + y + '&month=' + m + '&day=&view=';
}

// JMA value cell: '--' = phenomenon absent (0), '///' '×' '#' or blank = missing,
// a trailing ')' or ']' flags a quality caveat on a usable value.
function etrnNum(cell) {
  var t = cell.replace(/&nbsp;/g, '').replace(/\s/g, '');
  if (t === '--') return 0;
  t = t.replace(/[\)\]]$/, '');
  return /^-?\d+(\.\d+)?$/.test(t) ? +t : null;
}

// Parse an etrn daily page into [{ d, snow, depth }] (snow = 降雪の深さの合計, depth = 最深積雪, both cm).
// a1 tables end with snowfall, depth; s1 tables add two weather-summary columns after them.
function parseEtrnDaily(html, kind) {
  var m = /<table[^>]*id=['"]tablefix1['"][^>]*>([\s\S]*?)<\/table>/.exec(html);
  if (!m) return [];
  var out = [];
  m[1].replace(/<tr[^>]*>([\s\S]*?)<\/tr>/g, function(_, row) {
    var cells = [];
    row.replace(/<td[^>]*>([\s\S]*?)<\/td>/g, function(__, c) { cells.push(c.replace(/<[^>]+>/g, '')); });
    var d = cells.length ? parseInt(cells[0], 10) : NaN;
    if (!(d >= 1 && d <= 31)) return;
    var k = kind === 's' ? cells.length - 4 : cells.length - 2;
    out.push({ d: d, snow: etrnNum(cells[k]), depth: etrnNum(cells[k + 1]) });
  });
  return out;
}

// Put one month's parsed rows into season-day arrays
function placeMonth(rows, s, y, m, depth, snow) {
  rows.forEach(function(r) {
    var i = dayOfSeason(y, m, r.d, s);
    if (i < 0 || i >= SEASON_DAYS) return;
    depth[i] = r.depth;
    if (snow) snow[i] = r.snow;
  });
}

function median(a) {
  var s = a.slice().sort(function(x, y) { return x - y; }), h = s.length >> 1;
  return s.length % 2 ? s[h] : (s[h - 1] + s[h]) / 2;
}

// Daily median depth across past seasons: 1991-2020 when enough of those seasons exist, else the
// period of record. Returns { values, label } or null when neither has enough seasons.
function computeNormal(past) {
  function pick(test) { return Object.keys(past).map(Number).filter(test); }
  var seasons = pick(function(s) { return s >= NORMAL_FIRST && s <= NORMAL_LAST; }), label = '1991–2020 median';
  if (seasons.length < NORMAL_MIN_YEARS) {
    seasons = pick(function() { return true; });
    if (seasons.length < POR_MIN_YEARS) return null;
    seasons.sort(function(a, b) { return a - b; });
    label = seasons[0] + '–' + (seasons[seasons.length - 1] + 1) + ' median';
  }
  var values = [];
  for (var d = 0; d < SEASON_DAYS; d++) {
    var v = [];
    seasons.forEach(function(s) { var x = past[s][d]; if (x != null) v.push(x); });
    values.push(v.length >= seasons.length / 2 ? median(v) : null);
  }
  return { values: values, label: label, n: seasons.length };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    JAPOW_STATIONS: JAPOW_STATIONS, SEASON_DAYS: SEASON_DAYS, SEASON_MONTHS: SEASON_MONTHS,
    seasonStart: seasonStart, dayOfSeason: dayOfSeason, seasonOf: seasonOf, monthYear: monthYear,
    etrnUrl: etrnUrl, etrnNum: etrnNum, parseEtrnDaily: parseEtrnDaily, placeMonth: placeMonth,
    median: median, computeNormal: computeNormal
  };
}
