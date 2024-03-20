from django.contrib import admin

# Register your models here.

from .models import SyncTask


@admin.register(SyncTask)
class SyncTaskAdmin(admin.ModelAdmin):
    list_display = ["name", "source", "target", "sync_method", "batch_size", "order_by", "last_sync", "filter_by"]
