from django.urls import path
from .views import history, register, login_view, dashboard, logout_view, home, assistant

urlpatterns = [

    path('history/', history, name='history'),
    
    path('assistant/', assistant, name='assistant'),

    path('', home, name='home'),

    path('register/', register, name='register'),

    path('login/', login_view, name='login'),

    path('dashboard/', dashboard, name='dashboard'),

    path('logout/', logout_view, name='logout'),
]