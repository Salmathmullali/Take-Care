from django.urls import path
from . import views


urlpatterns= [
    path('',views.home,name="home"),
    path('navbar/',views.navbar,name="navbar"),
    path('normal_user_page/',views.normal_user_page,name="normal_user_page"),
    path('seller_page/',views.seller_page,name="seller_page"),
    path('charity_page/',views.charity_page,name="charity_page"),
    path('register/',views.registration,name="registration"),
    path('user_reg/',views.user_reg,name="user_reg"),
    path('charity_user_reg/',views.charity_user_reg,name="charity_user_reg"),
    path('seller_reg/',views.seller_reg,name="seller_reg")

]