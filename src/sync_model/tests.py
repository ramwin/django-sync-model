import datetime

from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from sync_model.exceptions import StepTooSmallException
from sync_model.models import (
        RawStockAction, StockAction,
        SyncTask,
)
from sync_model.utils import get_value



class Test(TestCase):

    def test(self):
        now = timezone.make_aware(
                datetime.datetime(2024, 1, 1, 2, 3, 4)
        )
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
                stock_number="LUCK_PRE",
        )
        third_stock = RawStockAction.objects.create(
                sender="bob",
                action_type="buy",
                update_datetime=now,
                canceled=False,
                stock_number="LUCK",
        )
        sync_task = SyncTask.objects.create(
                source=ContentType.objects.get_for_model(RawStockAction),
                target=ContentType.objects.get_for_model(StockAction),
                sync_method="sync_model.utils.sync_raw_stock_action",
                batch_size=1,
                order_by=["update_datetime", "-sender"],
                filter_by={
                    "canceled": False,
                }
        )
        call_command("sync_model")
        sync_task.refresh_from_db()
        first_sync_stock = StockAction.objects.get()
        self.assertEqual(
                first_sync_stock.update_datetime,
                first_stock.update_datetime,
        )
        self.assertEqual(
                first_sync_stock.update_datetime,
                first_stock.update_datetime,
        )
        self.assertEqual(
                first_sync_stock.stock_number,
                first_stock.stock_number,
        )
        last_sync_update_datetime = datetime.datetime.fromisoformat(
            sync_task.last_sync["update_datetime"],
        )
        self.assertEqual(
                last_sync_update_datetime,
                first_stock.update_datetime,
        )
        self.assertEqual(
                StockAction.objects.count(),
                1,
        )
        with self.assertRaises(StepTooSmallException):
            call_command("sync_model")
        sync_task.batch_size = 2
        sync_task.last_sync = {}
        sync_task.save()
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

    def test_get_value(self):
        now = timezone.make_aware(
                datetime.datetime(2024, 1, 1, 2, 3, 4)
        )
        first_stock = RawStockAction.objects.create(
                sender="bob",
                action_type="sell",
                update_datetime=now-datetime.timedelta(days=1),
                canceled=False,
                stock_number="LUCK_PRE",
        )
        value = get_value(
                first_stock,
                ["update_datetime"], datetime2str=False)
        self.assertEqual(
                value["update_datetime"],
                first_stock.update_datetime,
        )
        value2 = get_value(
                first_stock,
                ["update_datetime"], datetime2str=True)
        self.assertEqual(
                value2["update_datetime"],
                first_stock.update_datetime.isoformat(),
        )
