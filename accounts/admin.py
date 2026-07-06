from django.contrib import admin
from .models import (
    WorkerProfile,
    Service,
    CustomerProfile,
    Booking,
    Review,
    WorkerWarning,
    WorkerLocation,
    UserRole,
    AdminProfile,
    EmailOTP,
    SupportChat,
    SupportMessage,
)


@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "service_type", "pincode", "is_approved")
    list_filter = ("is_approved", "service_type")
    list_editable = ("is_approved",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "base_price", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


admin.site.register(CustomerProfile)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(WorkerWarning)
admin.site.register(WorkerLocation)
admin.site.register(UserRole)
admin.site.register(AdminProfile)
admin.site.register(EmailOTP)
admin.site.register(SupportChat)
admin.site.register(SupportMessage)