from django.contrib import admin
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin

from .models import Cleaner, CleanerAction, CleanerLog, Device, Reason, SurveyResponse


class ReasonResource(resources.ModelResource):
    class Meta:
        model = Reason
        fields = ("id", "rating", "text", "is_active", "order")


class SurveyResponseResource(resources.ModelResource):
    reason_text = fields.Field(attribute="reason", column_name="reason_text")
    device_name = fields.Field(attribute="device", column_name="device_name")

    class Meta:
        model = SurveyResponse
        fields = ("id", "rating", "reason_text", "device_name", "created_at")

    def dehydrate_reason_text(self, obj):
        return obj.reason.text if obj.reason else ""

    def dehydrate_device_name(self, obj):
        return str(obj.device) if obj.device else ""


@admin.register(Reason)
class ReasonAdmin(ImportExportModelAdmin):
    resource_class = ReasonResource
    list_display = ("text", "rating", "is_active", "order")
    list_filter = ("rating", "is_active")
    list_editable = ("is_active", "order")
    search_fields = ("text",)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("device_id", "name", "hotline", "is_active", "last_seen")
    list_editable = ("is_active", "hotline")
    search_fields = ("device_id", "name")


@admin.register(SurveyResponse)
class SurveyResponseAdmin(ImportExportModelAdmin):
    resource_class = SurveyResponseResource
    list_display = ("rating", "reason", "device", "created_at")
    list_filter = ("rating", "device", "created_at")
    readonly_fields = ("created_at",)


@admin.register(CleanerAction)
class CleanerActionAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "order")
    list_editable = ("is_active", "order")


@admin.register(Cleaner)
class CleanerAdmin(admin.ModelAdmin):
    list_display = ("cleaner_id", "name", "is_active")
    list_editable = ("is_active",)
    search_fields = ("cleaner_id", "name")


@admin.register(CleanerLog)
class CleanerLogAdmin(ImportExportModelAdmin):
    list_display = ("cleaner", "device", "actions_display", "logged_at")
    list_filter = ("device", "cleaner", "logged_at")
    readonly_fields = ("logged_at",)
    filter_horizontal = ("actions",)
