from django.urls import path
from . import views

urlpatterns = [

    # Home
    path('', views.home, name="home"),
    path('navbar/', views.navbar, name="navbar"),

    # Charity pages
    path('charity-page/', views.charity_page, name="charity_page"),
    path('apply-donor/', views.apply_donor, name='apply_donor'),
    path('apply-charity/', views.charity_application, name='apply_charity'),

    # Authentication
    path('nav_reg/', views.nav_reg, name="nav_reg"),
    path('user_page/', views.user_page, name="user_page"),
    path('register/', views.register_user, name="registration"),  # ✅ FIX
    path('user-reg/', views.user_reg, name="user_reg"),
    path('charity-user-reg/', views.charity_user_reg, name="charity_user_reg"),
    path('seller-reg/', views.seller_reg, name="seller_reg"),

    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Password reset
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         views.CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         views.CustomPasswordResetCompleteView.as_view(),
         name='password_reset_complete'),

    # ================= ADMIN =================
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Donors (Admin)
    path('admin/donors/', views.donor_list, name='donor_list'),
    path('admin/donor/<int:donor_id>/', views.admin_donor_detail, name='admin_donor_detail'),

    path('donor/approve/<int:pk>/', views.approve_donor, name='approve_donor'),
    path('donor/reject/<int:pk>/', views.reject_donor, name='reject_donor'),
    path('donors/approved/', views.approved_donors, name='approved_donors'),

    # Charity Requests
    path('charity/approve/<int:pk>/', views.approve_charity_app, name='approve_charity'),
    path('charity/reject/<int:pk>/', views.reject_charity_app, name='reject_charity'),
    path('charities/approved/', views.approved_charity_apps, name='approved_charities'),

    # Charity Applications (Admin)
    path('charity-app/approve/<int:pk>/', views.approve_charity_app, name='approve_charity_app'),
    path('charity-app/reject/<int:pk>/', views.reject_charity_app, name='reject_charity_app'),
    path('charity-apps/approved/', views.approved_charity_apps, name='approved_charity_apps'),

]
