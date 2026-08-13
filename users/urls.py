from django.urls import path
from .views import history, register, login_view, dashboard, logout_view, home, assistant, favorite_chat, visualizer, roadmap, module, verify_otp

urlpatterns = [

    path('roadmap/', roadmap, name='roadmap'),

    path('module/', module, name='module'),

    path('visualizer/', visualizer, name='visualizer'),

    path('history/', history, name='history'),
    
    path('assistant/', assistant, name='assistant'),

    path('', home, name='home'),

    path('register/', register, name='register'),

    path("verify-otp/", verify_otp, name="verify_otp"),

    path('login/', login_view, name='login'),

    path('dashboard/', dashboard, name='dashboard'),

    path('favorite/<int:chat_id>/', favorite_chat, name='favorite_chat'),

    path('logout/', logout_view, name='logout'),
]
