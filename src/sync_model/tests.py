import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from sync_model.models import (
        RawStockAction, StockAction,
        SyncTask,
)



class Test(TestCase):

    def test(self):
        now = timezone.now()
        second_stock = RawStockAction.objects.create(
                sender="charlie",
                action_type="buy",
                update_datetime=now,
                canceled=True,
                stock_number="LUCK",
        )
        fourth_stock = RawStockAction.objects.create(
                sender="alice",
                action_type="buy",
                update_datetime=now,
                canceled=False,
                stock_number="LUCK",
        )
        first_stock = RawStockAction.objects.create(
                sender="bob",
                action_type="sell",
                update_datetime=now-datetime.timedelta(days=1),
                canceled=False,
                stock_number="LUCK",
        )
        third_stock = RawStockAction.objects.create(
                sender="bob",
                action_type="buy",
                update_datetime=now,
                canceled=False,
                stock_number="LUCK",
        )
        SyncTask.objects.create(
                source=ContentType.objects.get_for_model(RawStockAction),
                target=ContentType.objects.get_for_model(StockAction),
                sync_method="sync_model.utils.sync_raw_stock_action",
                batch_size=2,
                order_by=["update_datetime", "-sender"],
                filter_by={
                    "canceled": False,
                }
        )
        call_command("sync_model")
        self.assertEqual(
                StockAction.objects.count(),
                2,
        )
        self.assertEqual(
                StockAction.objects.order_by("create_datetime").first().id,
                first_stock.id,
        )
        self.assertEqual(
                StockAction.objects.order_by("create_datetime").last().id,
                third_stock.id,
        )
        call_command("sync_model")
        self.assertEqual(
                StockAction.objects.count(),
                3,
        )
        call_command("sync_model")
        self.assertEqual(
                RawStockAction.objects.count() - 1,
                StockAction.objects.count(),
        )
