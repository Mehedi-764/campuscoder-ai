from django.urls import path
from .views import history, register, login_view, dashboard, logout_view, home, assistant, favorite_chat

urlpatterns = [

    path('history/', history, name='history'),
    
    path('assistant/', assistant, name='assistant'),

    path('', home, name='home'),

    path('register/', register, name='register'),

    path('login/', login_view, name='login'),

    path('dashboard/', dashboard, name='dashboard'),

    path('favorite/<int:chat_id>/', favorite_chat, name='favorite_chat'),

    path('logout/', logout_view, name='logout'),
]