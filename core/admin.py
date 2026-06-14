from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from .models import Reason, SurveyResponse, Device


class ReasonResource(resources.ModelResource):
    class Meta:
        model = Reason
        fields = ('id', 'rating', 'text', 'is_active', 'order')


class SurveyResponseResource(resources.ModelResource):
    reason_text = fields.Field(attribute='reason', column_name='reason_text')
    device_name = fields.Field(attribute='device', column_name='device_name')

    class Meta:
        model = SurveyResponse
        fields = ('id', 'rating', 'reason_text', 'device_name', 'created_at')

    def dehydrate_reason_text(self, obj):
        return obj.reason.text if obj.reason else ''

    def dehydrate_device_name(self, obj):
        return str(obj.device) if obj.device else ''


@admin.register(Reason)
class ReasonAdmin(ImportExportModelAdmin):
    resource_class = ReasonResource
    list_display = ('text', 'rating', 'is_active', 'order')
    list_filter = ('rating', 'is_active')
    list_editable = ('is_active', 'order')
    search_fields = ('text',)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'name', 'hotline', 'is_active', 'last_seen')
    list_editable = ('is_active', 'hotline')
    search_fields = ('device_id', 'name')


@admin.register(SurveyResponse)
class SurveyResponseAdmin(ImportExportModelAdmin):
    resource_class = SurveyResponseResource
    list_display = ('rating', 'reason', 'device', 'created_at')
    list_filter = ('rating', 'device', 'created_at')
    readonly_fields = ('created_at',)
