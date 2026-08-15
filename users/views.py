from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from groq import Groq
from django.db.models import Count
from django.shortcuts import get_object_or_404
from .models import AIQuery, Activity
from django.db.models.functions import TruncDate
from django.conf import settings
from users.models import AIQuery
from django.contrib.auth.decorators import login_required
import re
import random
import requests
from django.contrib import messages
from django.conf import settings



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

        action = request.POST.get('action')


        #
        # SMART AI ACTION SYSTEM
        #

        if action == "generate":

            full_prompt = f"""
        You are an expert coding mentor.

        Generate clean {language} code.

        Student Request:

        {prompt}

       Requirements:

    - Write clean code
    - Add comments
    - Beginner friendly
    - Explain output
    - Follow best practices

    Always return code inside markdown code block.
  """

            activity_text = f"{language} Code Generated"


        elif action == "explain":

            full_prompt = f"""
  You are an expert coding teacher.

  Explain this {language} code line by line.

  Requirements:

  - Explain in Bangla language
  - Keep programming keywords in English
  - Beginner friendly explanation
  - Explain each important line
  - Explain logic
  - Explain output
  - Give overall summary at the end
  - Use simple Bangla that university students can easily understand

  Code:

  {prompt}
  """

            activity_text = f"{language} Code Explained"


        elif action == "debug":

            full_prompt = f"""
You are an expert debugging assistant.

Find problems in this {language} code.

Requirements:

- Detect errors
- Explain why the error happened
- Show corrected code
- Beginner friendly explanation
- Explain expected output

Code:

{prompt}
"""

            activity_text = f"{language} Debug Completed"


        else:

            full_prompt = prompt

            activity_text = "AI Used"


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

                language=language,

                prompt=prompt,

                response=response

            )


            Activity.objects.create(

                user=request.user,

                action=activity_text

            )


        except Exception as e:

            response = f"AI Error: {str(e)}"


    return render(

        request,

        'users/assistant.html',

        {

            'response': response

        }

    )

def register(request):

    if request.method == 'POST':

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if not email.endswith("@manarat.ac.bd"):

            messages.error(request,"Only @manarat.ac.bd email is allowed.")

            return redirect("register")

        # Check existing username

        if User.objects.filter(username=username).exists():

         return render(request, 'users/register.html', {
         'error': 'Username already exists!'})

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        # Save registration data in session
        request.session["reg_username"] = username
        request.session["reg_email"] = email
        request.session["reg_password"] = password
        request.session["otp"] = otp

        # Send OTP using Brevo
        url = "https://api.brevo.com/v3/smtp/email"

        headers = { "accept": "application/json","api-key": settings.BREVO_API_KEY,"content-type": "application/json"}

        data = {
            "sender": {
            "name": settings.BREVO_SENDER_NAME,
            "email": settings.BREVO_SENDER_EMAIL},
            "to": [
                {
                    "email": email
                }],
            "subject": "CampusCoder AI OTP Verification",
            "htmlContent": f"""<h2>CampusCoder AI</h2><p>Your OTP is:</p><h1>{otp}</h1> <p>This OTP is valid for 5 minutes.</p>
             """}

        requests.post(url, headers=headers, json=data)

        return redirect("verify_otp")

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

    #
    # Total Prompts
    #
    total_prompts = AIQuery.objects.filter(
        user=request.user
    ).count()

    #
    # Favorite Count
    #
    favorite_count = AIQuery.objects.filter(
        user=request.user,
        is_favorite=True
    ).count()

    #
    # Most Used Language
    #
    most_used = AIQuery.objects.filter(user=request.user).values('language').annotate(total=Count('language')).order_by('-total').first()

    most_used_language = (
        most_used['language']
        if most_used
        else 'No Data'
    )

    #
    # Real-Time Activities
    #
    recent_activities = Activity.objects.filter(

        user=request.user

    ).order_by('-created_at')[:5]

    #
    # Weekly Prompt Analytics
    #
    weekly_data = AIQuery.objects.filter(

        user=request.user

    ).annotate(

        day=TruncDate('created_at')

    ).values('day').annotate(

        total=Count('id')

    ).order_by('day')

    #
    # Graph Labels + Data
    #
    graph_labels = []

    graph_data = []

    for item in weekly_data:

        graph_labels.append(
            item['day'].strftime("%b %d")
        )

        graph_data.append(
            item['total']
        )

    #
    # Language Analytics
    #
    language_data = AIQuery.objects.filter(

        user=request.user

    ).values('language').annotate(

        total=Count('language')

    )

    language_labels = []

    language_totals = []

    for item in language_data:

        language_labels.append(
            item['language']
        )

        language_totals.append(
            item['total']
        )

    #
    # Final Render
    #
    return render(request, 'users/dashboard.html', {

        'total_prompts': total_prompts,

        'favorite_count': favorite_count,

        'most_used_language': most_used_language,

        'recent_activities': recent_activities,

        'graph_labels': graph_labels,

        'graph_data': graph_data,

        'language_labels': language_labels,

        'language_totals': language_totals,

    })

def favorite_chat(request, chat_id):

    chat = get_object_or_404(
        AIQuery,
        id=chat_id,
        user=request.user
    )

    chat.is_favorite = True

    Activity.objects.create(

         user=request.user,

        action="Added Code To Favorites"

    )

    chat.save()

    return redirect('history')


def visualizer(request):

    return render(

        request,

        'users/visualizer.html'

    )


def logout_view(request):

    logout(request)

    return redirect('login')


@login_required
def roadmap(request):

    technology = ""
    modules = []
    question_list = []

    if request.method == "POST":

        technology = request.POST.get("technology", "").strip()

        prompt = f"""
You are an expert programming instructor.

Create a complete learning roadmap for {technology}.

Rules:

- Exactly 12 modules.
- Only write module titles.
- Do NOT explain anything.
- Format MUST be exactly like this.

Module 1: Introduction

Module 2: Installation

Module 3: Variables

Module 4: Data Types

...

Module 12: Final Project

After Module 12 write:

IMPORTANT QUESTIONS

Then write exactly 20 important interview or exam questions.

Do not write anything else.
"""

        try:

            chat_completion = client.chat.completions.create(

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                model="llama-3.3-70b-versatile",

            )

            result = chat_completion.choices[0].message.content

            # Split Roadmap & Questions
            if "IMPORTANT QUESTIONS" in result:

                roadmap_text, question_text = result.split(
                    "IMPORTANT QUESTIONS",
                    1
                )

            else:

                roadmap_text = result
                question_text = ""

            # Extract Modules
            pattern = r"Module\s*\d+\s*:\s*(.+)"

            matches = re.findall(
                pattern,
                roadmap_text,
                re.IGNORECASE
            )

            modules = []

            for item in matches:

                modules.append(item.strip())

            # Questions
            question_list = []

            for line in question_text.split("\n"):

                line = line.strip()

                if line:

                    question_list.append(line)

        except Exception as e:

            modules = []

            question_list = []

            print(e)

    return render(

        request,

        "users/roadmap.html",

        {

            "technology": technology,

            "modules": modules,

            "question_list": question_list,

        }

    )

@login_required
def module(request):

    technology = request.GET.get("technology", "Python")
    module_name = request.GET.get("module", "")

    lesson = ""
    code = ""
    practice = ""

    prompt = f"""
You are an expert programming teacher.

Technology: {technology}

Module:
{module_name}

Create the lesson in this exact format.

LESSON

Explain the topic in beginner-friendly language.

====================

CODE

Provide one simple code example.

====================

PRACTICE

Give one beginner practice task.

Do not write anything else.
"""

    try:

        chat_completion = client.chat.completions.create(

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            model="llama-3.3-70b-versatile",

        )

        result = chat_completion.choices[0].message.content

        if "====================" in result:

            parts = result.split("====================")

            lesson = parts[0].replace("LESSON", "").strip()

            if len(parts) > 1:
                code = parts[1].replace("CODE", "").strip()

            if len(parts) > 2:
                practice = parts[2].replace("PRACTICE", "").strip()

        else:

            lesson = result

    except Exception as e:

        lesson = str(e)

   

    return render(

        request,

        "users/module.html",

        {

            "technology": technology,
            "module_name": module_name,
            "module_no": 1,
            "lesson": lesson,
            "code": code,
            "practice": practice,
        

        }

    )



def verify_otp(request):

    if request.method == "POST":

        user_otp = request.POST.get("otp")

        session_otp = request.session.get("otp")

        if user_otp == session_otp:

            User.objects.create_user(

                username=request.session["reg_username"],

                email=request.session["reg_email"],

                password=request.session["reg_password"]

            )

            request.session.flush()

            messages.success(
                request,
                "Registration completed successfully."
            )

            return redirect("login")

        else:

            messages.error(
                request,
                "Invalid OTP."
            )

    return render(
        request,
        "users/verify_otp.html"
    )
