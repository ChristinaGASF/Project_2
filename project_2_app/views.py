from django.shortcuts import render, redirect
from project_2_app.forms import UserForm, UserProfileInfoForm
from project_2_app.models import UserProfileInfo, Video, Category, Likes
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, QueryDict
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.db.models import Q
import requests, json, os


key= os.environ['GOOGLAPI']

## helper functions

# recursive function pagination
def get_youtube_video_helper(video_list,next_page_token,max_limit):
    if len(video_list)>=max_limit: return
    
    max_results= 10
    part= 'snippet,contentDetails,statistics'
    orderby= 'viewCount'

    base_url= 'https://www.googleapis.com/youtube/v3/videos?part='+part+'&regionCode=US&maxResults='+str(max_results)+'&chart=mostPopular&order='+orderby+'&key='+key

    if next_page_token != '':
        base_url+= '&pageToken='+next_page_token
    elif next_page_token=='' and len(video_list)>0: 
        return

    res = requests.get(base_url)
    json_res= res.json()
    next_page_token= json_res.get('nextPageToken') if json_res.get('nextPageToken') else ''
    videos= json_res.get('items')
    video_list.extend(videos)

    get_youtube_video_helper(video_list,next_page_token,max_limit)


# get video list 
def get_video_list(max_limit):
    video_list= []
    get_youtube_video_helper(video_list,'',max_limit)    
    print(len(video_list))

    video_results= []
    for video in video_list:
        yid= video.get('id')
        snippet= video.get('snippet')
        title= snippet.get('title')
        descrp= snippet.get('description')
        thumbnail= snippet.get('thumbnails').get('default')
        channel_title= snippet.get('channelTitle')
        tags= ', '.join(snippet.get('tags')) if snippet.get('tags') else ''
        cat_id= snippet.get('categoryId')
        #print(yid,'\n',title,'\n',descrp,'\n',thumbnail,'\n',channel_title,'\n',tags,'\n',cat_id)
        video_results.append({'youtube_id': yid, 'title': title,'description': descrp,'thumbnail': thumbnail,'channel_title': channel_title,'tags': tags,'category_id': cat_id})    
    return video_results


# save likes/dislikes to lists
def append_likes_dislikes_videos_list(likes_dislikes_list,result_list):
    for like in likes_dislikes_list:
        video= Video.objects.get(title=like.video_id)
        result_list.append({
            'youtube_id': video.youtube_id,
            'title': video.title,
            'channel_title': video.channel_title,
            'description': video.description,
            'tags': video.tags,
            'thumbnail_url': video.thumbnail_url,
            'category': video.category
        })



# Create your views here.

## index
def index(request): return render(request,'project_2/landing.html')

## about
def about(request): return render(request, 'project_2/about.html')

## get youtube videos
def get_youtube(request): return render(request, 'project_2/youtube.html',{'video_results':get_video_list(20)})
    


def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            new_user = user_form.save()
            new_user.set_password(new_user.password)
            new_user.save()
            profile = profile_form.save(commit=False)
            profile.name = new_user
            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']
            profile.save()
            #print('profile: ',profile)
            registered = True
            #print('NEWUSER: ',new_user)
            login(request,new_user)
            return redirect('content')
        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()
    return render(request, 'project_2/register.html', {'user_form':user_form,'profile_form':profile_form,'registered':registered})


def user_login(request):
    if request.method == 'POST':
        username,password = request.POST.get('username'),request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request,user)
                return redirect('content')
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print(f"Someone tried to login and failed...\nattempted: username: {username} and password: {'#' * len(password)}")
            return render(request, 'project_2/login.html', {})
    else:
        return render(request, 'project_2/login.html', {})



### LOGIN_REQUIRED VIEWS ###

@login_required
def user_logout(request):
    logout(request)
    return redirect('index')


@login_required
def content_page(request): return render(request, 'project_2/content.html',{'video_results':get_video_list(20)})


@login_required
def profile_page(request):
    user_likes_videos, user_dislikes_videos= [], []
    user_id = request.user.userprofileinfo.id
    likes_list= Likes.objects.filter(user_id=user_id,like=True)
    dislikes_list= Likes.objects.filter(user_id=user_id,like=False)
    append_likes_dislikes_videos_list(likes_list,user_likes_videos)
    append_likes_dislikes_videos_list(dislikes_list,user_dislikes_videos)
    
    return render(request, 'project_2/profile.html',{
        'user_likes_videos':user_likes_videos,
        'user_dislikes_videos':user_dislikes_videos
    })


@login_required
def profile_edit(request):
    if request.method == 'PATCH':

        email = json.loads(request.body).get('email')
        with connection.cursor() as cursor:
            cursor.execute("UPDATE AUTH_USER SET email=%s WHERE id=%s;",[email,str(request.user.id)])
            row = cursor.rowcount
            if row>0: 
                return HttpResponse(json.dumps({"message":"edited"}),content_type="application/json")
            else:
                return HttpResponseNotFound(json.dumps({"message": "record not found"}),content_type="application/json")
    else:

        return HttpResponseBadRequest(json.dumps({"message": "bad request method"}),content_type="application/json")



@login_required
def remove_like_dislike(request):
    if request.method == 'DELETE':
        user_profile_id = request.user.userprofileinfo.id
        #user_profile_id = 36
        youtube_id = QueryDict(request.body).get('youtube_id')
        
        with connection.cursor() as cursor:
            cursor.execute("""
              DELETE FROM PROJECT_2_APP_LIKES
              WHERE id=(
                SELECT L.id
                FROM PROJECT_2_APP_VIDEO V, PROJECT_2_APP_LIKES L
                WHERE V.youtube_id='"""+youtube_id+"""'
                  AND L.user_id_id="""+str(user_profile_id)+"""
                  AND L.video_id_id=V.id);
            """)
            row = cursor.rowcount
            
            if row>0: 
                return HttpResponse(json.dumps({"message": "successfully deleted"}),content_type="application/json")
            else: 
                return HttpResponseNotFound(json.dumps({"message": "record not found"}),content_type="application/json")
        
    else:
        return HttpResponseBadRequest(json.dumps({"message": "bad request method"}),content_type="application/json")

@login_required
def add_like_dislike(request):
    if request.method == 'POST':
        user_profile = request.user.userprofileinfo
        data = request.POST
        yid = data.get("youtube_id")
        try:
            has_video = Video.objects.get(youtube_id=yid)
            this_video = has_video
        except ObjectDoesNotExist:
            v = Video(
                youtube_id=yid,
                title=data.get("title"),
                channel_title=data.get("channel_title"),
                description=data.get("description"),
                tags=data.get("tags"),
                thumbnail_url=data.get("thumbnail_url"),
                category=Category.objects.get(category_id=data.get("category_id"))
            )
            v.save()
            this_video = v

        try:
            has_likes= Likes.objects.get(user_id=user_profile.id,video_id=this_video.id)
            #lid= has_likes.id
            message= "duplicated"
        except ObjectDoesNotExist:

            l= Likes(
                user_id=user_profile,
                video_id=this_video,
                like=data.get("like")
            )
            l.save()
            message= "saved"
            #lid=l.id
        
        return HttpResponse(json.dumps({"message": message}),content_type="application/json")
    else:
        return HttpResponseBadRequest(json.dumps({"message": "bad request method"}),content_type="application/json")
    
