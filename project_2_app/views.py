from django.shortcuts import render, redirect
from project_2_app.forms import UserForm, UserProfileInfoForm
from project_2_app.models import UserProfileInfo, Video, Category, Likes
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
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


# Create your views here.

def index(request): return render(request,'project_2/landing.html')


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


def about(request): return render(request, 'project_2/about.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('index')


@login_required
def content(request): return render(request, 'project_2/content.html',{'video_results':get_video_list(20)})


def get_youtube(request): 
    max_limit= 20
    video_results= get_video_list(max_limit)
    return render(request, 'project_2/youtube.html',{'video_results':video_results})
    

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
                thumbnail_width=data.get("thumbnail_width"),
                thumbnail_height=data.get("thumbnail_height"),
                category=Category.objects.get(category_id=data.get("category_id"))
            )
            v.save()
            this_video = v

        try:
            has_likes= Likes.objects.get(user_id=user_profile.id,video_id=this_video.id)
            #lid= has_likes.id
            message= "duplicated action"
        except ObjectDoesNotExist:

            l= Likes(
                user_id=user_profile,
                video_id=this_video,
                like=data.get("like")
            )
            l.save()
            message= "saved action"
            #lid=l.id
        
        return HttpResponse(json.dumps({"message": message}),content_type="application/json")
    else:
        return HttpResponse(json.dumps({"message": "bad request method"}),content_type="application/json")
    
