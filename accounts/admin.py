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


# ==============================
# WORKER PROFILE ADMIN
# ==============================

@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "service_type",
        "pincode",
        "is_approved",
        "is_blocked",
    )

    list_filter = (
        "service_type",
        "is_approved",
        "is_blocked",
    )

    search_fields = (
        "user__username",
        "phone",
        "pincode",
    )

    list_editable = (
        "is_approved",
        "is_blocked",
    )


# ==============================
# SERVICE ADMIN
# ==============================

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "base_price",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
    )


# ==============================
# CUSTOMER PROFILE
# ==============================

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "phone",
        "city",
        "pincode",
    )

    search_fields = (
        "user__username",
        "phone",
        "city",
    )


# ==============================
# BOOKING
# ==============================

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer",
        "worker",
        "service",
        "status",
        "payment_status",
        "booking_date",
    )

    list_filter = (
        "status",
        "payment_status",
        "payment_method",
    )

    search_fields = (
        "customer__user__username",
        "worker__user__username",
    )


# ==============================
# REVIEW
# ==============================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        "booking",
        "rating",
        "created_at",
    )


# ==============================
# OTHER MODELS
# ==============================

admin.site.register(WorkerWarning)
admin.site.register(WorkerLocation)
admin.site.register(UserRole)
admin.site.register(AdminProfile)
admin.site.register(EmailOTP)


# ==============================
# SUPPORT CHAT
# ==============================

@admin.register(SupportChat)
class SupportChatAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "chat_type",
        "created_at",
    )

    list_filter = (
        "chat_type",
    )

    search_fields = (
        "user__username",
    )


# ==============================
# SUPPORT MESSAGE
# ==============================

@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):

    list_display = (
        "chat",
        "sender",
        "is_seen",
        "created_at",
    )

    list_filter = (
        "is_seen",
    )

    search_fields = (
        "message",
        "sender__username",
    )