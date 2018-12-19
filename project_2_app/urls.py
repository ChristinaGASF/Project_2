from django.urls import path
from . import views

urlpatterns= [
    path('',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('register/',views.register,name='register'),
    path('login/',views.user_login,name='user_login'),
    path('logout/',views.user_logout,name='logout'),
    #path('',views.analysis,name='analysis'),
    #path('',views.profile,name='profile'),
    path('content/',views.content,name='content'),
    path('youtube/',views.get_youtube,name='get_youtube'),

    path('add_like_dislike/',views.add_like_dislike,name='add_like_dislike'),
]
