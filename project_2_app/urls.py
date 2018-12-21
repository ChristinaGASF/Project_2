from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


#urlpatterns= []
#'''
urlpatterns= [
    
    path('',views.index,name='index'),
    path('about/',views.about,name='about'),
    path('register/',views.register,name='register'),
    path('login/',views.user_login,name='user_login'),
    path('logout/',views.user_logout,name='logout'),
    path('profile/',views.profile_page,name='profile'),
    path('content/',views.content_page,name='content'),
    path('analysis/',views.analysis,name='analysis'),

    path('user/profile_edit/',views.profile_edit,name='profile_edit'),
    path('user/add_like_dislike/',views.add_like_dislike,name='add_like_dislike'),
    path('user/remove_like_dislike/',views.remove_like_dislike,name='remove_like_dislike'),

    path('video/category_all/',views.videos_all_categories,name='videos_all_categories'),
    path('video/category_selected/',views.videos_selected_category,name='videos_selected_category'),
]
#'''