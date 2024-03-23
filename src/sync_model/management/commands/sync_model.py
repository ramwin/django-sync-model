#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


"""
handle sync model task
"""


import importlib
import logging

from django.core.management import BaseCommand

from sync_model.exceptions import StepTooSmallException
from sync_model.models import SyncTask
from sync_model.types import SyncResult
from sync_model.utils import (
        get_queryset, get_value,
        )


LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """run sync model task"""

    def add_arguments(self, parser):
        parser.add_argument("--name", type=str)

    def handle(self, *args, **kwargs):  # pylint: disable=unused-argument
        if kwargs.get("name"):
            self.run_sync_task(
                    SyncTask.objects.get(name=kwargs["name"])
            )
            return
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

        previous version: the queryset.count() will be very slow, so I require the sync_method to return a syncresult

        ```python
        if queryset.count() > sync_task.batch_size:
            last_sync_model = queryset[sync_task.batch_size - 1]
            result["finished"] = False
        else:
            last_sync_model = queryset.last()
            result["finished"] = True
        sync_function(queryset[0:sync_task.batch_size], sync_task.target.model_class(), sync_task)
        last_value = get_value(last_sync_model, sync_task.order_by, datetime2str=True)
        if result["finished"] is False and sync_task.last_sync == last_value:
        ```

        """
        LOGGER.info("start sync: %s", sync_task)
        queryset = get_queryset(sync_task)
        module, function = sync_task.sync_method.rsplit(".", 1)
        sync_function = getattr(
            importlib.import_module(module),
            function
        )
        LOGGER.debug("sync_function realized")
        sync_result: SyncResult = sync_function(
                queryset[0:sync_task.batch_size],
                sync_task.target.model_class(),
                sync_task)
        if sync_result["last_sync_model"] is None:
            if sync_result["count"] == 0:
                LOGGER.info("Origin model has deleted the last model")
                LOGGER.info("%s finished %s, last_sync: %s",
                            sync_task, sync_result, sync_task.last_sync)
                return sync_result
            raise ValueError("sync count is not None, but the last_sync_model is empty")
        last_value = get_value(sync_result["last_sync_model"],
                               sync_task.order_by,
                               datetime2str=True)
        if sync_result["finished"] is False and sync_task.last_sync == last_value:
            raise StepTooSmallException
        sync_task.last_sync = last_value
        sync_task.save()
        LOGGER.info("%s finished %s, last_sync: %s",
                    sync_task, sync_result, sync_task.last_sync)
        return sync_result
