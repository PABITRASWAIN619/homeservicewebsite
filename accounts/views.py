from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import WorkerSignupForm, CustomerSignupForm
import random
from .models import (
    WorkerProfile,
    CustomerProfile,
    UserRole,
    Booking,
    Service
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import WorkerProfile


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import WorkerProfile


@login_required
def worker_profile(request):
    worker = WorkerProfile.objects.filter(user=request.user).first()

    if not worker:
        return render(request, "worker/no_profile.html")

    return render(
        request,
        "worker/worker_profile.html",
        {
            "worker": worker,
        },
    )
# ==========================================
# HOME
# ==========================================

def home(request):
    return render(request, "index.html")


# ==========================================
# WORKER SIGNUP
# ==========================================
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import WorkerProfile, UserRole


# =========================
# STEP 1 - BASIC INFO
# =========================
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import WorkerProfile, UserRole


# =========================
# STEP 1 - BASIC INFO
# =========================
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import WorkerStep1Form, WorkerStep2Form, WorkerStep3Form, WorkerStep4Form
from .models import WorkerProfile, UserRole
import base64
from django.core.files.base import ContentFile

# =========================
# STEP 1
# =========================
def worker_signup_step1(request):
    
    if request.method == "POST":

        email = request.POST.get("email")
        phone = request.POST.get("phone")
        dob = request.POST.get("date_of_birth")

        # SAVE SESSION
        request.session["email"] = email
        request.session["phone"] = phone
        request.session["date_of_birth"] = dob

        return redirect("worker_signup_step2")  # ✔ THIS WILL WORK

    return render(request, "worker_signup_step1.html")

# =========================
# STEP 2
# =========================
def worker_signup_step2(request):
    if request.method == "POST":

        service_type = request.POST.get("service_type")
        address = request.POST.get("address")
        pincode = request.POST.get("pincode")
        experience = request.POST.get("experience")

        print("SERVICE TYPE:", service_type)  # DEBUG

        if not service_type:
            messages.error(request, "Select service type")
            return redirect("worker_signup_step2")

        request.session["service_type"] = service_type
        request.session["address"] = address
        request.session["pincode"] = pincode
        request.session["experience"] = experience

        return redirect("worker_signup_step3")

    return render(request, "worker_signup_step2.html")


# =========================
# STEP 3 (FACE)
# =========================
import base64
import uuid
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from django.contrib import messages

def worker_signup_step3(request):
    if request.method == "POST":
        face_data = request.POST.get("face_image")

        if not face_data:
            messages.error(request, "Please capture your face image before continuing.")
            return redirect("worker_signup_step3")

        try:
            # The image comes as: "data:image/png;base64,iVBORw0KGgoAAAANSU..."
            # We split the header away to capture raw base64 context chunks
            format, imgstr = face_data.split(';base64,')
            ext = format.split('/')[-1] # Grabs 'png' or 'jpeg'
            
            # Decode string array into pure system binary format
            decoded_image = base64.b64decode(imgstr)
            
            # Generate a globally unique, randomized cryptographical file name token string
            file_name = f"worker_face_{uuid.uuid4().hex[:10]}.{ext}"
            
            # Convert raw system binaries into a saveable Django ContentFile payload object wrapper
            file_data = ContentFile(decoded_image, name=file_name)
            
            # Stash base64 string directly inside system state session context 
            # We will pull it out and bind it to the Worker model file inside Step 4 view logic!
            request.session["face_image_base64"] = face_data
            request.session["face_image_name"] = file_name
            
            return redirect("worker_signup_step4")
            
        except Exception as e:
            messages.error(request, "Subsystem failed to decode asset payload telemetry matrix.")
            return redirect("worker_signup_step3")

    return render(request, "worker_signup_step3.html")




import base64
import uuid

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

from .models import WorkerProfile, UserRole


def worker_signup_step4(request):
    email = request.session.get("email")
    phone = request.session.get("phone")
    face_image_base64 = request.session.get("face_image_base64")
    face_image_name = request.session.get("face_image_name")

    if not email:
        return redirect("worker_signup_step1")

    if request.method == "POST":

        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        aadhaar = request.FILES.get("aadhaar_image")
        pan = request.FILES.get("pan_image")

        # -------------------------
        # VALIDATION
        # -------------------------
        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect("worker_signup_step4")

        if User.objects.filter(username=email).exists():
            messages.error(request, "User already exists.")
            return redirect("login")

        if not aadhaar or not pan:
            messages.error(request, "Please upload Aadhaar and PAN.")
            return redirect("worker_signup_step4")

        try:
            # -------------------------
            # FACE IMAGE
            # -------------------------
            face_file = None

            if face_image_base64:
                if ";base64," in face_image_base64:
                    _, imgstr = face_image_base64.split(";base64,")
                else:
                    imgstr = face_image_base64

                face_file = ContentFile(
                    base64.b64decode(imgstr),
                    name=face_image_name or f"{uuid.uuid4().hex}.png"
                )

            # -------------------------
            # CREATE USER
            # -------------------------
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
            )

            user.is_active = True
            user.save()

            # -------------------------
            # CREATE ROLE
            # -------------------------
            UserRole.objects.create(
                user=user,
                role="worker"
            )

            # -------------------------
            # CREATE WORKER PROFILE
            # -------------------------
            worker = WorkerProfile.objects.create(
                user=user,
                phone=phone,
                date_of_birth=request.session.get("date_of_birth"),
                service_type=request.session.get("service_type"),
                address=request.session.get("address"),
                pincode=request.session.get("pincode"),
                experience=request.session.get("experience"),

                face_image=face_file,
                aadhaar_image=aadhaar,
                pan_image=pan,

                is_approved=False
            )

            # -------------------------
            # SAVE WORKER ID IN SESSION
            # -------------------------
            request.session["worker_id"] = worker.id

            # Optional: clear signup data
            for key in [
                "email",
                "phone",
                "face_image_base64",
                "face_image_name",
                "date_of_birth",
                "service_type",
                "address",
                "pincode",
                "experience",
            ]:
                request.session.pop(key, None)

            # -------------------------
            # REDIRECT TO PENDING PAGE
            # -------------------------
            return redirect("worker_signup_pending")

        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect("worker_signup_step4")

    return render(
        request,
        "worker_signup_step4.html",
        {
            "email": email
        }
    )
# =========================
# PENDING PAGE
# =========================
from django.shortcuts import render, redirect
from .models import WorkerProfile


def worker_signup_pending(request):
    # Get worker id from session
    worker_id = request.session.get("worker_id")

    if not worker_id:
        return redirect("worker_signup_step1")

    try:
        worker = WorkerProfile.objects.get(id=worker_id)
    except WorkerProfile.DoesNotExist:
        return redirect("worker_signup_step1")

    # If admin approved the account
    if worker.is_approved:
        # Remove session
        request.session.pop("worker_id", None)

        # Redirect to login
        return redirect("login")

    # Show waiting page
    return render(
        request,
        "worker_signup_pending.html",
        {
            "worker": worker
        }
    )
# ==========================================
# CUSTOMER SIGNUP
# ==========================================
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User

from .models import CustomerProfile, UserRole


def customer_signup(request):

    if request.method == "POST":

        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        pincode = request.POST.get("pincode")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # -----------------------------
        # Validation
        # -----------------------------
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("customer_signup")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("customer_signup")

        try:

            # -----------------------------
            # Create User
            # -----------------------------
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password1,
                first_name=full_name
            )

            # -----------------------------
            # Update Existing CustomerProfile
            # (Created automatically by signals.py)
            # -----------------------------
            profile = CustomerProfile.objects.get(user=user)

            profile.phone = phone
            profile.pincode = pincode

            profile.save()

            # -----------------------------
            # Create User Role
            # -----------------------------
            UserRole.objects.get_or_create(
                user=user,
                defaults={
                    "role": "customer"
                }
            )

            messages.success(
                request,
                "Customer account created successfully."
            )

            return render(
                request,
                "customer_signup.html",
                {
                    "redirect_to_login": True
                }
            )

        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect("customer_signup")

    return render(request, "customer_signup.html")
# ==========================================
# LOGIN
# ==========================================


from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import UserRole, WorkerProfile


def user_login(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        # If someone is already logged in in this browser
        if request.user.is_authenticated:

            if request.user.email != email:

                old_email = request.user.email

                logout(request)

                messages.warning(
                    request,
                    f"Previous account ({old_email}) was logged out."
                )

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:

            login(request, user)

            # ADMIN
            if user.is_superuser:
                return redirect("admin_dashboard")

            # ROLE FETCH SAFELY
            role = UserRole.objects.filter(user=user).first()

            if not role:
                messages.error(
                    request,
                    "No role assigned. Contact admin."
                )
                logout(request)
                return redirect("login")

            # WORKER FLOW
            if role.role == "worker":

                profile = WorkerProfile.objects.filter(
                    user=user
                ).first()

                if not profile:
                    messages.error(
                        request,
                        "Worker profile missing"
                    )
                    logout(request)
                    return redirect("login")

                if not profile.is_approved:
                    messages.error(
                        request,
                        "Not approved yet"
                    )
                    logout(request)
                    return redirect("login")

                return redirect("worker_dashboard")

            # CUSTOMER FLOW
            if role.role == "customer":
                return redirect("customer_dashboard")

            # UNKNOWN ROLE
            messages.error(
                request,
                "Invalid role assigned"
            )
            logout(request)
            return redirect("login")

        messages.error(
            request,
            "Invalid email or password"
        )

    return render(
        request,
        "login.html"
    )



from django.contrib.auth import logout
from django.shortcuts import redirect

def user_logout(request):
    logout(request)
    return redirect("login")
# ==========================================
# ADMIN DASHBOARD
# ==========================================
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import (
    WorkerProfile,
    CustomerProfile,
    Booking
)

# ==========================================
# ADMIN DASHBOARD
# ==========================================
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import WorkerProfile, CustomerProfile, Booking, AdminProfile

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect("login")

    # Get admin profile
    profile, created = AdminProfile.objects.get_or_create(user=request.user)

    context = {
        "profile": profile,

        "total_workers": WorkerProfile.objects.count(),
        "pending_workers": WorkerProfile.objects.filter(is_approved=False).count(),

        "total_customers": CustomerProfile.objects.count(),

        "total_bookings": Booking.objects.count(),
        "pending_bookings": Booking.objects.filter(status="Pending").count(),
        "completed_bookings": Booking.objects.filter(status="Completed").count(),
    }

    return render(request, "admin/dashboard.html", context)


# ==========================================
# WORKERS PAGE
# ==========================================
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import WorkerProfile

@login_required
def admin_workers(request):

    # Allow only admin
    if not request.user.is_superuser:
        return redirect("login")

    # Get search text from URL
    search = request.GET.get("search", "")

    # Get all workers
    workers = WorkerProfile.objects.select_related("user").all()

    # Search by username, first name, last name, email, or phone
    if search:
        workers = workers.filter(
            Q(user__username__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(phone__icontains=search)
        )

    context = {
        "workers": workers,
        "search": search,
    }

    return render(request, "admin/workers.html", context)


# ==========================================
# CUSTOMERS PAGE
# ==========================================
@login_required
def admin_customers(request):
    if not request.user.is_superuser:
        return redirect("login")

    customers = CustomerProfile.objects.all()

    return render(request, "admin/customers.html", {
        "customers": customers
    })
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import WorkerProfile


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
@login_required
def warn_worker(request, worker_id):
    # Only admin can warn workers
    if not request.user.is_superuser:
        return redirect("login")

    worker = get_object_or_404(WorkerProfile, id=worker_id)

    message = "Please follow the platform rules. This is an official warning from the administrator."

    # Update worker
    worker.warning_count += 1
    worker.warning_message = message
    worker.save()

    # Save warning history
    WorkerWarning.objects.create(
        worker=worker,
        message=message,
        warned_by=request.user,
    )

    messages.success(
        request,
        f"Warning sent to {worker.user.username}."
    )

    return redirect("admin_workers")
@login_required
def worker_blocked(request):

    worker = WorkerProfile.objects.filter(user=request.user).first()

    if not worker or not worker.is_blocked:
        return redirect("worker_dashboard")

    return render(request, "worker/blocked.html", {
        "worker": worker
    })


@login_required
def block_worker(request, worker_id):

    if not request.user.is_superuser:
        return redirect("login")

    worker = get_object_or_404(WorkerProfile, id=worker_id)

    # 🔴 BLOCK WORKER
    worker.is_blocked = True
    worker.warning_message = "🚫 Your account has been blocked by the administrator."
    worker.blocked_reason = "Blocked by Administrator"
    worker.blocked_at = timezone.now()
    worker.save()

    # 🔥 IMPORTANT: REMOVE ACTIVE JOBS
    Booking.objects.filter(
        worker=worker,
        status__in=["Assigned", "Accepted", "On The Way", "Working"]
    ).update(worker=None, status="Pending")

    messages.success(
        request,
        f"{worker.user.username} has been blocked successfully."
    )

    return redirect("admin_workers")
@login_required
def blocked_page(request):
    worker = request.user.workerprofile

    if not worker.is_blocked:
        return redirect("worker_dashboard")

    return render(request, "blocked.html", {
        "message": worker.warning_message,
        "reason": worker.blocked_reason,
    })


@login_required
def unblock_worker(request, worker_id):
    # Only admin can unblock workers
    if not request.user.is_superuser:
        return redirect("login")

    worker = get_object_or_404(WorkerProfile, id=worker_id)

    worker.is_blocked = False
    worker.warning_count = 0
    worker.warning_message = ""
    worker.blocked_reason = ""
    worker.blocked_at = None

    worker.save()

    messages.success(
        request,
        f"{worker.user.username} has been unblocked successfully."
    )

    return redirect("admin_workers")

# ==========================================
# BOOKINGS PAGE
# ==========================================
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def admin_bookings(request):

    if not request.user.is_superuser:
        return redirect("login")

    bookings = Booking.objects.select_related(
        "customer",
        "worker",
        "service"
    ).order_by("-booking_date")

    # Get status from URL
    status = request.GET.get("status")

    # Filter pending bookings
    if status == "pending":
        bookings = bookings.filter(status="Pending")   # Change "Pending" if your status value is different

    workers = WorkerProfile.objects.filter(
    is_approved=True,
    is_blocked=False
)

    return render(
        request,
        "admin/bookings.html",
        {
            "bookings": bookings,
            "workers": workers,
        }
    )
@login_required
def select_payment_method(request, booking_id, method):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.status != "Working":
        return redirect("assign_jobs")

    if method == "online":
        booking.payment_method = "Online"
        booking.payment_status = "Paid"

    elif method == "cash":
        booking.payment_method = "Cash"
        booking.payment_status = "Paid"

    booking.save()

    return redirect("assign_jobs")

# ==========================================
# PROFILE PAGE
# ==========================================
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import AdminProfile, WorkerProfile, CustomerProfile, Booking

def admin_profile(request):
    if not request.user.is_superuser:
        return redirect("login")

    # Get or create admin profile
    profile, created = AdminProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":

        request.user.username = request.POST.get("username")
        request.user.email = request.POST.get("email")
        request.user.first_name = request.POST.get("first_name")
        request.user.last_name = request.POST.get("last_name")

        if request.FILES.get("profile_image"):
            profile.image = request.FILES["profile_image"]

        request.user.save()
        profile.save()

        messages.success(request, "✅ Profile updated successfully!")

        return redirect("admin_profile")

    context = {
        "profile": profile,
        "total_workers": WorkerProfile.objects.count(),
        "total_customers": CustomerProfile.objects.count(),
        "total_bookings": Booking.objects.count(),
        "pending_bookings": Booking.objects.filter(status="Pending").count(),
    }

    return render(request, "admin/profile.html", context)


# ==========================================
# SUPPORT PAGE
# ==========================================
@login_required
def admin_support(request):

    if not request.user.is_superuser:
        return redirect("login")

    chats = SupportChat.objects.all().order_by("-created_at")

    return render(
        request,
        "admin/support_inbox.html",
        {
            "chats": chats
        }
    )


# ==========================================
# REAL TIME STATS API (AJAX)
# ==========================================
from django.http import JsonResponse

def admin_stats(request):
    return JsonResponse({
        "workers": WorkerProfile.objects.count(),
        "customers": CustomerProfile.objects.count(),
        "bookings": Booking.objects.count(),
        "pending": Booking.objects.filter(status="Pending").count(),
    })
from django.db.models import Count
from django.utils.timezone import now
from datetime import timedelta

def booking_chart_data(request):
    labels = []
    values = []

    # last 7 days data
    for i in range(6, -1, -1):
        day = now().date() - timedelta(days=i)
        count = Booking.objects.filter(created_at__date=day).count()

        labels.append(day.strftime("%d %b"))
        values.append(count)

    return JsonResponse({
        "labels": labels,
        "values": values,
    })
# ==========================================
# APPROVE WORKER
# ==========================================

@login_required
def approve_worker(request, worker_id):

    worker = get_object_or_404(
        WorkerProfile,
        id=worker_id
    )

    worker.is_approved = True
    worker.save()

    messages.success(
        request,
        "Worker approved successfully"
    )

    return redirect("admin_dashboard")


# ==========================================
# CUSTOMER DASHBOARD
# ==========================================

# ==========================================
# CUSTOMER DASHBOARD
# ==========================================

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from .models import (
    CustomerProfile,
    Booking,
    WorkerProfile
)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserRole, CustomerProfile, Booking, WorkerProfile

@login_required
def customer_dashboard(request):

    role = UserRole.objects.filter(user=request.user).first()

    # ❌ no role → logout/login
    if not role:
        return redirect("login")

    # ❌ NOT customer → send to worker dashboard (or login)
    if role.role != "customer":
        return redirect("worker_dashboard")

    customer = CustomerProfile.objects.filter(user=request.user).first()

    if not customer:
        return redirect("customer_signup")

    bookings = Booking.objects.filter(customer=customer).order_by("-id")

    return render(request, "customer/dashboard.html", {
        "customer": customer,
        "bookings": bookings,
        "total_bookings": bookings.count(),
        "completed_jobs": bookings.filter(status="Completed").count(),
        "pending_jobs": bookings.exclude(status="Completed").count(),
        "top_workers": WorkerProfile.objects.filter(is_approved=True).order_by("-last_seen")[:4],
        "latest_booking": bookings.first(),
    })

def role_based_redirect(request):

    role = UserRole.objects.filter(
        user=request.user
    ).first()

    if not role:
        return redirect("login")

    if role.role == "customer":
        return redirect("customer_dashboard")

    if role.role == "worker":
        return redirect("worker_dashboard")

    return redirect("login")
from django.shortcuts import render, get_object_or_404

@login_required
def worker_details(request, worker_id):

    worker = get_object_or_404(
        WorkerProfile,
        id=worker_id
    )

    return render(
        request,
        "customer/worker_details.html",
        {
            "worker": worker
        }
    )
# ==========================================
# BOOK SERVICE
# ==========================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Booking, Service, CustomerProfile

@login_required
def book_service(request):

    service_id = request.GET.get("service_id")

    if not service_id:
        messages.error(request, "Service ID missing")
        return redirect("services")

    service = get_object_or_404(Service, id=service_id)

    if request.method == "POST":

        customer, created = CustomerProfile.objects.get_or_create(
            user=request.user
        )

        latitude = request.POST.get("latitude") or None
        longitude = request.POST.get("longitude") or None

        booking = Booking.objects.create(
            customer=customer,
            service=service,
            address=request.POST.get("address"),
            amount=service.base_price,
            status="Pending",
            latitude=latitude,
            longitude=longitude,
        )

        messages.success(request, "Booking created successfully")
        return redirect("my_bookings")

    return render(request, "customer/book_service.html", {
        "selected_service": service
    })


# ==========================================
# MY BOOKINGS
# ==========================================
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomerProfile, Booking

# --- VIEW 1: Displaying the list of bookings ---
@login_required
def my_bookings(request):

    customer = CustomerProfile.objects.filter(user=request.user).first()

    if not customer:
        return render(request, "customer/my_bookings.html", {
            "bookings": []
        })

    bookings = Booking.objects.filter(
        customer=customer
    ).select_related(
        "worker",
        "service"
    ).order_by("-id")

    return render(request, "customer/my_bookings.html", {
        "bookings": bookings
    })

# --- VIEW 2: Handling the Booking Form ---
# (Note: Ensure your HTML form calls this view)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Booking, CustomerProfile


@login_required
def my_bookings(request):

    customer = CustomerProfile.objects.filter(user=request.user).first()

    if not customer:
        bookings = Booking.objects.none()
    else:
        bookings = Booking.objects.filter(
            customer=customer
        ).select_related(
            "worker",
            "service",
            "customer"
        ).order_by("-id")

    return render(request, "customer/my_bookings.html", {
        "bookings": bookings
    })

@property
def needs_payment(self):
    return self.payment_method == "Cash" and self.payment_status == "Pending"
# ==========================================
# CUSTOMER PROFILE
# ==========================================
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import CustomerProfile, WorkerProfile, UserRole, Booking


@login_required
def profile(request):

    role = UserRole.objects.get(user=request.user).role

    if role == "worker":

        profile = WorkerProfile.objects.get(user=request.user)

        return render(
            request,
            "worker/worker_profile.html",
            {
                "profile": profile
            }
        )

    # Customer Profile
    profile = CustomerProfile.objects.get(user=request.user)

    bookings = Booking.objects.filter(
        customer=profile
    ).order_by("-id")

    completed_jobs = bookings.filter(status="Completed").count()

    pending_jobs = bookings.exclude(status="Completed").count()

    return render(
        request,
        "customer/profile.html",
        {
            "profile": profile,
            "bookings": bookings,
            "completed_jobs": completed_jobs,
            "pending_jobs": pending_jobs,
        }
    )

# ==========================================
# EDIT PROFILE
# ==========================================
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import WorkerProfile


@login_required
def edit_worker_profile(request):
    profile = WorkerProfile.objects.filter(user=request.user).first()

    if not profile:
        return redirect("worker_profile")

    if request.method == "POST":

        # Update basic information
        profile.phone = request.POST.get("phone", "").strip()
        profile.location = request.POST.get("location", "").strip()
        profile.address = request.POST.get("address", "").strip()
        profile.experience = request.POST.get("experience", "").strip()
        profile.pincode = request.POST.get("pincode", "").strip()

        # Update latitude & longitude
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        if latitude:
            profile.latitude = float(latitude)

        if longitude:
            profile.longitude = float(longitude)

        # Update profile picture
        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES["profile_image"]

        profile.save()

        return redirect("worker_profile")

    context = {
        "profile": profile,
        "location_value": profile.location or "",
    }

    return render(
        request,
        "worker/edit_worker_profile.html",
        context,
    )
# ==========================================
# SERVICES
# ==========================================

@login_required
def services(request):
    services = Service.objects.all()

    return render(
        request,
        "customer/services.html",
        {
            "services": services
        }
    )


# ==========================================
# WORKERS LIST
# ==========================================

@login_required
def workers_list(request):

    workers = WorkerProfile.objects.filter(
        is_approved=True
    )

    return render(
        request,
        "workers_list.html",
        {
            "workers": workers
        }
    )

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import WorkerProfile, Booking


# ==========================================
# WORKER DASHBOARD (SAFE VERSION)
# ==========================================
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import WorkerProfile, Booking, UserRole, WorkerWarning


@login_required
def worker_dashboard(request):

    role = UserRole.objects.filter(user=request.user).first()

    if not role:
        return redirect("login")

    if role.role != "worker":
        return redirect("login")

    worker = WorkerProfile.objects.filter(user=request.user).first()

    if not worker:
        return redirect("worker_profile")

    # Worker is blocked
    if worker.is_blocked:
        return render(
            request,
            "worker/blocked.html",
            {
                "worker": worker,
            },
        )

    # Worker not approved
    if not worker.is_approved:
        return redirect("worker_signup_pending")

    bookings = Booking.objects.filter(worker=worker).order_by("-id")

    warnings = WorkerWarning.objects.filter(worker=worker).order_by("-created_at")

    total_jobs = bookings.count()

    assigned_jobs = bookings.filter(status="Assigned").count()

    completed_jobs = bookings.filter(status="Completed").count()

    total_earnings = sum(
        booking.amount or 0
        for booking in bookings.filter(status="Completed")
    )

    return render(
        request,
        "worker/worker_dashboard.html",
        {
            "worker": worker,
            "bookings": bookings,
            "warnings": warnings,
            "total_jobs": total_jobs,
            "assigned_jobs": assigned_jobs,
            "completed_jobs": completed_jobs,
            "total_earnings": total_earnings,
        },
    )
@login_required
def on_the_way(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)

    booking.status = "On The Way"
    booking.save()

    messages.success(request, "Travelling to customer.")

    return redirect("assign_jobs")
@login_required
def accept_job(request, booking_id):

    worker = get_object_or_404(WorkerProfile, user=request.user)
    booking = get_object_or_404(Booking, id=booking_id, worker=worker)

    booking.is_accepted = True
    booking.status = "On The Way"   # ✅ FIXED FLOW STEP
    booking.save()

    messages.success(request, "Job accepted")
    return redirect("assign_jobs")

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

@login_required
def reject_job(request, booking_id):

    worker = get_object_or_404(WorkerProfile, user=request.user)
    booking = get_object_or_404(Booking, id=booking_id, worker=worker)

    booking.rejected_by = worker
    booking.worker = None
    booking.status = "Pending"
    booking.is_accepted = False
    booking.save()

    messages.warning(request, "Job rejected and sent back to admin")
    return redirect("assign_jobs")

    #==========================================
# ASSIGNED JOBS
# ==========================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Booking, WorkerProfile


# =========================
# WORKER JOB LIST
# =========================
@login_required
def assign_jobs(request):

    worker = WorkerProfile.objects.filter(
        user=request.user
    ).first()

    if not worker:
        return redirect("worker_profile")

    bookings = Booking.objects.filter(
        worker=worker
    ).exclude(
        status="Cancelled"
    ).order_by("-id")

    return render(
        request,
        "worker/assign_jobs.html",
        {
            "worker": worker,
            "bookings": bookings
        }
    )

# =========================
# MARK PAYMENT DONE (CASH)
# =========================
@login_required
def mark_payment_done(request, booking_id, method):
    booking = get_object_or_404(Booking, id=booking_id)

    if method == "cash":
        booking.payment_method = "Cash"

    elif method == "online":
        booking.payment_method = "Online"

    booking.payment_status = "Paid"
    booking.save()

    messages.success(request, "Payment updated successfully")
    return redirect("assign_jobs")

# ==========================================
# COMPLETED JOBS
# ==========================================


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import WorkerProfile, Booking


from django.db.models import Sum
@login_required
def completed_jobs(request):

    worker = WorkerProfile.objects.filter(
        user=request.user
    ).first()

    print("Current Worker:", worker)

    bookings = Booking.objects.filter(
        worker=worker,
        status="Completed"
    )

    print("Completed Jobs Count:", bookings.count())

    for b in bookings:
        print(
            b.id,
            b.status,
            b.worker
        )

    total_completed = bookings.count()

    total_earnings = bookings.aggregate(
        total=Sum("amount")
    )["total"] or 0

    return render(
        request,
        "worker/completed_jobs.html",
        {
            "worker": worker,
            "bookings": bookings,
            "total_completed": total_completed,
            "total_earnings": total_earnings,
        }
    )
# ==========================================
# EARNINGS
# ==========================================

@login_required
def earnings(request):

    worker = WorkerProfile.objects.get(
        user=request.user
    )

    jobs = Booking.objects.filter(
        worker=worker,
        status="Completed"
    )

    total = sum(
        booking.amount
        for booking in jobs
    )

    return render(
        request,
        "worker/earnings.html",
        {
            "jobs": jobs,
            "total": total
        }
    )


# ==========================================
# REVIEWS
# ==========================================

@login_required
def reviews(request):
    return render(
        request,
        "worker/reviews.html"
    )


# ==========================================
# WORKER PROFILE
# ==========================================

# ==========================================
# SUPPORT
# ==========================================

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import SupportChat, SupportMessage


# CUSTOMER CHAT
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import SupportChat, SupportMessage


# ---------------- CUSTOMER ----------------
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import SupportChat, SupportMessage


# ---------------- CUSTOMER SUPPORT ----------------
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import SupportChat, SupportMessage
from .utils import get_bot_reply


@login_required
def customer_support(request):

    chat, created = SupportChat.objects.get_or_create(
        user=request.user,
        chat_type="customer"
    )

    # ✅ Auto welcome message (only first time)
    if created:
        SupportMessage.objects.create(
            chat=chat,
            sender=None,
            message="👋 Hi! Welcome to Support. How can I help you today?"
        )

    # =========================
    # SEND MESSAGE
    # =========================
    if request.method == "POST":
        user_msg = request.POST.get("message", "").strip()

        if user_msg:
            # user message
            SupportMessage.objects.create(
                chat=chat,
                sender=request.user,
                message=user_msg,
                image=request.FILES.get("image"),
                file=request.FILES.get("file")
            )

            # bot reply
            bot_reply = get_bot_reply(user_msg)

            SupportMessage.objects.create(
                chat=chat,
                sender=None,
                message=bot_reply
            )

        return redirect("customer_support")

    messages = chat.messages.all().order_by("created_at")

    return render(request, "customer/support.html", {
        "chat": chat,
        "messages": messages
    })


# ---------------- WORKER SUPPORT ----------------
@login_required
def worker_support(request):

    chat, created = SupportChat.objects.get_or_create(
        user=request.user,
        chat_type="worker"
    )

    # ✅ Auto welcome message
    if created:
        SupportMessage.objects.create(
            chat=chat,
            sender=None,
            message="👷 Welcome to Worker Support. How can I help you today?"
        )

    # =========================
    # SEND MESSAGE
    # =========================
    if request.method == "POST":
        user_msg = request.POST.get("message", "").strip()

        if user_msg:
            # user message
            SupportMessage.objects.create(
                chat=chat,
                sender=request.user,
                message=user_msg,
                image=request.FILES.get("image"),
                file=request.FILES.get("file")
            )

            # bot reply
            bot_reply = get_bot_reply(user_msg)

            SupportMessage.objects.create(
                chat=chat,
                sender=None,
                message=bot_reply
            )

        return redirect("worker_support")

    messages = chat.messages.all().order_by("created_at")

    return render(request, "worker/support.html", {
        "chat": chat,
        "messages": messages
    })


# ---------------- ADMIN INBOX ----------------
@login_required
def admin_support(request):

    if not request.user.is_superuser:
        return redirect("login")

    chats = SupportChat.objects.all().order_by("-created_at")

    return render(request, "admin/support_inbox.html", {
        "chats": chats
    })


# ---------------- ADMIN CHAT ----------------
@login_required
def admin_chat(request, chat_id):

    if not request.user.is_superuser:
        return redirect("login")

    chat = get_object_or_404(SupportChat, id=chat_id)

    if request.method == "POST":
        SupportMessage.objects.create(
            chat=chat,
            sender=request.user,
            message=request.POST.get("message", "").strip(),
            image=request.FILES.get("image"),
            file=request.FILES.get("file")
        )
        return redirect("admin_chat", chat_id=chat.id)

    messages = chat.messages.all().order_by("created_at")

    return render(request, "admin/support_chat.html", {
        "chat": chat,
        "messages": messages
    })


# ---------------- UNREAD COUNT API ----------------
@login_required
def unread_messages_count(request):

    count = SupportMessage.objects.filter(
        chat__user=request.user,
        is_seen=False
    ).exclude(sender=request.user).count()

    return JsonResponse({"unread_count": count})


# ---------------- BOT REPLY ----------------
def get_bot_reply(message):

    msg = message.lower()

    if "booking" in msg:
        return "📅 Check My Bookings section."
    elif "payment" in msg:
        return "💰 Payment after job completion."
    elif "worker" in msg:
        return "👷 Worker assigned based on location."
    elif "cancel" in msg:
        return "❌ Cancel before work starts."
    else:
        return "🤖 We received your message. Team will reply soon."


# ---------------- SUPPORT DETAIL ----------------
def support_detail(request, id):

    chat = get_object_or_404(SupportChat, id=id)
    messages = chat.messages.all().order_by("created_at")

    return render(request, "support_detail.html", {
        "chat": chat,
        "messages": messages
    })
# ==========================================
# ASSIGN WORKER
# ==========================================

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Booking, WorkerProfile


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@login_required
def assign_worker(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)

    # prevent duplicate assignment
    if booking.status == "Assigned":
        messages.warning(request, "Worker already assigned.")
        return redirect("all_bookings")

    # =========================
    # POST → ASSIGN WORKER
    # =========================
    if request.method == "POST":

        worker_id = request.POST.get("worker")

        if not worker_id:
            messages.error(request, "Please select a worker.")
            return redirect("assign_worker", booking_id=booking.id)

        # ✅ SAFE: block blocked + unapproved workers
        worker = get_object_or_404(
            WorkerProfile,
            id=worker_id,
            is_approved=True,
            is_blocked=False
        )

        booking.worker = worker
        booking.status = "Assigned"
        booking.save()

        messages.success(
            request,
            f"Worker {worker.user.username} assigned successfully."
        )

        return redirect("all_bookings")
    # =========================
    # GET → SHOW PAGE
    # =========================
    workers = WorkerProfile.objects.filter(
        is_approved=True
    )

    return render(
        request,
        "admin/assign_worker.html",
        {
            "booking": booking,
            "workers": workers
        }
    )
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from math import radians, sin, cos, sqrt, atan2

from .models import Booking, WorkerProfile


# =========================
# DISTANCE FUNCTION
# =========================
def get_distance(lat1, lon1, lat2, lon2):

    R = 6371  # Earth radius in KM

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# =========================
# AUTO ASSIGN VIEW (ADMIN ONLY)
# =========================
from geopy.distance import geodesic
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages



@login_required
def auto_assign_worker(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)

    if not booking.latitude or not booking.longitude:
        messages.error(request, "Booking location not found")
        return redirect("admin_dashboard")

    booking_location = (
        booking.latitude,
        booking.longitude
    )

    workers = WorkerProfile.objects.filter(
        is_approved=True,
        service_type__iexact=booking.service.name.strip(),
        latitude__isnull=False,
        longitude__isnull=False
    )

    nearest_worker = None
    min_distance = float("inf")

    for worker in workers:

        worker_location = (
            worker.latitude,
            worker.longitude
        )

        distance = geodesic(
            booking_location,
            worker_location
        ).km

        if distance < min_distance:
            min_distance = distance
            nearest_worker = worker

    if not nearest_worker:
        messages.error(
            request,
            f"No approved {booking.service.name} worker found nearby."
        )
        return redirect("admin_dashboard")

    booking.worker = nearest_worker
    booking.status = "Assigned"
    booking.save()

    messages.success(
        request,
        f"{nearest_worker.user.username} assigned ({min_distance:.2f} km away)"
    )

    return redirect("admin_dashboard")




from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomerProfile


@login_required
def edit_profile(request):

    profile, created = CustomerProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        # Update Django User
        request.user.first_name = request.POST.get("first_name")
        request.user.last_name = request.POST.get("last_name")
        request.user.username = request.POST.get("username")
        request.user.email = request.POST.get("email")
        request.user.save()

        # Update Customer Profile
        profile.phone = request.POST.get("phone")
        profile.city = request.POST.get("city")
        profile.address = request.POST.get("address")
        profile.pincode = request.POST.get("pincode")

        # Upload Profile Image
        if request.FILES.get("profile_image"):
            profile.image = request.FILES["profile_image"]

        profile.save()

        messages.success(request, "Profile updated successfully.")

        return redirect("profile")

    return render(
        request,
        "customer/edit_profile.html",
        {
            "profile": profile
        }
    )
@login_required
def accept_job(request, booking_id):
    worker = WorkerProfile.objects.get(user=request.user)
    booking = Booking.objects.get(id=booking_id, worker=worker)

    booking.is_accepted = True
    booking.status = "On The Way"

    if not booking.otp:
        booking.otp = str(random.randint(100000, 999999))
        booking.otp_created_time = timezone.now()

    booking.save()

    return redirect("worker_dashboard")


@login_required
def reject_job(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)

    booking.worker = None
    booking.status = "Pending"
    booking.save()

    return redirect("worker_dashboard")
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Booking
from django.contrib.auth.decorators import login_required


@login_required
def track_worker(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    return render(
        request,
        "worker/track_worker.html",
        {
            "booking": booking
        }
    )


# @login_required
# def get_worker_location(request, booking_id):
#     booking = get_object_or_404(Booking, id=booking_id)

#     return JsonResponse({
#         "latitude": booking.latitude,
#         "longitude": booking.longitude,
#     })
from django.http import JsonResponse
from .models import WorkerLocation
from django.contrib.auth.decorators import login_required

@login_required
def save_location(request):
    lat = request.POST.get('lat')
    lng = request.POST.get('lng')

    WorkerLocation.objects.update_or_create(
        worker=request.user,
        defaults={
            "lat": lat,
            "lng": lng
        }
    )

    return JsonResponse({"status": "success"})
from math import radians, sin, cos, sqrt, atan2
from django.http import JsonResponse

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return round(R * c, 2)


def get_worker_location(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    loc = WorkerLocation.objects.get(worker=booking.worker.user)

    # customer location (example: booking.address lat/lng)
    customer_lat = float(request.GET.get("lat", 0))
    customer_lng = float(request.GET.get("lng", 0))

    distance = calculate_distance(
        customer_lat,
        customer_lng,
        loc.lat,
        loc.lng
    )

    return JsonResponse({
        "lat": loc.lat,
        "lng": loc.lng,
        "distance": distance
    })
    from django.http import JsonResponse
from django.shortcuts import get_object_or_404

@login_required
def get_customer_location(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    return JsonResponse({
        "latitude": booking.latitude,
        "longitude": booking.longitude,
    })
# views.py

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def update_worker_location(request):
    if request.method == "POST":
        data = json.loads(request.body)

        worker_id = data.get("worker_id")
        lat = data.get("latitude")
        lng = data.get("longitude")

        worker = WorkerProfile.objects.get(id=worker_id)
        worker.latitude = lat
        worker.longitude = lng
        worker.save()

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "invalid request"})
def worker_location(request, worker_id):
    worker = WorkerProfile.objects.get(id=worker_id)

    return JsonResponse({
        "latitude": worker.latitude,
        "longitude": worker.longitude
    })



from django.utils import timezone
import random

@login_required
def start_work(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)

    if not booking.worker:
        messages.error(request, "No worker assigned")
        return redirect("assign_jobs")

    booking.status = "Working"

    # generate OTP
    booking.otp = str(random.randint(100000, 999999))
    booking.otp_created_time = timezone.now()
    booking.save()

    messages.success(request, f"OTP generated: {booking.otp}")
    return redirect("assign_jobs")  # ✅ ALWAYS dashboard   # ✅ FIX HERE
@login_required
def verify_otp(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        if str(booking.otp) != str(entered_otp):
            messages.error(request, "Invalid OTP")
            return redirect("assign_jobs")

        booking.otp_verified = True
        booking.status = "Completed"
        booking.payment_status = "Paid"   # ✅ FIXED
        booking.save()

        messages.success(request, "Job completed successfully")
        return redirect("assign_jobs")

    return render(request, "worker/verify_otp.html", {"booking": booking})

    # If the user tries to access this URL directly via GET, 
    # redirect them back to the dashboard.
   
def cancel_booking(request, id):
    booking = Booking.objects.get(id=id)
    booking.status = "Cancelled"
    booking.save()
    return redirect('my_bookings')
def payment_page(request, id):
    booking = Booking.objects.get(id=id)
    return render(request, "customer/payment.html", {"booking": booking})
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def update_status(request, booking_id, status):

    booking = get_object_or_404(Booking, id=booking_id)

    booking.status = status
    booking.save()

    messages.success(request, f"Status updated to {status}")
    return redirect("assign_jobs")
@login_required
def resend_otp(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id)

    if booking.can_resend_otp:
        booking.generate_otp()
        booking.otp_created_time = timezone.now()
        booking.save()

        messages.success(request, "OTP resent")
    else:
        messages.error(request, "Wait 5 minutes")

    return redirect("assign_jobs")
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomerProfile


@login_required
def edit_profile(request):

    profile, created = CustomerProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        # ==========================
        # Update Django User
        # ==========================
        request.user.first_name = request.POST.get("first_name", "")
        request.user.last_name = request.POST.get("last_name", "")
        request.user.username = request.POST.get("username", "")
        request.user.email = request.POST.get("email", "")
        request.user.save()

        # ==========================
        # Update Customer Profile
        # ==========================
        profile.phone = request.POST.get("phone", "")
        profile.city = request.POST.get("city", "")
        profile.address = request.POST.get("address", "")
        profile.pincode = request.POST.get("pincode", "")

        # ==========================
        # DEBUG
        # ==========================
        print("POST DATA:", request.POST)
        print("FILES:", request.FILES)

        # ==========================
        # Upload Image
        # ==========================
        if "profile_image" in request.FILES:

            image = request.FILES["profile_image"]

            print("Image Received:", image)

            profile.image = image

        else:

            print("No image uploaded.")

        profile.save()

        print("Saved Image:", profile.image)

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect("profile")

    return render(
        request,
        "customer/edit_profile.html",
        {
            "profile": profile
        }
    )
from django.http import JsonResponse
from .models import Booking

@login_required
def get_booking_otp(request, booking_id):
    booking = Booking.objects.filter(id=booking_id, customer=request.user.customerprofile).first()

    if not booking:
        return JsonResponse({"error": "Not found"}, status=404)

    return JsonResponse({
        "otp": booking.otp,
        "status": booking.status
    })
from datetime import timedelta
from django.utils import timezone

def is_otp_valid(booking):
    if not booking.otp_created_time:
        return False

    return timezone.now() <= booking.otp_created_time + timedelta(minutes=5)
from .models import Booking, WorkerProfile, Review
from .models import Review
from django.db.models import Avg

@login_required
def reviews(request):

    worker = request.user.workerprofile

    reviews = Review.objects.filter(
        booking__worker=worker
    ).order_by("-created_at")

    average_rating = reviews.aggregate(
        Avg("rating")
    )["rating__avg"]

    return render(
        request,
        "worker/reviews.html",
        {
            "reviews": reviews,
            "average_rating": average_rating,
            "total_reviews_count": reviews.count(),
        }
    )
from .forms import ReviewForm

@login_required
def add_review(request, booking_id):

    booking = Booking.objects.get(
        id=booking_id,
        customer=request.user.customerprofile
    )

    if Review.objects.filter(booking=booking).exists():
        return redirect("my_bookings")

    if request.method == "POST":
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.save()

            return redirect("my_bookings")

    else:
        form = ReviewForm()

    return render(
        request,
        "customer/add_review.html",
        {
            "form": form,
            "booking": booking
        }
    )
@login_required
def manual_assign_worker(request, booking_id):
    if not request.user.is_superuser:
        return redirect("login")

    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":
        worker_id = request.POST.get("worker_id")

        if worker_id:
            worker = WorkerProfile.objects.get(id=worker_id)

            booking.worker = worker
            booking.status = "Assigned"   # ✅ FIX HERE
            booking.is_accepted = False   # ✅ IMPORTANT RESET
            booking.save()

            messages.success(request, f"Assigned to {worker.user.username}")
        else:
            messages.error(request, "No worker selected.")

    return redirect("admin_dashboard")
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from .models import EmailOTP


# STEP 2: VERIFY OTP

def verify_email_otp(request):
    email = request.session.get("email")

    if not email:
        return redirect("send_otp")

    if request.method == "POST":
        otp_input = request.POST.get("otp")

        user = User.objects.get(email=email)
        otp_obj = EmailOTP.objects.filter(user=user).last()

        if otp_obj and otp_obj.otp == otp_input and not otp_obj.is_expired():
            otp_obj.is_verified = True
            otp_obj.save()

            from django.contrib.auth import login
            login(request, user)

            return redirect("home")

        messages.error(request, "Invalid or expired OTP")

    return render(request, "verify_otp.html")



from django.core.mail import send_mail
from django.conf import settings
import random
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import EmailOTP

def ajax_send_otp(request):
    if request.method == "POST":

        email = request.POST.get("email", "").strip().lower()

        user = User.objects.filter(email=email).first()

        if not user:
            return JsonResponse({"success": False, "message": "User not found"})

        # ✅ generate OTP
        otp = str(random.randint(100000, 999999))

        # save OTP
        EmailOTP.objects.create(
            user=user,
            otp=otp
        )

        # send email
        send_mail(
            "Your OTP Code",
            f"Your OTP is {otp}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False
        )

        # save session
        request.session["otp_email"] = email
        request.session.set_expiry(300)

        print("OTP SENT + SESSION SET:", email, otp)

        return JsonResponse({
            "success": True,
            "message": "OTP sent successfully"
        })
from django.contrib.auth import login
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.models import User
from .models import EmailOTP, UserRole
def ajax_verify_otp(request):
    if request.method == "POST":

        otp_input = request.POST.get("otp", "").strip()
        email = request.session.get("otp_email")

        print("SESSION EMAIL:", email)

        if not email:
            return JsonResponse({"success": False, "message": "Session expired"})

        user = User.objects.filter(email=email).first()

        if not user:
            return JsonResponse({"success": False, "message": "User not found"})

        otp_obj = EmailOTP.objects.filter(user=user).last()

        if not otp_obj:
            return JsonResponse({"success": False, "message": "OTP not found"})

        if otp_obj.otp != otp_input:
            return JsonResponse({"success": False, "message": "Invalid OTP"})

        # ✅ LOGIN FIX
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        request.session.set_expiry(86400)

        # redirect based on role
        role = UserRole.objects.filter(user=user).first()

        if role and role.role == "worker":
            redirect_url = reverse("worker_dashboard")
        else:
            redirect_url = reverse("customer_dashboard")

        return JsonResponse({
            "success": True,
            "message": "Login successful",
            "redirect": redirect_url
        })

    return JsonResponse({"success": False, "message": "Invalid request"})
from django.db.models import Avg
from django.contrib.auth.decorators import login_required

@login_required
def admin_reviews(request):

    reviews = Review.objects.select_related(
        "booking",
        "booking__customer",
        "booking__worker"
    ).order_by("-created_at")

    return render(
        request,
        "admin/reviews.html",
        {
            "reviews": reviews
        }
    )
from django.shortcuts import get_object_or_404, redirect

@login_required
def book_worker(request, worker_id):
    worker = get_object_or_404(
        WorkerProfile,
        id=worker_id,
        is_approved=True
    )

    request.session["selected_worker"] = worker.id

    service = Service.objects.get(name=worker.service_type)

    return redirect(f"/book-service/?service_id={service.id}")


@login_required
def my_worker_profile(request):

    worker = WorkerProfile.objects.filter(
        user=request.user
    ).first()

    if not worker:
        return render(
            request,
            "worker/no_profile.html"
        )

    return render(
        request,
        "worker/profile.html",
        {
            "worker": worker
        }
    )
# from django.contrib import messages

# def admin_profile(request):

#     profile = request.user.adminprofile

#     if request.method == "POST":

#         request.user.username = request.POST.get("username")
#         request.user.email = request.POST.get("email")
#         request.user.first_name = request.POST.get("first_name")
#         request.user.last_name = request.POST.get("last_name")

#         if request.FILES.get("profile_image"):
#             profile.image = request.FILES["profile_image"]

#         request.user.save()
#         profile.save()

#         messages.success(request, "✅ Profile updated successfully!")

#         return redirect("admin_profile")

#     context = {
#         "profile": profile,
#     }

#     return render(request, "admin/profile.html", context)
@login_required
def my_worker_profile(request):

    worker = WorkerProfile.objects.filter(
        user=request.user
    ).first()

    if not worker:
        return render(
            request,
            "worker/no_profile.html"
        )

    return render(
        request,
        "worker/profile.html",
        {
            "worker": worker
        }
    )
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.db.models import Avg

from .models import WorkerProfile, Booking, Review


@login_required
def worker_details(request, worker_id):

    worker = get_object_or_404(
        WorkerProfile,
        id=worker_id,
        is_approved=True
    )

    completed_jobs = Booking.objects.filter(
        worker=worker,
        status="Completed"
    ).count()

    reviews = Review.objects.filter(
        booking__worker=worker
    ).order_by("-created_at")

    average_rating = reviews.aggregate(
        Avg("rating")
    )["rating__avg"] or 0

    return render(
        request,
        "customer/worker_details.html",
        {
            "worker": worker,
            "completed_jobs": completed_jobs,
            "reviews": reviews,
            "reviews_count": reviews.count(),
            "average_rating": round(average_rating, 1),
        },
    )
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect

def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get("email")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("forgot_password")

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            messages.success(request, "Password changed successfully. Please login.")
            return redirect("login")

        except User.DoesNotExist:
            messages.error(request, "Email not found.")

    return render(request, "forgot_password.html")