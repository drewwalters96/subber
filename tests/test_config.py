# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import unittest

from testfixtures import log_capture

from subber import config

TESTDIR = os.path.dirname(os.path.abspath(__file__))
TESTCONF = os.path.join(TESTDIR, 'config_files')


class TestConfig(unittest.TestCase):

    @log_capture()
    def test_good_configuration(self, capture):
        cfg = os.path.join(TESTCONF, 'good.cfg')
        res = config.get_config(cfg)
        self.assertEqual("ID", res["id"])

    @log_capture()
    def test_invalid_configuration(self, capture):
        cfg = os.path.join(TESTCONF, 'non_existing.conf')
        self.assertRaises(RuntimeError, config.get_config, cfg)
        rec = capture.records[0]
        self.assertEqual("CRITICAL", rec.levelname)
        self.assertTrue(rec.msg.startswith("Config file not found"))

    @log_capture()
    def test_missing_sections(self, capture):
        cfg = os.path.join(TESTCONF, 'missing_section.cfg')
        self.assertRaises(RuntimeError, config.get_config, cfg)
        rec = capture.records[0]
        self.assertEqual("CRITICAL", rec.levelname)
        self.assertTrue(rec.msg.startswith("Missing header:"))

    @log_capture()
    def test_missing_field(self, capture):
        cfg = os.path.join(TESTCONF, 'missing_field.cfg')
        self.assertRaises(RuntimeError, config.get_config, cfg)
        rec = capture.records[0]
        self.assertEqual("CRITICAL", rec.levelname)
        self.assertTrue(rec.msg.startswith("Validation error:"))
