#!/usr/bin/env python3
"""Refresh local UAC Salt Lake danger roses from the daily forecast emails.

Usage:
    python3 -I tools/fetch_uac_roses.py          # add days not saved yet
    python3 -I tools/fetch_uac_roses.py --all    # redo every email

Reads the "Forecast: Salt Lake Area Mountains" emails from Gmail over IMAP,
downloads each email's overall danger rose PNG, decodes the 24 cells from
their colors, and writes day files plus index.json under
data/avy-local/uac/salt-lake/ (git-ignored, so deploy.sh never uploads them).
avy_map.html reads that folder when it is served from localhost.

Gmail login comes from 1Password through its CLI (`op`). The item holds the
Gmail address as username and a Gmail app password as password. Default item
reference: op://Private/Wx avy map (override with WX_UAC_OP_ITEM).

Limitation: the rose PNG draws "pockets of" a level in that level's plain
color, so decoded roses only contain even values (0, 2, 4, 6, 8, 10).

Standard library only.
"""

import argparse
import datetime as dt
import email
import email.policy
import html
import imaplib
import json
import os
import re
import struct
import subprocess
import sys
import urllib.parse
import urllib.request
import zlib
from zoneinfo import ZoneInfo

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, 'data', 'avy-local', 'uac', 'salt-lake')
PNG_DIR = os.path.join(OUT_DIR, 'png')
MOUNTAIN = ZoneInfo('America/Denver')
UTC = dt.timezone.utc

OP_ITEM_DEFAULT = 'op://Private/Wx avy map'
IMAP_HOST = 'imap.gmail.com'
SENDER = 'no-reply@utahavalanchecenter.org'
SUBJECT = 'Salt Lake'
USER_AGENT = 'Wx-avy-map-local/1.0 (personal use; reads forecast email images)'

SETUP_HELP = """\
One-time setup:
  1. brew install 1password-cli
  2. 1Password app > Settings > Developer > turn on "Integrate with 1Password CLI"
  3. Google Account > Security > 2-Step Verification > App passwords: create one
  4. Save a 1Password login item named "Wx avy map" in the Private vault, with
     your Gmail address as username and the app password as password
     (or point WX_UAC_OP_ITEM at another item, e.g. op://Vault/Item)."""


# ---------------------------------------------------------------- PNG reader

class RoseError(ValueError):
    """The image or email is not something this tool can decode."""


def read_png(data):
    """Decode an 8-bit, non-interlaced RGB or RGBA PNG. Returns (width, height, bpp, rows)."""
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise RoseError('not a PNG file')
    pos, idat, ihdr = 8, [], None
    while pos + 8 <= len(data):
        length, ctype = struct.unpack('>I4s', data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if ctype == b'IHDR':
            ihdr = struct.unpack('>IIBBBBB', body)
        elif ctype == b'IDAT':
            idat.append(body)
        elif ctype == b'IEND':
            break
    if ihdr is None:
        raise RoseError('PNG has no IHDR chunk')
    width, height, depth, color_type, _comp, _filt, interlace = ihdr
    if depth != 8 or color_type not in (2, 6) or interlace != 0:
        raise RoseError('unsupported PNG (depth %d, color type %d, interlace %d); '
                        'expected 8-bit non-interlaced RGB/RGBA' % (depth, color_type, interlace))
    bpp = 4 if color_type == 6 else 3
    try:
        raw = zlib.decompress(b''.join(idat))
    except zlib.error as e:
        raise RoseError('corrupt PNG data: %s' % e)
    stride = width * bpp
    if len(raw) < height * (stride + 1):
        raise RoseError('truncated PNG data')
    rows, prev, i = [], bytearray(stride), 0
    for _ in range(height):
        ftype = raw[i]
        line = bytearray(raw[i + 1:i + 1 + stride])
        i += stride + 1
        if ftype == 1:
            for x in range(bpp, stride):
                line[x] = (line[x] + line[x - bpp]) & 255
        elif ftype == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif ftype == 3:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + ((a + prev[x]) >> 1)) & 255
        elif ftype == 4:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x - bpp] if x >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        elif ftype != 0:
            raise RoseError('bad PNG filter type %d' % ftype)
        rows.append(line)
        prev = line
    return width, height, bpp, rows


# ---------------------------------------------------------------- rose decoder

ROSE_SIZE = (400, 440)
ROSE_CENTER = (201, 156)
ASPECTS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
# Distance in px from ROSE_CENTER along each aspect's compass direction to the
# middle of that cell's top face, per band. Measured on UAC rose PNGs
# (2024-12-24 to 2026-11-22: same layout). The rose is drawn in perspective,
# so the southern half is stretched.
SAMPLE_RADIUS = {
    'upper': [28, 28, 28, 28, 28, 28, 28, 28],
    'mid':   [56, 59, 72, 77, 78, 78, 74, 59],
    'low':   [88, 92, 110, 122, 125, 123, 112, 92],
}
# Top-face fill color for each level (same palette as avy_map.html LEVELS,
# plus UAC's gray for no rating). No rating, Low, Moderate and Considerable
# were checked against real roses. High and Extreme have not appeared in a
# rose yet and use the UAC palette; any other color fails loudly.
PALETTE = {
    0: (0xC0, 0xC0, 0xC0),
    2: (0x50, 0xB8, 0x48),
    4: (0xFF, 0xF2, 0x00),
    6: (0xF7, 0x94, 0x1E),
    8: (0xED, 0x1C, 0x24),
    10: (0x23, 0x1F, 0x20),
}
COLOR_TOLERANCE = 12      # max per-channel difference from a palette color
PATCH = 2                 # sample a (2*PATCH+1)^2 square
MIN_SHARE = 0.8           # share of patch pixels that must agree


def _classify(rgb):
    for level, ref in PALETTE.items():
        if all(abs(a - b) <= COLOR_TOLERANCE for a, b in zip(rgb, ref)):
            return level
    return None


def decode_rose(png_bytes):
    """Return the 24-value overall danger rose (upper, mid, low; N..NW) from a UAC rose PNG."""
    import math
    width, height, bpp, rows = read_png(png_bytes)
    if (width, height) != ROSE_SIZE:
        raise RoseError('rose image is %dx%d, expected %dx%d' % ((width, height) + ROSE_SIZE))
    cx, cy = ROSE_CENTER
    values = []
    for band in ('upper', 'mid', 'low'):
        for k, aspect in enumerate(ASPECTS):
            ang = math.radians(k * 45)
            r = SAMPLE_RADIUS[band][k]
            x0 = round(cx + r * math.sin(ang))
            y0 = round(cy - r * math.cos(ang))
            votes, colors = {}, []
            for dy in range(-PATCH, PATCH + 1):
                for dx in range(-PATCH, PATCH + 1):
                    o = (x0 + dx) * bpp
                    rgb = tuple(rows[y0 + dy][o:o + 3])
                    colors.append(rgb)
                    lv = _classify(rgb)
                    if lv is not None:
                        votes[lv] = votes.get(lv, 0) + 1
            n = (2 * PATCH + 1) ** 2
            best = max(votes.items(), key=lambda kv: kv[1]) if votes else (None, 0)
            if best[1] < MIN_SHARE * n:
                common = max(set(colors), key=colors.count)
                raise RoseError('%s %s cell: unrecognized color rgb%s at (%d,%d)'
                                % (band, aspect, common, x0, y0))
            values.append(best[0])
    return values


# ---------------------------------------------------------------- email parsing

FORECAST_LINK_RE = re.compile(r'utahavalanchecenter\.org/forecast/salt-lake/(\d{1,2})/(\d{1,2})/(\d{4})')
ROSE_IMG_RE = re.compile(r'<img\b[^>]*\bsrc="(https://utahavalanchecenter\.org/sites/default/files/'
                         r'forecast/\d{6}/(\d{8})-(\d{6})-\d+\.png)"', re.I)


def parse_forecast_email(raw_bytes):
    """Return {date, rose_url, issued_at, source_url} from a raw UAC forecast email."""
    msg = email.message_from_bytes(raw_bytes, policy=email.policy.default)
    html_part = msg.get_body(preferencelist=('html',))
    text_part = msg.get_body(preferencelist=('plain',))
    html_body = html_part.get_content() if html_part else ''
    text_body = text_part.get_content() if text_part else ''

    # The HTML wraps links in a click tracker with the real URL percent-encoded.
    m = FORECAST_LINK_RE.search(urllib.parse.unquote(html_body)) or FORECAST_LINK_RE.search(text_body)
    if not m:
        raise RoseError('no Salt Lake forecast link (older email format?)')
    month, day, year = (int(g) for g in m.groups())
    try:
        date = dt.date(year, month, day).isoformat()
    except ValueError:
        raise RoseError('bad forecast date in link: %s' % m.group(0))

    # The overall rose is the first forecast image; problem roses come later.
    img = ROSE_IMG_RE.search(html_body)
    if not img:
        raise RoseError('no rose image in email')
    rose_url = html.unescape(img.group(1))
    stamp = dt.datetime.strptime(img.group(2) + img.group(3), '%Y%m%d%H%M%S').replace(tzinfo=MOUNTAIN)
    return {
        'date': date,
        'rose_url': rose_url,
        'issued_at': stamp.astimezone(UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source_url': 'https://utahavalanchecenter.org/forecast/salt-lake/%d/%d/%d' % (month, day, year),
    }


def day_record(info, rose, fetched_at):
    return {
        'schema': 1,
        'center': 'uac',
        'zone': 'salt-lake',
        'zone_name': 'Salt Lake',
        'date': info['date'],
        'sample': False,
        'source': 'uac-email-png',
        'source_url': info['source_url'],
        'issued_at': info['issued_at'],
        'fetched_at': fetched_at,
        'overall_danger_rose': rose,
        'problems': [],
    }


# ---------------------------------------------------------------- I/O

def write_json(path, obj):
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')
    os.replace(tmp, path)


def saved_dates(out_dir):
    if not os.path.isdir(out_dir):
        return []
    return sorted(n[:-5] for n in os.listdir(out_dir) if re.fullmatch(r'\d{4}-\d{2}-\d{2}\.json', n))


def write_index(out_dir, now):
    write_json(os.path.join(out_dir, 'index.json'), {
        'schema': 1, 'center': 'uac', 'zone': 'salt-lake',
        'updated_at': now, 'dates': saved_dates(out_dir),
    })


def op_read(ref):
    try:
        r = subprocess.run(['op', 'read', ref], capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        raise SystemExit('1Password CLI (op) not found.\n' + SETUP_HELP)
    if r.returncode != 0:
        raise SystemExit('Could not read %s from 1Password: %s\n%s' % (ref, r.stderr.strip(), SETUP_HELP))
    return r.stdout.strip()


def gmail_login():
    item = os.environ.get('WX_UAC_OP_ITEM', OP_ITEM_DEFAULT).rstrip('/')
    user = op_read(item + '/username')
    password = op_read(item + '/password')
    imap = imaplib.IMAP4_SSL(IMAP_HOST)
    try:
        imap.login(user, password.replace(' ', ''))
    except imaplib.IMAP4.error as e:
        raise SystemExit('Gmail login failed (%s). Use a Gmail app password, not your normal password.\n%s'
                         % (e, SETUP_HELP))
    return imap


def all_mail_folder(imap):
    """Gmail's All Mail folder (its name is localized), found by the \\All flag."""
    typ, lines = imap.list()
    for line in lines or []:
        s = line.decode(errors='replace')
        if '\\All' in s:
            m = re.search(r'"([^"]+)"\s*$', s) or re.search(r'(\S+)\s*$', s)
            if m:
                return m.group(1)
    return 'INBOX'


def fetch_png(url):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def mountain_date_of_internaldate(resp):
    """INTERNALDATE from an IMAP FETCH response line -> Mountain-time date string."""
    m = re.search(rb'INTERNALDATE "([^"]+)"', resp)
    if not m:
        return None
    t = imaplib.Internaldate2tuple(b'INTERNALDATE "' + m.group(1) + b'"')
    if t is None:
        return None
    import time
    return dt.datetime.fromtimestamp(time.mktime(t), UTC).astimezone(MOUNTAIN).date().isoformat()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--all', action='store_true', help='re-decode every email, not just new days')
    args = ap.parse_args(argv)

    os.makedirs(PNG_DIR, exist_ok=True)
    have = set(saved_dates(OUT_DIR))
    now = dt.datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')

    imap = gmail_login()
    try:
        imap.select('"%s"' % all_mail_folder(imap), readonly=True)
        typ, data = imap.uid('SEARCH', None, 'FROM', SENDER, 'SUBJECT', '"%s"' % SUBJECT)
        uids = data[0].split() if typ == 'OK' and data and data[0] else []
        print('Found %d UAC Salt Lake emails.' % len(uids))

        # Cheap pass: skip emails whose received day (Mountain) already has a file.
        todo = []
        for uid in uids:
            typ, meta = imap.uid('FETCH', uid, '(INTERNALDATE)')
            day = mountain_date_of_internaldate(meta[0] if meta and meta[0] else b'')
            if args.all or day is None or day not in have:
                todo.append(uid)

        best = {}          # date -> (info, uid); latest issue wins
        failed = []
        for uid in todo:
            typ, msg_data = imap.uid('FETCH', uid, '(BODY.PEEK[])')
            raw = next((part[1] for part in msg_data if isinstance(part, tuple)), None)
            if raw is None:
                failed.append(('uid %s' % uid.decode(), 'could not download email'))
                continue
            try:
                info = parse_forecast_email(raw)
            except RoseError as e:
                failed.append(('uid %s' % uid.decode(), str(e)))
                continue
            prev = best.get(info['date'])
            if prev is None or info['issued_at'] > prev['issued_at']:
                best[info['date']] = info
    finally:
        try:
            imap.logout()
        except Exception:
            pass

    added = []
    for date in sorted(best):
        info = best[date]
        if date in have and not args.all:
            continue
        png_path = os.path.join(PNG_DIR, date + '.png')
        try:
            png = fetch_png(info['rose_url'])
            rose = decode_rose(png)
        except (RoseError, OSError) as e:
            failed.append((date, str(e)))
            continue
        with open(png_path, 'wb') as f:
            f.write(png)
        write_json(os.path.join(OUT_DIR, date + '.json'), day_record(info, rose, now))
        added.append(date)

    write_index(OUT_DIR, now)
    print('Added %d day(s)%s.' % (len(added), (': ' + ', '.join(added)) if added else ''))
    print('Already saved: %d.' % len(have))
    for what, why in failed:
        print('Skipped %s: %s' % (what, why))
    print('Local data: %s' % os.path.relpath(OUT_DIR, REPO))
    return 1 if failed and not added and not have else 0


if __name__ == '__main__':
    sys.exit(main())
