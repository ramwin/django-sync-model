# django-sync-model
a django reusable application to migrate data from source table to target table.


# Install
```
pip3 install django-sync-model
```

add `sync_model` to `INSTALLED_APPS` in settings.py


# Usage
for example you may has connected to a stock database provided by the broker.  
you want to save some filtered data to your own database to create foreignkey.  

1. create a sync task
```
from sync_model.models import (
        RawStockAction, StockAction,
        SyncTask,
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

here your sync_method should return a sync result
```

2. run sync task
```
python3 manage.py sync_model
```

# Features
* [x] support sync data from one database to another
* [x] incremental update
* [x] support non-cycle dependency
* [x] support filter
* [x] support custom sync size of each table
* [ ] support exclude filters
* [ ] support timeout parameter

# Release Notes
* 0.5.0
break change: `sync_function` should return `SyncResult`
