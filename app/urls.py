from django.urls import path
from . import views

urlpatterns = [

    # ================= HOME =================
    path('', views.home, name="home"),

    # ================= AUTH =================
    path('register/', views.register_user, name="user_reg"),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ================= USER DASHBOARD =================
    path('dashboard/', views.user_dashboard, name="user_dashboard"),
    path('user/', views.user_page, name="user_page"),

    # ================= APPLICATIONS =================
    path('apply/donor/', views.apply_donor, name='apply_donor'),
    path('apply/charity/', views.apply_charity, name='apply_charity'),

    # ================= CHARITY → DONOR FLOW =================
    # Charity sees available donors
    path('donors/available/', views.available_donors, name='available_donors'),

    # Charity sends request to donor
    path(
    "send-donor-request/<int:donor_id>/",
    views.send_donor_request,
    name="send_donor_request"
),

    path(
    "respond-request/<int:request_id>/<str:action>/",
    views.respond_request,
    name="respond_request"
),
    path(
    "approve-receiver/<int:request_id>/",
    views.approve_receiver,
    name="approve_receiver"
),
    path(
    "reject-receiver/<int:request_id>/",
    views.reject_receiver,
    name="reject_receiver"
),




    # ================= DONOR SIDE =================
    # Donor views requests
    # path('donor/requests/', views.donor_requests, name='donor_requests'),

    # Donor approves / rejects request
    

    # ================= ADMIN =================
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # ---- Donor Applications ----
    path('admin/donor/approve/<int:donor_id>/', views.approve_donor, name='approve_donor'),
    path('admin/donor/reject/<int:donor_id>/', views.reject_donor, name='reject_donor'),

    # ---- Charity Applications ----
    path('admin/charity/approve/<int:charity_id>/', views.approve_charity, name='approve_charity'),
    path('admin/charity/reject/<int:charity_id>/', views.reject_charity, name='reject_charity'),
]
