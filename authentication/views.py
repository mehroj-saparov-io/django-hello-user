from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail
from .utils import generate_code

@login_required
def home(request):
    return render(request, 'home.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {
                'error': 'Bu email allaqachon ishlatilgan'
            })

        code = generate_code()

        # session’da vaqtincha saqlaymiz
        request.session['verify_code'] = code
        request.session['register_data'] = {
            'username': username,
            'email': email,
            'password': password
        }

        send_mail(
            'Email tasdiqlash kodi',
            f'Sizning tasdiqlash kodingiz: {code}',
            None,
            [email],
        )

        return redirect('verify_email')

    return render(request, 'register.html')


def verify_email(request):
    if request.method == 'POST':
        code = request.POST.get('code')

        if code == request.session.get('verify_code'):
            data = request.session.get('register_data')

            User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )

            request.session.flush()
            return redirect('login')

        return render(request, 'verify_email.html', {
            'error': 'Kod noto‘g‘ri'
        })

    return render(request, 'verify_email.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {
                'error': 'Username yoki parol xato'
            })

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')
