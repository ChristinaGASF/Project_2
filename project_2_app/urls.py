from django.urls import path
from . import views

urlpatterns= [
    path('',views.index,name='index'),
    path('user_login',views.user_login,name='user_login'),
    path('logout',views.user_logout,name='logout'),
]