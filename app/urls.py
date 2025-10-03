from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Home and Navigation
    path('', views.home, name="home"),
    path('navbar/', views.navbar, name="navbar"),
    path('normal_user_page/', views.normal_user_page, name="normal_user_page"),
    path('seller_page/', views.seller_page, name="seller_page"),
    path('charity_page/', views.charity_page, name="charity_page"),
    path('apply-donor/', views.apply_donor, name='apply_donor'),
    path('apply-charity/', views.apply_charity, name='apply_charity'),
    
    # Registration and Login
    path('register/', views.registration, name="registration"),
    path('user_reg/', views.user_reg, name="user_reg"),
    path('charity_user_reg/', views.charity_user_reg, name="charity_user_reg"),
    path('seller_reg/', views.seller_reg, name="seller_reg"),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('terms_condition/', views.terms_condition, name='terms_condition'),
    path('admin_page/', views.admin_page, name='admin_page'),
    path('charity_approvel/', views.charity_approvel, name='charity_approvel'),
    path("donor-applications/", views.donor_applications_list, name="donor_applications_list"),
    path("donor-applications/<int:pk>/approve/", views.approve_donor, name="approve_donor"),
    path("donor-applications/<int:pk>/reject/", views.reject_donor, name="reject_donor"),
    path("approved-donors/", views.approved_donors, name="approved_donors"),
    path('business_approvel/', views.business_approvel, name='business_approvel'),

    # Password Management
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]


