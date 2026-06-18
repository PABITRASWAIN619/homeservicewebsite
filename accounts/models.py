from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random


# ==========================================
# CUSTOMER PROFILE
# ==========================================
from django.db import models
from django.contrib.auth.models import User


class CustomerProfile(models.Model):
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    phone = models.CharField(max_length=15)

    pincode = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    latitude = models.FloatField(
        null=True,
        blank=True
    )

    longitude = models.FloatField(
        null=True,
        blank=True
    )

    last_seen = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.user.username
# ==========================================
# WORKER PROFILE
# ==========================================
class WorkerProfile(models.Model):
    
    SERVICE_CHOICES = [
        ('electrician', 'Electrician'),
        ('plumber', 'Plumber'),
        ('ac_repair', 'AC Repair'),
        ('mobile_repair', 'Mobile Repair'),
        ('carpenter', 'Carpenter'),
        ('painter', 'Painter'),
        ('cleaning_service', 'Cleaning Service'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)

    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField(null=True, blank=True)

    service_type = models.CharField(
        max_length=50,
        choices=SERVICE_CHOICES
    )

    address = models.TextField()

    location = models.CharField(max_length=255, blank=True, null=True)

    pincode = models.CharField(max_length=10, blank=True, null=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    experience = models.CharField(max_length=50)

    is_approved = models.BooleanField(default=False)

    face_image = models.ImageField(upload_to="faces/", null=True, blank=True)
    aadhaar_image = models.ImageField(upload_to="aadhaar/", null=True, blank=True)
    pan_image = models.ImageField(upload_to="pan/", null=True, blank=True)

    profile_image = models.ImageField(
        upload_to="worker_profiles/",
        default="worker_profiles/default.png",
        null=True,
        blank=True
    )

    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.service_type})"

# ==========================================
# USER ROLE
# ==========================================
class UserRole(models.Model):

    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('worker', 'Worker'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# ==========================================
# SERVICE
# ==========================================
class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


# ==========================================
# BOOKING
# ==========================================
import random
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# =========================
# BOOKING MODEL
# =========================
class Booking(models.Model):

    # =========================
    # STATUS FLOW
    # =========================
    STATUS_CHOICES = [
        ('Pending', 'Pending'),                 # Booking created
        ('Assigned', 'Assigned'),               # Admin assigned worker
        ('Accepted', 'Accepted'),               # Worker accepted job
        ('On The Way', 'On The Way'),           # Worker traveling
        ('Working', 'Working'),                 # Work started
        ('Completed', 'Completed'),             # Work finished
        ('Rejected', 'Rejected'),               # Worker rejected
        ('Cancelled', 'Cancelled'),             # Cancelled
    ]

    # =========================
    # PAYMENT
    # =========================
    PAYMENT_STATUS = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ]

    PAYMENT_METHOD = [
        ('Cash', 'Cash'),
        ('Online', 'Online'),
        ('Not Selected', 'Not Selected'),
    ]

    # =========================
    # RELATIONS
    # =========================
    customer = models.ForeignKey(
        "CustomerProfile",
        on_delete=models.CASCADE
    )

    worker = models.ForeignKey(
        "WorkerProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_jobs"
    )

    rejected_by = models.ForeignKey(
        "WorkerProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rejected_jobs"
    )

    service = models.ForeignKey(
        "Service",
        on_delete=models.CASCADE
    )

    # =========================
    # BASIC INFO
    # =========================
    address = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    booking_date = models.DateTimeField(auto_now_add=True)

    # =========================
    # STATUS
    # =========================
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    is_accepted = models.BooleanField(default=False)

    # =========================
    # PAYMENT
    # =========================
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD,
        default='Not Selected'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='Pending'
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # =========================
    # OTP SYSTEM
    # =========================
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_verified = models.BooleanField(default=False)
    otp_created_time = models.DateTimeField(null=True, blank=True)

    # =========================
    # METHODS
    # =========================
    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.otp_created_time = timezone.now()
        self.save()

    @property
    def can_resend_otp(self):
        if not self.otp_created_time:
            return True

        return timezone.now() >= (
            self.otp_created_time + timedelta(minutes=5)
        )

    @property
    def needs_payment(self):
        return (
            self.payment_method == "Cash"
            and self.payment_status == "Pending"
        )

    @property
    def can_verify_otp(self):
        return (
            self.payment_status == "Paid"
            and not self.otp_verified
            and self.status == "Working"
        )

    def __str__(self):
        return f"{self.customer.user.username} - {self.service.name}"


# =========================
# WORKER LIVE LOCATION
# =========================
class WorkerLocation(models.Model):

    worker = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    lat = models.FloatField()
    lng = models.FloatField()

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.worker.username




# ==========================================
# REVIEW
# ==========================================

class Review(models.Model):
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField(default=5)

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for Booking #{self.booking.id}"
    from django.db import models
from django.contrib.auth.models import User
import random
from datetime import timedelta
from django.utils import timezone

class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))
    # ==========================================
# support and chat
# ==========================================
# ==========================================
# SUPPORT CHAT
# ==========================================
from django.db import models
from django.contrib.auth.models import User


class SupportChat(models.Model):
    CHAT_TYPES = (
        ("customer", "Customer"),
        ("worker", "Worker"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_type = models.CharField(max_length=20, choices=CHAT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.chat_type}"


class SupportMessage(models.Model):
    chat = models.ForeignKey(
        SupportChat,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE)

    message = models.TextField(blank=True, null=True)

    image = models.ImageField(upload_to="support/images/", blank=True, null=True)
    file = models.FileField(upload_to="support/files/", blank=True, null=True)

    is_seen = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}"
    