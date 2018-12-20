from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns= [
    path('',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('register/',views.register,name='register'),
    path('login/',views.user_login,name='user_login'),
    path('logout/',views.user_logout,name='logout'),
<<<<<<< HEAD
    path('about/',views.about,name='about'),
    path('youtube/',views.get_youtube,name='youtube'),
=======
>>>>>>> 11c75d75240ef9899c9ec8c272a5982bc0c26d05
    #path('',views.analysis,name='analysis'),
    path('profile/',views.profile_page,name='profile'),
    path('content/',views.content_page,name='content'),
    path('youtube/',views.get_youtube,name='get_youtube'),

    path('user/profile_edit/',views.profile_edit,name='profile_edit'),
    path('user/add_like_dislike/',views.add_like_dislike,name='add_like_dislike'),
    path('user/remove_like_dislike/',views.remove_like_dislike,name='remove_like_dislike'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
