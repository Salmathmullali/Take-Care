from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import LoginForm, MyUserCreationForm


def home(request):
    return render(request, 'index.html')


def register_user(request):
    if request.user.is_authenticated:
        return redirect('charity:my_dashboard')
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to Take Care! Your account was created.')
            return redirect('charity:my_dashboard')
    else:
        form = MyUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'auth/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy('charity:my_dashboard')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def user_dashboard(request):
    return redirect('charity:my_dashboard')
