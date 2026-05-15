from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from groq import Groq

from django.conf import settings

from users.models import AIQuery

client = Groq(
    api_key=settings.GROQ_API_KEY
)

def history(request):

    if not request.user.is_authenticated:

        return redirect('login')

    chats = AIQuery.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'users/history.html', {
        'chats': chats
    })

def home(request):

    return render(request, 'users/home.html')

def assistant(request):

    if not request.user.is_authenticated:

        return redirect('login')

    response = None

    if request.method == 'POST':

        prompt = request.POST.get('prompt')

        language = request.POST.get('language')

        full_prompt = f"""
You are an expert AI Coding Mentor for university students.

Selected Programming Language:
{language}

Your tasks:
- Find coding errors
- Explain bugs clearly
- Generate correct code
- Explain output
- Teach step-by-step
- Use beginner friendly explanations

Student Request:
{prompt}

IMPORTANT:
Generate code and explanations specifically in {language}.
IMPORTANT:
Always return code inside markdown code blocks.

Example:

```python
print("Hello")
```
"""

        try:

            chat_completion = client.chat.completions.create(

                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],

                model="llama-3.3-70b-versatile",
            )

            response = chat_completion.choices[0].message.content

            AIQuery.objects.create(
                user=request.user,
                prompt=prompt,
                response=response
            )

        except Exception as e:

            response = f"AI Error: {str(e)}"

    return render(request, 'users/assistant.html', {
        'response': response
    })

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