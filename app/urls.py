from django.urls import path
from . import views


urlpatterns= [
    path('',views.home,name="home"),
    path('navbar/',views.navbar,name="navbar"),
    path('register/',views.registration,name="registration")
]