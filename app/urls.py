from django.urls import path
from . import views

urlpatterns = [

    # ================= HOME =================
    path('', views.home, name="home"),

    # ================= AUTH =================
    path('register/', views.register_user, name="user_reg"),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),

    path('logout/', views.logout_view, name='logout'),

    # ================= USER DASHBOARD =================
    path('user/', views.user_page, name="user_page"),

    # ================= APPLICATIONS =================
    path('apply/donor/', views.apply_donor, name='apply_donor'),
    path('apply/charity/', views.charity_application, name='apply_charity'),

    # ================= CHARITY BROWSING =================
    path('charity/categories/', views.charity_categories, name='charity_categories'),
    path('charity/categories/<str:category>/', views.category_donors, name='category_donors'),

    # ================= ADMIN =================
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # ---- Donor Applications (Admin) ----
    path('admin/donors/', views.donor_list, name='donor_list'),
    path('admin/donor/<int:donor_id>/', views.admin_donor_detail, name='admin_donor_detail'),
    path('admin/donor/approve/<int:donor_id>/', views.approve_donor, name='approve_donor'),
    path('admin/donor/reject/<int:donor_id>/', views.reject_donor, name='reject_donor'),

    # ---- Charity Applications (Admin) ----
    path('admin/charity/approve/<int:id>/', views.approve_charity, name='approve_charity'),
    path('admin/charity/reject/<int:id>/', views.reject_charity, name='reject_charity'),

    # ================= DONOR ↔ RECEIVER FLOW =================
    # Charity receiver sends request to donor
    path('donor/request/<int:donor_id>/', views.request_donor, name='request_donor'),

    # Donor actions on receiver requests
    path('donor/requests/', views.donor_requests, name='donor_requests'),
    path('donor/request/approve/<int:request_id>/', views.approve_receiver, name='approve_receiver'),
    path('donor/request/reject/<int:request_id>/', views.reject_receiver, name='reject_receiver'),

]
