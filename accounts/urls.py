from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [

    # ======================================================
    # HOME
    # ======================================================
    path("", views.home, name="home"),
    path("redirect/", views.role_based_redirect, name="role_redirect"),

    # ======================================================
    # AUTH
    # ======================================================
    path("login/", views.user_login, name="login"),
    path("worker-login/", views.user_login, name="worker_login"),
    path("logout/", views.user_logout, name="logout"),
    path("signup/customer/", views.customer_signup, name="customer_signup"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),

    # ======================================================
    # DASHBOARDS
    # ======================================================
    path("customer-dashboard/", views.customer_dashboard, name="customer_dashboard"),
    path("worker-dashboard/", views.worker_dashboard, name="worker_dashboard"),
    path("worker-blocked/", views.worker_blocked, name="worker_blocked"),

    # ======================================================
    # WORKER SIGNUP
    # ======================================================
      path(
    "signup/worker/",
    views.worker_signup_step1,
    name="worker_signup"
),
    path("worker-signup/step1/", views.worker_signup_step1, name="worker_signup_step1"),
    path("worker-signup/step2/", views.worker_signup_step2, name="worker_signup_step2"),
    path("worker-signup/step3/", views.worker_signup_step3, name="worker_signup_step3"),
    path("worker-signup/step4/", views.worker_signup_step4, name="worker_signup_step4"),
    path("worker-signup/pending/", views.worker_signup_pending, name="worker_signup_pending"),
  

    # ======================================================
    # WORKERS
    # ======================================================
    path("workers/", views.workers_list, name="workers_list"),
    path("worker-profile/", views.worker_profile, name="worker_profile"),
    path("edit-worker-profile/", views.edit_worker_profile, name="edit_worker_profile"),
    path("approve-worker/<int:worker_id>/", views.approve_worker, name="approve_worker"),

    path("worker/<int:worker_id>/", views.worker_details, name="worker_details"),
    path("worker-profile/<int:worker_id>/", views.worker_details, name="worker_profile_details"),
    path("my-worker-profile/", views.my_worker_profile, name="my_worker_profile"),

    # ======================================================
    # SERVICES
    # ======================================================
    path("services/", views.services, name="services"),
    path("book-service/", views.book_service, name="book_service"),
    path("book-worker/<int:worker_id>/", views.book_worker, name="book_worker"),

    # ======================================================
    # BOOKINGS
    # ======================================================
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("cancel-booking/<int:id>/", views.cancel_booking, name="cancel_booking"),

    # ======================================================
    # JOB MANAGEMENT
    # ======================================================
    path("assign-jobs/", views.assign_jobs, name="assign_jobs"),
    path("completed-jobs/", views.completed_jobs, name="completed_jobs"),
    path("earnings/", views.earnings, name="earnings"),
    path("reviews/", views.reviews, name="reviews"),

    # ======================================================
    # JOB ACTIONS
    # ======================================================
    path("assign-worker/<int:booking_id>/", views.assign_worker, name="assign_worker"),
    path("manual-assign/<int:booking_id>/", views.manual_assign_worker, name="manual_assign_worker"),
    path("auto-assign/<int:booking_id>/", views.auto_assign_worker, name="auto_assign_worker"),

    path("accept-job/<int:booking_id>/", views.accept_job, name="accept_job"),
    path("reject-job/<int:booking_id>/", views.reject_job, name="reject_job"),

    path(
        "update-status/<int:booking_id>/<str:status>/",
        views.update_status,
        name="update_status",
    ),

    path("start-work/<int:booking_id>/", views.start_work, name="start_work"),

    # ======================================================
    # OTP
    # ======================================================
    path("booking-otp/<int:booking_id>/", views.get_booking_otp, name="booking_otp"),
    path("verify-otp/<int:booking_id>/", views.verify_otp, name="verify_otp"),
    path("verify-otp/", views.verify_email_otp, name="verify_email_otp"),
    path(
    "resend-otp/<int:booking_id>/",
    views.resend_otp,
    name="resend_otp",
),
    path("ajax/verify-otp/", views.ajax_verify_otp, name="ajax_verify_otp"),
 path(
    "dashboard/admin/resend-otp/<int:booking_id>/",
    views.admin_resend_otp,
    name="admin_resend_otp",
),

    # ======================================================
    # REVIEWS
    # ======================================================
    path("add-review/<int:booking_id>/", views.add_review, name="add_review"),

    # ======================================================
    # PROFILE
    # ======================================================
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    # ======================================================
    # LOCATION
    # ======================================================
    path("save-location/", views.save_location, name="save_location"),
    path("worker-location/<int:worker_id>/", views.worker_location, name="worker_location"),
    path("track-worker/<int:booking_id>/", views.track_worker, name="track_worker"),
    path("get-worker-location/<int:booking_id>/", views.get_worker_location, name="get_worker_location"),
    path("get-customer-location/<int:booking_id>/", views.get_customer_location, name="get_customer_location"),
    path("api/update-location/", views.update_worker_location, name="update_location"),

    # ======================================================
    # PAYMENT
    # ======================================================
    path("payment/<int:id>/", views.payment_page, name="payment_page"),

    path(
        "payment-select/<int:booking_id>/<str:method>/",
        views.select_payment_method,
        name="select_payment_method",
    ),

    path(
        "mark_payment_done/<int:booking_id>/<str:method>/",
        views.mark_payment_done,
        name="mark_payment_done",
    ),

    # ======================================================
    # ADMIN
    # ======================================================
    path("dashboard/admin/", views.admin_dashboard, name="admin_dashboard"),
    path("dashboard/admin/workers/", views.admin_workers, name="admin_workers"),
    path("dashboard/admin/customers/", views.admin_customers, name="admin_customers"),
    path("dashboard/admin/bookings/", views.admin_bookings, name="admin_bookings"),
    path("dashboard/admin/profile/", views.admin_profile, name="admin_profile"),
    path("dashboard/admin/reviews/", views.admin_reviews, name="admin_reviews"),
    path("dashboard/admin/support/", views.admin_support, name="admin_support"),
    path("dashboard/admin/support/<int:chat_id>/", views.admin_chat, name="admin_chat"),
    path("admin-stats/", views.admin_stats, name="admin_stats"),

    path("dashboard/admin/workers/warn/<int:worker_id>/", views.warn_worker, name="warn_worker"),
    path("dashboard/admin/workers/block/<int:worker_id>/", views.block_worker, name="block_worker"),
    path("dashboard/admin/workers/unblock/<int:worker_id>/", views.unblock_worker, name="unblock_worker"),

    # ======================================================
    # SUPPORT
    # ======================================================
    path("customer/support/", views.customer_support, name="customer_support"),
    path("worker/support/", views.worker_support, name="worker_support"),
    path("support/<int:id>/", views.support_detail, name="support_detail"),
    path("api/unread-count/", views.unread_messages_count, name="unread_messages_count"),
   path("clean-db/", views.clean_database, name="clean_database"),
   path("cleanup/", views.cleanup_customer_profiles),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)