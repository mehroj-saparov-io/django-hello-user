from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.core.mail import send_mail
from .utils import generate_code

@login_required
def home(request):
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        request.session.flush()

        username = request.POST['username'].strip()
        email = request.POST['email'].lower().strip()
        password = request.POST['password']

        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {
                'error': 'Bu email allaqachon ishlatilgan'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'error': 'Bu username band'
            })

        code = generate_code()

        request.session['verify_code'] = code
        request.session['register_data'] = {
            'username': username,
            'email': email,
            'password': password
        }

        try:
            send_mail(
                subject="BusterDev — Email tasdiqlash kodi",
                message=(
                    "Assalomu alaykum!\n\n"
                    "Bizning demo Auth loyihamizdan ro‘yxatdan o‘tishni "
                    "tasdiqlash uchun kodingiz:\n\n"
                    f"{code}\n\n"
                    "Agar bu amalni siz bajarmagan bo‘lsangiz, "
                    "ushbu xabarni e’tiborsiz qoldiring.\n\n"
                    "Hurmat bilan,\n"
                    "BusterDev jamoasi"
                ),
                from_email="BusterDev <yourgmail@gmail.com>",
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception:
            return render(request, 'register.html', {
                'error': 'Email yuborilmadi. Keyinroq urinib ko‘ring.'
            })

        return redirect('verify_email')

    return render(request, 'register.html')

def verify_email(request):
    if request.method == 'POST':
        code = request.POST.get('code')

        if code != request.session.get('verify_code'):
            return render(request, 'verify_email.html', {
                'error': 'Kod noto‘g‘ri'
            })

        data = request.session.get('register_data')

        # 🔐 HIMOYA: agar user oldin yaratilgan bo‘lsa
        if User.objects.filter(username=data['username']).exists():
            messages.info(
                request,
                "Bu akkaunt allaqachon tasdiqlangan."
            )
            return redirect('login')

        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )

        login(request, user)
        request.session.flush()

        messages.success(
            request,
            "Email tasdiqlandi! Xush kelibsiz 👋"
        )

        return redirect('home')

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
