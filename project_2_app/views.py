from django.shortcuts import render, redirect, get_object_or_404
from project_2_app.forms import UserForm, UserProfileInfoForm
from project_2_app.models import UserProfileInfo, Video, Category, Likes
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, QueryDict, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.db.models import Q
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, EmotionOptions, SentimentOptions, CategoriesOptions, ConceptsOptions
import requests, json, os, re

max_num_youtube_videos = 50
key= os.environ['GOOGLAPI']


## helper functions

# recursive function pagination
def get_youtube_video_helper(video_list,next_page_token,max_limit,cat_id):
    if len(video_list)>=max_limit: return
    
    max_results= 50
    part= 'snippet,contentDetails,statistics'
    orderby= 'viewCount'

    base_url= 'https://www.googleapis.com/youtube/v3/videos?part='+part+'&regionCode=US&maxResults='+str(max_results)+'&chart=mostPopular&order='+orderby+'&key='+key

    if cat_id!=-1:
        base_url+= '&videoCategoryId='+str(cat_id)

    if next_page_token != '':
        base_url+= '&pageToken='+next_page_token
    
    res = requests.get(base_url)
    if res.status_code!=200: return
    
    json_res= res.json()
    next_page_token= json_res.get('nextPageToken') if json_res.get('nextPageToken') else ''
    videos= json_res.get('items')
    video_list.extend(videos)
    if next_page_token=='': return 

    get_youtube_video_helper(video_list,next_page_token,max_limit,cat_id)


# get video list 
def get_video_list(max_limit,cat_id):
    video_list= []
    get_youtube_video_helper(video_list,'',max_limit,cat_id)    
    
    video_results= []
    for video in video_list:
        yid= video.get('id')
        snippet= video.get('snippet')
        title= snippet.get('title')
        descrp= snippet.get('description')
        thumbnail= snippet.get('thumbnails').get('standard')
        channel_title= snippet.get('channelTitle')
        tags= ', '.join(snippet.get('tags')) if snippet.get('tags') else ''
        cat_id= snippet.get('categoryId')
        video_results.append({'youtube_id': yid, 'title': title,'description': descrp,'thumbnail': thumbnail,'channel_title': channel_title,'tags': tags,'category_id': cat_id})    
    return video_results

## get youtube category list
def get_youtube_category_list(url):
    res = requests.get(url)
    category = []
    for cat in res.json().get('items'):
        category.append({'category_id': cat.get('id'),'title':cat.get('snippet').get('title')})
    return category



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

    
## register
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
            else:
                profile.profile_pic = 'profile_pics/user_default.png'
            profile.save()
            registered = True
            login(request,new_user)
            return redirect('content')
        else:
            print(user_form.errors,profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()
    return render(request, 'project_2/register.html', {'user_form':user_form,'profile_form':profile_form,'registered':registered})


## user login
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
            #print(f"Someone tried to login and failed...\nattempted: username: {username} and password: {'#' * len(password)}")
            return render(request, 'project_2/login.html', {})
    else:
        return render(request, 'project_2/login.html', {})



##### ===== LOGIN_REQUIRED VIEWS ===== #####

## user logout
@login_required
def user_logout(request):
    logout(request)
    return redirect('index')


## display content
@login_required
def content_page(request): 
    url = 'https://www.googleapis.com/youtube/v3/videoCategories?part=snippet&regionCode=US&key='+key
    categories = get_youtube_category_list(url)
    return render(request, 'project_2/content.html',{'video_results':get_video_list(max_num_youtube_videos,-1),'categories':categories})


## profile page
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
        'user_dislikes_videos':user_dislikes_videos,
    })


## analysis page
@login_required
def analysis(request):
    watson_text= ''
    user = request.user.userprofileinfo
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT v.channel_title,v.title,v.tags, v.description
        FROM project_2_app_video v
        WHERE v.id IN
            (SELECT video_id_id FROM project_2_app_likes WHERE user_id_id=%s);
        """,[str(user.id)])
        records= cursor.fetchall()
        
        for row in records:
            row= list(row)
            watson_text+= ' '.join(row)

        pattern = re.compile(r'\s+')
        replace_words = ['https://','http://',':','/','&amp;','www.','.com']
        for r in replace_words: 
            watson_text = watson_text.replace(r,' ')
        watson_text = re.sub(pattern, ' ',watson_text)
        watson_response = watson_nlp_analysis(watson_text)
        result = json.dumps(watson_response,indent=2) if watson_response!='' else ''

    return render(request,'project_2/analysis.html',
        {'watson_text':watson_text,'watson_response':result})



##### ===== API VIEWS ===== #####

## edit profile
@login_required
def profile_edit(request):
    if request.method == 'PATCH':
        # update email
        email = json.loads(request.body).get('email')
        with connection.cursor() as cursor:
            cursor.execute("UPDATE AUTH_USER SET email=%s WHERE id=%s;",[email,str(request.user.id)])
            row = cursor.rowcount
            if row>0: 
                return HttpResponse(json.dumps({"message":"email edited"}),content_type="application/json")
            else:
                return HttpResponseNotFound(json.dumps({"message": "record not found"}),content_type="application/json")
    
    elif request.method == 'POST':
        # update profile_pic
        current_user = get_object_or_404(UserProfileInfo,id=request.user.userprofileinfo.id)
        current_user.profile_pic = request.FILES.get('image')
        current_user.save()

        return HttpResponse(json.dumps({"message":"pic edited","img_url":current_user.profile_pic.url}),content_type="application/json")
    else:
        return HttpResponseBadRequest(json.dumps({"message": "bad request method"}),content_type="application/json")


## get videos across all categories
@login_required
def videos_all_categories(request): 
    if request.method == 'GET':
        return HttpResponse(json.dumps({"video_results":get_video_list(max_num_youtube_videos,-1)}),content_type="application/json")
    else:
        return HttpResponseBadRequest(json.dumps({"message": "bad request method"}),content_type="application/json")


## get videos from specific category
@login_required
def videos_selected_category(request):
    if request.method == 'GET':
        return HttpResponse(json.dumps({"video_results":get_video_list(max_num_youtube_videos,request.GET.get('cat_id'))}),content_type="application/json")
    else:
        return HttpResponseBadRequest(json.dumps({"message": "bad request method"}),content_type="application/json")


## remove likes / dislikes
@login_required
def remove_like_dislike(request):
    if request.method == 'DELETE':
        user_profile_id = request.user.userprofileinfo.id
        youtube_id = QueryDict(request.body).get('youtube_id')
        
        with connection.cursor() as cursor:
            cursor.execute("""
              DELETE FROM PROJECT_2_APP_LIKES
              WHERE id=(
                SELECT L.id FROM PROJECT_2_APP_VIDEO V, PROJECT_2_APP_LIKES L WHERE V.youtube_id=%s AND L.user_id_id= %s AND L.video_id_id=V.id);"""
                ,[youtube_id,str(user_profile_id)])
            row = cursor.rowcount
            
            if row>0: 
                return HttpResponse(json.dumps({"message": "successfully deleted"}),content_type="application/json")
            else: 
                return HttpResponseNotFound(json.dumps({"message": "record not found"}),content_type="application/json")
        
    else:
        return HttpResponseBadRequest(json.dumps({"message": "bad request method"}),content_type="application/json")


## add likes / dislikes
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
                category=data.get("category_id")
            )
            v.save()
            this_video = v

        try:
            has_likes= Likes.objects.get(user_id=user_profile.id,video_id=this_video.id)
            message= "duplicated"
        except ObjectDoesNotExist:

            l= Likes(
                user_id=user_profile,
                video_id=this_video,
                like=data.get("like")
            )
            l.save()
            message= "saved"
        return HttpResponse(json.dumps({"message": message}),content_type="application/json")
    else:
        return HttpResponseBadRequest(json.dumps({"message": "bad request method"}),content_type="application/json")
    
## call watson api
def watson_nlp_analysis(text):

    if text=='': return text

    max_limit_one= 10
    max_limit_two= 30

    naturalLanguageUnderstanding = NaturalLanguageUnderstandingV1(
        version = '2018-11-16',
        iam_apikey = os.environ['WATSON'],
        url = 'https://gateway.watsonplatform.net/natural-language-understanding/api')

    response = naturalLanguageUnderstanding.analyze(
        text= text,
        features=Features(
            concepts=ConceptsOptions(limit=max_limit_one),
            categories=CategoriesOptions(limit=max_limit_one),
            sentiment=SentimentOptions(document=True),
            emotion=EmotionOptions(document=True),
            entities=EntitiesOptions(emotion=True, sentiment=True, limit=max_limit_two),
            keywords=KeywordsOptions(emotion=True, sentiment=True, limit=max_limit_two))
        ).get_result()
    return response
