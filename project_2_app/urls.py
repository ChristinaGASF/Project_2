from django.urls import path
from . import views

urlpatterns= [
    path('',views.index,name='index'),
    path('register/',views.register,name='register'),
    path('login/',views.user_login,name='user_login'),
    #path('user_signin',views.user_signin,name='user_signin'),
    path('logout/',views.user_logout,name='logout'),
    #path('',views.analysis,name='analysis'),
    #path('',views.profile,name='profile'),
    path('content/',views.content,name='content'),
]