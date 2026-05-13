from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.urls import is_valid_path
from .forms import LoginForm, RegistrationForm, ProfileForm
from .models import Profile


def login(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            next_url = request.POST.get('next') or request.GET.get('next', '')
            if next_url and is_valid_path(next_url):
                return redirect(next_url)
            return redirect('index')
    else:
        form = LoginForm()

    context = {
        'form': form,
        'next': request.GET.get('next', ''),
    }
    return render(request, 'core/login.html', context)


@login_required
def profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={'nickname': request.user.username}
    )

    if request.method == 'POST':
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=request.user.profile,
            user=request.user
        )
        if form.is_valid():
            form.save()
            return redirect('setting')
    else:
        form = ProfileForm(
            instance=request.user.profile,
            user=request.user
        )

    context = {
        'form': form,
    }
    return render(request, 'core/setting.html', context)


def registration(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('index')

    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'core/reg.html', context)


def logout(request):
    auth_logout(request)
    return redirect('login')
