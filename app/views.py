from django.shortcuts import render

def home(request):
    return render(request,"index.html")
def navbar(request):
    return render(request,"navbar.html")

def registration(request):
    return render(request,"register.html")
def user_reg(request):
    return render(request,"user_reg.html")


