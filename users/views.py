from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

def register(request):

    if request.method == 'POST':

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        allowed_domains = ['manarat.ac.bd']

        email_domain = email.split('@')[-1]

        if email_domain not in allowed_domains:

            return render(request, 'users/register.html', {
                'error': 'Only university email allowed!'
            })

        # Check existing username

        if User.objects.filter(username=username).exists():

         return render(request, 'users/register.html', {
         'error': 'Username already exists!'})

        # Create user
        user = User.objects.create_user(
          username=username,
          email=email,
          password=password)

        # Admin approval required
        user.is_active = True
        user.save()

        return redirect('login')

    return render(request, 'users/register.html')


def login_view(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('dashboard')

        else:

            return render(request, 'users/login.html', {
                'error': 'Invalid credentials or admin approval pending'
            })

    return render(request, 'users/login.html')


def dashboard(request):

    if not request.user.is_authenticated:

        return redirect('login')

    return render(request, 'users/dashboard.html')


def logout_view(request):

    logout(request)

    return redirect('login')