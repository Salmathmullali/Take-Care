from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    
    # Applications
    path('apply/donor/', views.apply_donor, name='apply_donor'),
    path('apply/charity/', views.apply_charity, name='apply_charity'),
    
    # Category and Requests
    path('category/<int:category_id>/', views.view_donors_by_category, name='view_donors'),
    path('send-request/<int:donor_id>/', views.send_request_to_donor, name='send_request'),
    path('respond/<int:request_id>/<str:action>/', views.respond_to_request, name='respond_request'),
]