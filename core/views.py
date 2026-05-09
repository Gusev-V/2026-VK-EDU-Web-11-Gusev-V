from django.shortcuts import render


def login(request):
    return render(request, 'core/login.html')


def profile(request):
    return render(request, 'core/setting.html')


def registration(request):
    return render(request, 'core/reg.html')
