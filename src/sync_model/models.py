"""
sync model
"""


from django.db import models
from django.contrib.contenttypes.models import ContentType


def default_order_by():
    """
    by default, sync the table according to pk field
    """
    return ["pk"]


class SyncTask(models.Model):
    """
    A synctask means you need to handle all the data from source model to target model
    """
    source = models.ForeignKey(ContentType, related_name="+", on_delete=models.DO_NOTHING)
    target = models.ForeignKey(ContentType, related_name="+", on_delete=models.DO_NOTHING)
    sync_method = models.TextField()
    batch_size = models.IntegerField(default=100)
    order_by = models.JSONField(default=default_order_by)
    last_sync = models.JSONField(default=dict)
    dependencies = models.ManyToManyField(
            "self",
    )
    filter_by = models.JSONField(default=dict)


class RawStockAction(models.Model):
    """
    e.g.
        In a stock system, many user will
            1. buy a stock,
            2. sell a stock
            3. cancel some action
        to support super fast tps, we will build the foreignkey later.  
        build the StockAction table from RawStockAction.
        We only sync the
            * action_type in buy and sell,
            * order by update_datetime and -sender
    """
    ACTION_TYPE_CHOICES = (
            ("buy", "buy"),
            ("sell", "sell"),
            ("cancel", "cancel"),
    )
    sender = models.CharField(max_length=32)
    action_type = models.CharField(
            choices=ACTION_TYPE_CHOICES,
            max_length=10,
    )
    update_datetime = models.DateTimeField()
    canceled = models.BooleanField()
    stock_number = models.CharField(max_length=32)


class StockAction(models.Model):
    """
    inner StockAction with foreignkey
    """
    create_datetime = models.DateTimeField(auto_now_add=True)
