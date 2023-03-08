from datetime import datetime
from datetime import timedelta
from datetime import timezone
from ntfs.mft.config import *


def time_to_dt(ft):
    (s, ns100) = divmod(ft - EPOCH_AS_FILETIME, HUNDREDS_OF_NANOSECONDS)
    dt = datetime.fromtimestamp(s, tz=timezone.utc) + timedelta(hours=7)
    return dt
