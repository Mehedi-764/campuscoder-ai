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

- Beginner friendly explanation
- Explain each important line
- Explain logic
- Explain output
- Give overall summary

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
    most_used = AIQuery.objects.filter(
        user=request.user
    ).values('language').annotate(
        total=Count('language')
    ).order_by('-total').first()

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