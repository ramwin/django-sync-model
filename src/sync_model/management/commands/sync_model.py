#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


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
                next_tasks.add()

    @staticmethod
    def run_sync_task(sync_task: SyncTask) -> SyncResult:
        queryset = get_queryset(sync_task)[0:sync_task.batch_size]
        module, function = sync_task.sync_method.rsplit(".")
        sync_function = getattr(
            importlib.import_module(module),
            function
        )
        sync_function(queryset, sync_task.target.model_class(), sync_task)
        last_value = get_value(queryset[sync_task.batch_size], sync_task.order_by)
        sync_task.last_sync = last_value
        sync_task.save()
