from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_user, name='register'),
    path('user_reg/', views.register_user, name='user_reg'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('registration/', RedirectView.as_view(pattern_name='login', permanent=False), name='registration'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),

    # Legacy charity routes → new module
    path(
        'apply/donor/',
        RedirectView.as_view(pattern_name='charity:blood:apply_donor', permanent=False),
        name='apply_donor',
    ),
    path(
        'apply/charity/',
        RedirectView.as_view(pattern_name='charity:medical:apply_recipient', permanent=False),
        name='apply_charity',
    ),
    path(
        'category/<int:category_id>/',
        RedirectView.as_view(url='/charity/', permanent=False),
        name='view_donors',
    ),
    path(
        'send-request/<int:donor_id>/',
        RedirectView.as_view(pattern_name='charity:hub', permanent=False),
        name='send_request',
    ),
    path(
        'respond/<int:request_id>/<str:action>/',
        RedirectView.as_view(pattern_name='charity:my_dashboard', permanent=False),
        name='respond_request',
    ),
    # Legacy registration aliases
    path(
        'charity_user_reg/',
        RedirectView.as_view(pattern_name='charity:hub', permanent=False),
        name='charity_user_reg',
    ),
    path(
        'seller_reg/',
        RedirectView.as_view(pattern_name='register', permanent=False),
        name='seller_reg',
    ),
]
