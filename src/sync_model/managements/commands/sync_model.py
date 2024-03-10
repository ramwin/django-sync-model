#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import importlib
import logging

from django.core.management import BaesCommand

from sync_model.models import SyncTask
from sync_model.types import SyncResult
from sync_model.utils import get_queryset


LOGGER = logging.getLogger(__name__)


class Command(BaesCommand):

    def handle(self, *args, **kwargs):
        LOGGER.info("start run sync model")
        synced_tasks = set()
        finished_tasks = set()
        next_tasks = set(SyncTask.objects.filter(dependencies=None))
        while next_tasks:
            sync_task = next_tasks.pop()
            result = self.run_sync_task(sync_task)
            if result["finished"] is True:
                finished_tasks.add(sync_task)
                next_tasks.add(
                    set(SyncTask.objects.filter(
                        dependencies=sync_task
                    )) - finished_tasks,
                )

    @classmethod
    def run_sync_task(sync_task: SyncTask) -> SyncResult:
        queryset = get_queryset(sync_task)[0:sync.batch_size]
        module, function = sync_task.sync_method.rsplit(".")
        getattr(
            importlib.import_module(module),
            function
        )(queryset)
        last_value = get_value(queryset[sync.batch_size], sync_task.order_by)
        sync_task.last_sync = last_value
        sync_task.save()
