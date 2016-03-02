#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from datetime import datetime

EPOCH = datetime(1970, 1, 1)


def to_unix_timestamp(dt):
    return int(time.mktime(dt.timetuple()))
