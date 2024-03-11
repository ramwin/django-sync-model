#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


"""
handle sync model task
"""


import importlib
import logging

from django.core.management import BaseCommand

from sync_model.models import SyncTask
from sync_model.types import SyncResult
from sync_model.utils import (
        get_queryset, get_value,
        )


LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """run sync model task"""

    def handle(self, *args, **kwargs):  # pylint: disable=unused-argument
        LOGGER.info("start run sync model")
        synced_tasks = set()
        finished_tasks = set()
        next_tasks = set(SyncTask.objects.filter(dependencies=None))
        while next_tasks:
            sync_task = next_tasks.pop()
            result = self.run_sync_task(sync_task)
            synced_tasks.add(sync_task)
            if result["finished"] is True:
                finished_tasks.add(sync_task)
                for nomination_task in SyncTask.objects.filter(
                        dependencies=sync_task
                        ):
                    if nomination_task in synced_tasks:
                        continue
                    if set(nomination_task.dependencies.all()) - finished_tasks:
                        continue
                    next_tasks.add(nomination_task)

    @staticmethod
    def run_sync_task(sync_task: SyncTask) -> SyncResult:
        """
        sync a single SyncTask
        """
        result = {}
        queryset = get_queryset(sync_task)
        module, function = sync_task.sync_method.rsplit(".", 1)
        sync_function = getattr(
            importlib.import_module(module),
            function
        )
        if queryset.count() > sync_task.batch_size:
            last_sync_model = queryset[sync_task.batch_size]
            result["finished"] = False
        else:
            last_sync_model = queryset.last()
            result["finished"] = True
        sync_function(queryset[0:sync_task.batch_size], sync_task.target.model_class(), sync_task)
        last_value = get_value(last_sync_model, sync_task.order_by, datetime2str=True)
        sync_task.last_sync = last_value
        sync_task.save()
        return result
