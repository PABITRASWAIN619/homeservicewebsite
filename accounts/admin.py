from django.contrib import admin
from .models import WorkerProfile

@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_type', 'pincode', 'is_approved')
    list_filter = ('is_approved', 'service_type')
    list_editable = ('is_approved',)