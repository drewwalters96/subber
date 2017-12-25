import datetime
import logging
import math
import time

logger = logging.getLogger(__name__)


def utc_epoch_sec_to_years(sec):
    """Converts seconds from UTC epoch to elapsed time from current time"""

    logging.debug('Converting {} seconds from UTC epoch to years to '
                  'date'.format(sec))

    try:
        # Elapsed seconds from time
        elapsed_sec = time.time() - sec

        # Elapsed days from time
        days = datetime.timedelta(seconds=elapsed_sec).days

        # Reddit rounds years this way on their website
        # Subber does the same for consistency
        return math.floor(days/365)

    except Exception:
        logging.error('Unable to calculate years to date from UTC epoch '
                      'timestamp')
