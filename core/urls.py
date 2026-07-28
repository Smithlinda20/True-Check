from django.urls import path
from . import views

urlpatterns = [
    # Home & Public Pages
    path("", views.home, name="home"),
    path("services/", views.services_page, name="services"),
    path("pricing/", views.pricing_page, name="pricing"),
    
    # Authentication
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    # User Dashboard & Profile
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    
    # Background Check Requests
    path("request-check/", views.request_check, name="request_check"),
    path("check/<str:request_id>/", views.check_detail, name="check_detail"),
    path("my-checks/", views.my_checks, name="my_checks"),
    
    # Payment & Invoice
    path("payment/<str:request_id>/", views.process_payment, name="process_payment"),
    path("invoices/", views.my_invoices, name="my_invoices"),
    
    # Notifications
    path("notifications/", views.notifications, name="notifications"),
    path("notification/<int:notification_id>/read/", views.mark_notification_read, name="mark_notification_read"),
]