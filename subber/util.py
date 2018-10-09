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

import time
import logging

logger = logging.getLogger(__name__)


def utc_epoch_sec_to_years(sec):
    """Converts seconds from UTC epoch to elapsed time from current time"""

    logging.debug('Converting {} seconds from UTC epoch to years to '
                  'date'.format(sec))

    time_diff = int(time.time()) - sec
    return int(time_diff / 60 / 60 / 24 // 365.25)
