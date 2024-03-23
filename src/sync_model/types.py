#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import datetime
from typing import TypedDict, Optional

from django.db.models import Model


class SyncResult(TypedDict):
    finished: bool
    count: int
    start: datetime.datetime
    end: datetime.datetime
    last_sync_model: Optional[Model]
