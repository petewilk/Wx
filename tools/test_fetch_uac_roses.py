#!/usr/bin/env python3
"""Tests for fetch_uac_roses. Run: python3 -I tools/test_fetch_uac_roses.py"""

import os
import struct
import sys
import tempfile
import unittest
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fetch_uac_roses as f  # noqa: E402

FIX = os.path.join(HERE, 'fixtures', 'uac_rose')
SAMPLES = os.path.join(os.path.dirname(HERE), 'data', 'avy', 'uac', 'salt-lake')


def fixture(name):
    with open(os.path.join(FIX, name), 'rb') as fh:
        return fh.read()


def make_png(width, height, color_type=6, interlace=0, depth=8, pixel=(0, 0, 0, 255)):
    bpp = {6: 4, 2: 3}.get(color_type, 1)
    row = b'\x00' + bytes(pixel[:bpp]) * width
    raw = row * height

    def chunk(t, body):
        return struct.pack('>I', len(body)) + t + body + struct.pack('>I', zlib.crc32(t + body))
    ihdr = struct.pack('>IIBBBBB', width, height, depth, color_type, 0, 0, interlace)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(raw))
            + chunk(b'IEND', b''))


class DecodeRose(unittest.TestCase):
    def check_sample(self, date):
        import json
        with open(os.path.join(SAMPLES, date + '.json')) as fh:
            expected = json.load(fh)['overall_danger_rose']
        self.assertEqual(f.decode_rose(fixture('rose_%s.png' % date)), expected)

    def test_sample_2025_01_30_all_low(self):
        self.check_sample('2025-01-30')

    def test_sample_2025_02_11_mixed(self):
        self.check_sample('2025-02-11')

    def test_sample_2025_02_13(self):
        self.check_sample('2025-02-13')

    def test_pockets_day_reads_as_plain_level(self):
        # The PNG draws "pockets of Moderate" in plain Moderate yellow, so the
        # hand-entered 3s come back as 4s. Documented limitation.
        upper = [4, 4, 4, 2, 2, 2, 4, 4]
        self.assertEqual(f.decode_rose(fixture('rose_2024-12-24.png')), upper + [2] * 16)

    def test_2026_11_21_considerable_upper_nw_n_e(self):
        # Email: Considerable on upper NW-N-E, Moderate other mid/upper, Low below 8,000 ft.
        self.assertEqual(f.decode_rose(fixture('rose_2026-11-21.png')),
                         [6, 6, 6, 4, 4, 4, 4, 6] + [4] * 8 + [2] * 8)

    def test_2026_11_22_moderate_mid_upper(self):
        self.assertEqual(f.decode_rose(fixture('rose_2026-11-22.png')), [4] * 16 + [2] * 8)

    def test_2026_04_01_no_rating_low(self):
        # Spring: Moderate mid/upper, low band unrated (gray).
        self.assertEqual(f.decode_rose(fixture('rose_2026-04-01.png')), [4] * 16 + [0] * 8)

    def test_wrong_size_rejected(self):
        with self.assertRaisesRegex(f.RoseError, 'expected 400x440'):
            f.decode_rose(make_png(10, 10))

    def test_unknown_color_rejected(self):
        with self.assertRaisesRegex(f.RoseError, 'unrecognized color'):
            f.decode_rose(make_png(400, 440, pixel=(255, 255, 255, 255)))

    def test_rgb_png_supported(self):
        green = make_png(400, 440, color_type=2, pixel=(0x50, 0xB8, 0x48))
        self.assertEqual(f.decode_rose(green), [2] * 24)


class ReadPng(unittest.TestCase):
    def test_not_png(self):
        with self.assertRaisesRegex(f.RoseError, 'not a PNG'):
            f.read_png(b'GIF89a....')

    def test_interlaced_rejected(self):
        with self.assertRaisesRegex(f.RoseError, 'unsupported PNG'):
            f.read_png(make_png(4, 4, interlace=1))

    def test_palette_rejected(self):
        with self.assertRaisesRegex(f.RoseError, 'unsupported PNG'):
            f.read_png(make_png(4, 4, color_type=3))

    def test_truncated(self):
        with self.assertRaises(f.RoseError):
            f.read_png(make_png(4, 4)[:40])


class ParseEmail(unittest.TestCase):
    def test_forecast_email(self):
        info = f.parse_forecast_email(fixture('forecast_email.eml'))
        self.assertEqual(info['date'], '2026-11-22')
        self.assertEqual(info['rose_url'], 'https://utahavalanchecenter.org/sites/default/files/'
                                           'forecast/202611/20261122-071604-0.png')
        self.assertEqual(info['issued_at'], '2026-11-22T14:16:04Z')   # 07:16:04 MST
        self.assertEqual(info['source_url'], 'https://utahavalanchecenter.org/forecast/salt-lake/11/22/2026')

    def test_summer_time_issue(self):
        raw = fixture('forecast_email.eml').replace(b'20261122-071604', b'20260401-063000')
        self.assertEqual(f.parse_forecast_email(raw)['issued_at'], '2026-04-01T12:30:00Z')   # MDT

    def test_no_rose_image(self):
        raw = fixture('forecast_email.eml').replace(b'sites/default/files/forecast', b'elsewhere')
        with self.assertRaisesRegex(f.RoseError, 'no rose image'):
            f.parse_forecast_email(raw)

    def test_no_forecast_link(self):
        raw = fixture('forecast_email.eml').replace(b'salt-lake', b'logan')
        with self.assertRaisesRegex(f.RoseError, 'no Salt Lake forecast link'):
            f.parse_forecast_email(raw)


class WriteFiles(unittest.TestCase):
    def test_day_record_and_index(self):
        info = f.parse_forecast_email(fixture('forecast_email.eml'))
        rec = f.day_record(info, [4] * 16 + [2] * 8, '2026-11-22T15:00:00Z')
        self.assertEqual(set(rec), {'schema', 'center', 'zone', 'zone_name', 'date', 'sample', 'source',
                                    'source_url', 'issued_at', 'fetched_at', 'overall_danger_rose', 'problems'})
        self.assertIs(rec['sample'], False)
        with tempfile.TemporaryDirectory() as d:
            f.write_json(os.path.join(d, '2026-11-22.json'), rec)
            f.write_json(os.path.join(d, '2026-11-20.json'), rec)
            open(os.path.join(d, 'notes.json'), 'w').close()
            f.write_index(d, '2026-11-22T15:00:00Z')
            import json
            with open(os.path.join(d, 'index.json')) as fh:
                idx = json.load(fh)
            self.assertEqual(idx['dates'], ['2026-11-20', '2026-11-22'])
            self.assertEqual(idx['zone'], 'salt-lake')


if __name__ == '__main__':
    unittest.main()
