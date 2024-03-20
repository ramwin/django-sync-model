#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


"""
useful utils to sync model instance
"""


import datetime
import warnings

from typing import NewType, List

from django.db.models import Q, Model

from .models import (
        SyncTask, StockAction
        )


OrderBy = NewType("OrderBy", List[str])


def get_queryset(sync_task: SyncTask):
    """get filtered and ordered queryset from sync_task"""
    source_model = sync_task.source.model_class()
    queryset = source_model.objects.using(sync_task.source_db).filter(
            **sync_task.filter_by
    ).order_by(*sync_task.order_by)
    filter_q = get_Q(sync_task.order_by, sync_task.last_sync)
    return queryset.filter(filter_q)


def get_value(instance: Model, order_by: OrderBy, datetime2str: bool) -> dict:
    """
    get last sync value from instance according order_by
    e.g.
        >>> get_value(User, order_by: ["id", "-username"])
        {"id": 888, "-username": "alice"}
    """
    result = {}
    for key in order_by:
        if key.startswith("-"):
            result[key] = getattr(instance, key[1:])
        else:
            result[key] = getattr(instance, key)
        if datetime2str and isinstance(result[key], datetime.datetime):
            result[key] = result[key].isoformat()
    return result


def get_Q(order_by: OrderBy, last_sync: dict) -> Q:  # pylint: disable=invalid-name
    """
    get django Q filter from order_by and last_sync data
    """
    if not last_sync:
        return Q()
    if not order_by:
        warnings.warn("empty order by will cause sync always sync from the first model ")
        return Q()
    greater_keys = order_by.copy()
    first_key = greater_keys.pop(0)
    if first_key.startswith("-"):
        direction = "lt"
    else:
        direction = "gt"
    result = Q(**{
        f"{first_key.strip('-')}__{direction}": last_sync[first_key]
    })
    same_dict = {
        first_key.strip("-"): last_sync[first_key]
    }
    while greater_keys:
        greater_key = greater_keys.pop(0)
        if greater_key.startswith("-"):
            direction = "lt"
        else:
            direction = "gt"
        greater_dict = {
            f"{greater_key.strip('-')}__{direction}": last_sync[greater_key]
        }
        result |= Q(
            **same_dict,
            **greater_dict,
        )
        same_dict[greater_key.strip("-")] = last_sync[greater_key]
    result |= Q(**same_dict)
    return result


def sync_raw_stock_action(queryset,
                          target_model: StockAction,
                          sync_task: SyncTask):  # pylint: disable=unused-argument
    """
    only sync the id field
    """
    for raw_stockaction in queryset:
        target_model.objects.get_or_create(
                id=raw_stockaction.id,
        )
