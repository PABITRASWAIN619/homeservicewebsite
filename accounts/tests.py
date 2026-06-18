from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Signup
    path(
        'signup/customer/',
        views.customer_signup,
        name='customer_signup'
    ),

    path(
        'signup/worker/',
        views.worker_signup,
        name='worker_signup'
    ),

    # Login / Logout
    path(
        'login/',
        views.user_login,
        name='login'
    ),

    path(
        'logout/',
        views.user_logout,
        name='logout'
    ),

    # Dashboards
    path(
        'customer-dashboard/',
        views.customer_dashboard,
        name='customer_dashboard'
    ),

    path(
        'worker-dashboard/',
        views.worker_dashboard,
        name='worker_dashboard'
    ),

    path(
        'admin-dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),
]