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


@login_required
def worker_profile(request):

    print("LOGGED USER:", request.user.id)
    print("LOGGED EMAIL:", request.user.email)

    profile = WorkerProfile.objects.filter(
        user=request.user
    ).first()

    print("PROFILE:", profile)

    if not profile:
        return render(
            request,
            "worker/no_profile.html"
        )

    return render(
        request,
        "worker/worker_profile.html",
        {"profile": profile}
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
            messages.error(request, "Passwords do not match")
            return redirect("worker_signup_step4")

        if User.objects.filter(username=email).exists():
            messages.error(request, "User already exists")
            return redirect("login")

        if not aadhaar or not pan:
            messages.error(request, "Upload Aadhaar and PAN")
            return redirect("worker_signup_step4")

        try:
            # -------------------------
            # FACE IMAGE PROCESS
            # -------------------------
            face_file_payload = None

            if face_image_base64:
                if ";base64," in face_image_base64:
                    _, imgstr = face_image_base64.split(";base64,")
                else:
                    imgstr = face_image_base64

                decoded = base64.b64decode(imgstr)

                face_file_payload = ContentFile(
                    decoded,
                    name=face_image_name or f"worker_{uuid.uuid4().hex}.png"
                )

            # -------------------------
            # CREATE USER (KEEP ACTIVE = TRUE)
            # -------------------------
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )

            # 🔥 IMPORTANT FIX
            # DO NOT set is_active = False (it breaks login system)
            user.is_active = True
            user.save()

            # -------------------------
            # ROLE CREATE
            # -------------------------
            UserRole.objects.create(user=user, role="worker")

            # -------------------------
            # WORKER PROFILE CREATE
            # -------------------------
            WorkerProfile.objects.create(
                user=user,
                phone=phone,
                date_of_birth=request.session.get("date_of_birth"),
                service_type=request.session.get("service_type"),
                address=request.session.get("address"),
                pincode=request.session.get("pincode"),
                experience=request.session.get("experience"),

                face_image=face_file_payload,
                aadhaar_image=aadhaar,
                pan_image=pan,

                is_approved=False
            )

            # -------------------------
            # GO TO PENDING PAGE
            # -------------------------
            return redirect("worker_signup_pending")

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect("worker_signup_step4")

    return render(request, "worker_signup_step4.html", {"email": email})
# =========================
# PENDING PAGE
# =========================
from django.shortcuts import render, redirect
from .models import WorkerProfile


def worker_signup_pending(request):

    # 🔥 Get latest worker (NO SESSION DEPENDENCY)
    worker = WorkerProfile.objects.order_by("-id").first()

    if not worker:
        return redirect("worker_signup_step1")

    # If admin approved → send to login
    if worker.is_approved:
        return redirect("login")

    return render(
        request,
        "worker_signup_pending.html",
        {"worker": worker}
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

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("customer_signup")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists")
            return redirect("customer_signup")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=full_name
        )

        CustomerProfile.objects.create(
            user=user,
            phone=phone,
            pincode=pincode
        )

        UserRole.objects.create(
            user=user,
            role="customer"
        )

        messages.success(
            request,
            "Customer account created successfully"
        )

        return render(
            request,
            "customer_signup.html",
            {"redirect_to_login": True}
        )

    return render(
        request,
        "customer_signup.html"
    )

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
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect("login")

    context = {
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
@login_required
def admin_workers(request):
    if not request.user.is_superuser:
        return redirect("login")

    workers = WorkerProfile.objects.all()

    return render(request, "admin/workers.html", {
        "workers": workers
    })


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


# ==========================================
# BOOKINGS PAGE
# ==========================================
@login_required
def admin_bookings(request):

    if not request.user.is_superuser:
        return redirect("login")

    bookings = Booking.objects.select_related(
        "customer",
        "worker",
        "service"
    ).order_by("-booking_date")   # ✅ FIXED

    workers = WorkerProfile.objects.filter(
        is_approved=True
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
def admin_profile(request):
    if not request.user.is_superuser:
        return redirect("login")

    return render(request, "admin/profile.html", {
        "total_workers": WorkerProfile.objects.count(),
        "total_customers": CustomerProfile.objects.count(),
        "total_bookings": Booking.objects.count(),
        "pending_bookings": Booking.objects.filter(status="Pending").count(),
    })


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
from .models import (
    CustomerProfile,
    WorkerProfile,
    UserRole,
    Booking
)

@login_required
def profile(request):

    role = UserRole.objects.get(
        user=request.user
    ).role

    if role == "worker":

        profile = WorkerProfile.objects.get(
            user=request.user
        )

        return render(
            request,
            "worker/worker_profile.html",
            {
                "profile": profile
            }
        )

    customer = CustomerProfile.objects.get(
        user=request.user
    )

    bookings = Booking.objects.filter(
        customer=customer
    ).order_by("-id")[:5]

    return render(
        request,
        "customer/profile.html",
        {
            "customer": customer,
            "bookings": bookings
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
        profile.phone = request.POST.get("phone")
        # Handle potential empty input
        profile.location = request.POST.get("location") or ""
        profile.address = request.POST.get("address")
        profile.experience = request.POST.get("experience")
        profile.pincode = request.POST.get("pincode")

        profile.save()
        return redirect("worker_profile")

    # FIX: Ensure 'None' is converted to an empty string for the template
    context = {
        "profile": profile,
        "location_value": profile.location if profile.location else ""
    }
    return render(request, "worker/edit_worker_profile.html", context)
# ==========================================
# SERVICES
# ==========================================

@login_required
def services(request):

    services = Service.objects.filter(
        is_active=True
    )

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
from .models import WorkerProfile, Booking, UserRole

@login_required
def worker_dashboard(request):

    print("========== WORKER DASHBOARD ==========")
    print("USER:", request.user)
    print("EMAIL:", request.user.email)

    role = UserRole.objects.filter(user=request.user).first()

    print("ROLE:", role.role if role else "NO ROLE")

    if not role:
        return redirect("login")

    if role.role != "worker":
        return redirect("login")

    worker = WorkerProfile.objects.filter(user=request.user).first()

    print("WORKER:", worker)

    if not worker:
        print("NO WORKER PROFILE FOUND")
        return redirect("worker_profile")

    print("APPROVED:", worker.is_approved)

    if not worker.is_approved:
        print("REDIRECTING TO PENDING PAGE")
        return redirect("worker_signup_pending")

    bookings = Booking.objects.filter(worker=worker).order_by("-id")

    total_jobs = bookings.count()
    assigned_jobs = bookings.filter(status="Assigned").count()
    completed_jobs = bookings.filter(status="Completed").count()

    total_earnings = sum(
        booking.amount or 0
        for booking in bookings.filter(status="Completed")
    )

    print("LOADING DASHBOARD")

    return render(request, "worker/worker_dashboard.html", {
        "worker": worker,
        "bookings": bookings,
        "total_jobs": total_jobs,
        "assigned_jobs": assigned_jobs,
        "completed_jobs": completed_jobs,
        "total_earnings": total_earnings,
    })
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
@login_required
def customer_support(request):

    chat, created = SupportChat.objects.get_or_create(
        user=request.user,
        chat_type="customer"
    )

    # 🔵 AUTO WELCOME MESSAGE
    if created:
        SupportMessage.objects.create(
            chat=chat,
            sender=None,
            message="👋 Hi! Welcome to Home Service Support.\nPlease tell us your issue — we are here to help you 24/7.",
            is_bot=True
        )

    # ⚡ USER MESSAGE
    if request.method == "POST":
        user_msg = request.POST.get("message")

        SupportMessage.objects.create(
            chat=chat,
            sender=request.user,
            message=user_msg
        )

        # 🔵 SIMPLE AUTO BOT REPLY
        bot_reply = get_bot_reply(user_msg)

        SupportMessage.objects.create(
            chat=chat,
            sender=None,
            message=bot_reply,
            is_bot=True
        )

        return redirect("customer_support")

    messages = chat.messages.all().order_by("created_at")

    return render(request, "customer/support_chat.html", {
        "chat": chat,
        "messages": messages
    })

# WORKER CHAT
@login_required
def worker_support(request):

    chat, created = SupportChat.objects.get_or_create(
        user=request.user,
        chat_type="worker"
    )

    if created:
        SupportMessage.objects.create(
            chat=chat,
            sender=None,
            message="👷 Welcome Worker Support!\nYou can ask about jobs, payments, or app issues here.",
            is_bot=True
        )

    if request.method == "POST":
        user_msg = request.POST.get("message")

        SupportMessage.objects.create(
            chat=chat,
            sender=request.user,
            message=user_msg
        )

        bot_reply = get_bot_reply(user_msg)

        SupportMessage.objects.create(
            chat=chat,
            sender=None,
            message=bot_reply,
            is_bot=True
        )

        return redirect("worker_support")

    messages = chat.messages.all().order_by("created_at")

    return render(request, "worker/support_chat.html", {
        "chat": chat,
        "messages": messages
    })
def get_bot_reply(message):
    
    msg = message.lower()

    if "booking" in msg:
        return "📅 You can check your bookings in 'My Bookings' section."

    elif "payment" in msg:
        return "💰 Payments are processed after job completion."

    elif "worker" in msg:
        return "👷 Workers are assigned based on nearest location."

    elif "cancel" in msg:
        return "❌ You can cancel booking before work starts."

    else:
        return "🤖 We received your message. Our team will respond soon."
# ADMIN INBOX
@login_required
def admin_support(request):

    if not request.user.is_superuser:
        return redirect("login")

    chats = SupportChat.objects.all().order_by("-created_at")

    return render(request, "admin/support_inbox.html", {
        "chats": chats
    })
    


# ADMIN CHAT
@login_required
def admin_chat(request, chat_id):

    if not request.user.is_superuser:
        return redirect("login")

    chat = get_object_or_404(SupportChat, id=chat_id)

    if request.method == "POST":
        SupportMessage.objects.create(
            chat=chat,
            sender=request.user,
            message=request.POST.get("message"),
            image=request.FILES.get("image"),
            file=request.FILES.get("file")
        )
        return redirect("admin_chat", chat_id=chat.id)

    messages = chat.messages.all().order_by("created_at")

    messages.exclude(sender=request.user).update(is_seen=True)

    return render(request, "admin/support_chat.html", {
        "chat": chat,
        "messages": messages
    })


# UNREAD API
@login_required
def unread_messages_count(request):

    count = SupportMessage.objects.filter(
        chat__user=request.user,
        is_seen=False
    ).exclude(sender=request.user).count()

    return JsonResponse({
        "unread_count": count
    })
    from django.shortcuts import render, get_object_or_404
from .models import SupportChat

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

        worker = get_object_or_404(
            WorkerProfile,
            id=worker_id,
            is_approved=True
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
from django.shortcuts import render, redirect, get_object_or_404
from .models import WorkerProfile


@login_required
def edit_profile(request):
    try:
        profile = WorkerProfile.objects.get(user=request.user)
    except WorkerProfile.DoesNotExist:
        profile = None

    if request.method == "POST":
        if profile is None:
            profile = WorkerProfile(user=request.user)

        profile.name = request.POST.get("name")
        profile.phone = request.POST.get("phone")
        profile.date_of_birth = request.POST.get("date_of_birth")
        profile.service_type = request.POST.get("service_type")
        profile.address = request.POST.get("address")
        profile.city = request.POST.get("city")
        profile.state = request.POST.get("state")
        profile.experience = request.POST.get("experience")
        profile.pincode = request.POST.get("pincode")

        profile.save()
        return redirect("worker_profile")

    return render(request, "accounts/edit___profile.html", {
        "profile": profile
    })
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
from .models import Booking

def track_worker(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    return render(request, "customer/track_worker.html", {
        "booking": booking
    })
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
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomerProfile


def edit_profile(request):
    user = request.user

    # get or create customer profile
    profile, created = CustomerProfile.objects.get_or_create(user=user)

    if request.method == "POST":

        # ======================
        # USER MODEL UPDATE
        # ======================
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.save()

        # ======================
        # CUSTOMER PROFILE UPDATE
        # ======================
        profile.phone = request.POST.get("phone")
        profile.pincode = request.POST.get("pincode")

        profile.latitude = request.POST.get("latitude") or None
        profile.longitude = request.POST.get("longitude") or None

        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(request, "customer/edit_profile.html", {"profile": profile})
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