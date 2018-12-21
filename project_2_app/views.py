from django.shortcuts import render, redirect, get_object_or_404
from project_2_app.forms import UserForm, UserProfileInfoForm
from project_2_app.models import UserProfileInfo, Video, Category, Likes
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, QueryDict, JsonResponse
from django.contrib.auth.decorators import login_required
#import requests, json
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.db.models import Q
import requests, json, os
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 \
import Features, EntitiesOptions, KeywordsOptions, EmotionOptions, SentimentOptions, CategoriesOptions, ConceptsOptions
#from project_2_app.watson_api import watsonResponse

key= ''

## helper functions

# recursive function pagination
def get_youtube_video_helper(video_list,next_page_token,max_limit,cat_id):
    if len(video_list)>=max_limit: return
    
    max_results= 10
    part= 'snippet,contentDetails,statistics'
    orderby= 'viewCount'

    base_url= 'https://www.googleapis.com/youtube/v3/videos?part='+part+'&regionCode=US&maxResults='+str(max_results)+'&chart=mostPopular&order='+orderby+'&key='+key

    if cat_id!=-1:
        base_url+= '&videoCategoryId='+str(cat_id)

    if next_page_token != '':
        base_url+= '&pageToken='+next_page_token
    
    res = requests.get(base_url)
    print('res= ',res.status_code)
    if res.status_code!=200: return
    
    json_res= res.json()
    next_page_token= json_res.get('nextPageToken') if json_res.get('nextPageToken') else ''
    print ('next_page_token= ',next_page_token)
    videos= json_res.get('items')
    video_list.extend(videos)
    if next_page_token=='': return 

    get_youtube_video_helper(video_list,next_page_token,max_limit,cat_id)


# get video list 
def get_video_list(max_limit,cat_id):
    video_list= []
    get_youtube_video_helper(video_list,'',max_limit,cat_id)    
    print(len(video_list))

    video_results= []
    for video in video_list:
        yid= video.get('id')
        snippet= video.get('snippet')
        title= snippet.get('title')
        descrp= snippet.get('description')
        thumbnail= snippet.get('thumbnails').get('maxres')
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
def get_youtube(request): return render(request, 'project_2/youtube.html',{'video_results':get_video_list(20,-1)})
    
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
            print(f"Someone tried to login and failed...\nattempted: username: {username} and password: {'#' * len(password)}")
            return render(request, 'project_2/login.html', {})
    else:
        return render(request, 'project_2/login.html', {})



### LOGIN_REQUIRED VIEWS ###

## user logout
@login_required
def user_logout(request):
    logout(request)
    return redirect('index')


## display content
@login_required
def content_page(request): 
    categories = []
    for cat in Category.objects.all():
        categories.append({'category_id':cat.category_id,'title':cat.title})
    return render(request, 'project_2/content.html',{'video_results':get_video_list(20,-1),'categories':categories})


@login_required
def videos_all_categories(request): 
    if request.method == 'GET':
        return HttpResponse(json.dumps({"video_results":get_video_list(20,-1)}),content_type="application/json")
    else:
        return HttpResponseBadRequest(json.dumps({"message": "bad request method"}),content_type="application/json")

@login_required
def videos_selected_category(request):
    if request.method == 'GET':
        return HttpResponse(json.dumps({"video_results":get_video_list(20,request.GET.get('cat_id'))}),content_type="application/json")
    else:
        return HttpResponseBadRequest(json.dumps({"message": "bad request method"}),content_type="application/json")


## profile page
@login_required
def profile_page(request):
    user_likes_videos, user_dislikes_videos= [], []
    user_id = request.user.userprofileinfo.id
    likes_list= Likes.objects.filter(user_id=user_id,like=True)
    dislikes_list= Likes.objects.filter(user_id=user_id,like=False)
    append_likes_dislikes_videos_list(likes_list,user_likes_videos)
    append_likes_dislikes_videos_list(dislikes_list,user_dislikes_videos)
    print('host:',request.get_host())
    return render(request, 'project_2/profile.html',{
        'user_likes_videos':user_likes_videos,
        'user_dislikes_videos':user_dislikes_videos,
        'base_url': request.get_host()
    })


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

        return HttpResponse(json.dumps({"message":"pic edited"}),content_type="application/json")
    else:
        return HttpResponseBadRequest(json.dumps({"message": "bad request method"}),content_type="application/json")


### API VIEWS ###

## remove likes / dislikes
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
        print('yid=',yid)
        try:
            has_video = Video.objects.get(youtube_id=yid)
            print('has_video')
            this_video = has_video
        except ObjectDoesNotExist:
            
            print('data= ',data)
            print('data_title= ',data.get("title"))
            
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
 

def get_data(request):
    # response = watsonResponse
    # return JsonResponse(response)
    text = "A Beginner’s Guide to Sous Vide Cooking- Kitchen Conundrums with Thomas JosephA Recap of Bill Burr's Best Interview Moments of 2018 Sources:- Sara Silverman:- https://www.youtube.com/watch?v=i-VU25UfHWM Comic Con:- https://www.youtube.com/watch?v=JOVWum1vv4Y&t=8s The Herd...ABC NewsAcaiadam22Adam22 GOES IN on Corny Rapper who paid to be on WorldstarAden FilmsAmerican Football - TopicAndrea Savage on Husband's Tank Top, Daughter & Her Mom's Bizarre Holiday TraditionsApple Killed the Mac Mini.April Fools' Day Pranks with Mark RoberAwkward Bill Burr vs Sarah Silverman InterviewBaked Lemon Chicken with Garlic Lemon Cream Sauce | Oven Baked Chicken RecipeBaked Potato Puffs - Food WishesBaking - TopicBash: How can that come out of Sarah Sanders' mouth?Beastie Boys, Nas - Too Many RappersBeastieBoysBernie Sanders Assesses The 2020 Presidential FieldBest Ever Food Review ShowBest web features of 2018: Part 2/4 - HTTP203Bill Burr | Best of 2018 | A Year In ReviewBinging with BabishBinging with BabishBinging with BabishBINGING WITH BABISH  S1 • E78BINGING WITH BABISH  S2 • E30Binging with Babish: Chateaubriand Steak from The MatrixBinging with Babish: Roast Beast from How The Grinch Stole ChristmasBinging with Babish: Seinfeld Volume IIBlockchain Takes ManhattanBloombergBon AppétitBoy's emotional Christmas surprise goes viralBrexit (2019) | Official Trailer | HBOBrexit Update - UK Version: Last Week Tonight with John Oliver (HBO)BroadlyBroncos vs. 49ers Week 14 Highlights | NFL 2018BuzzFeedVideoBuzzFeedVideo viewers also watch...Cal McKinley - Go LocalCan a Millennial Troll Survive NATO's Biggest War Games?Cardi B Carpool KaraokeCarFactionCars - TopicCFP RankingsCHAMPAIGN ILL  S1 • E1Champaign ILL - Ep 1 “A Gangster Way To Start Your Day”Check out original movies and series from YouTube Creators and moreChicken Noodle Soup - How to Make Classic Chicken Noodle SoupChinese Girl Visits Amish Country - She Was Shocked!CHRISTMAS RECIPE: Honey Glazed Ham With Pear & Saffron ChutneyCNNCNNCNNCNNCNNCNNCNNCNNCobra KaiCOBRA KAI  S1 • E1Cobra Kai Ep 1 - “Ace Degenerate” - The Karate Kid Saga ContinuesComedians 'R' GoComedy - TopicComedy CentralComedy Central Stand-UpComedy UniversityComedy UniversityComplexComputerphileCONAN On TBS Returns January 22ndContinue watchingCooking - TopicCS50CS50 Lecture by Steve BallmerDALLAS & ROBO  S1 • E1Daniel Solves Your Local Twissues - Tosh.0Day In The Life Of A Software Engineer | Weekend EditionDMX Ends 6ix9ine With Insane FreestyleDoes Mick Mulvaney Like Donald Trump? 'No'Doug DeMuroDoug DeMuroEaterEaterEMOJOIE CUISINEEngineering ExplainedEp 1 - Dallas & Robo Aces WildEpicuriousESPNEveryday FoodFOOD INSIDERFOOD INSIDERFood Truck Serves 3,000 Grilled Cheese Sandwiches A DayFood WishesFood WishesFood WishesFood WishesFood WishesFood WishesFood Wishes viewers also watch...Free episodeFree episodeFree episodeFree episodeFreethinkFrench Cooking AcademyFrom your subscriptionsGeorge W. BushGetting High over Tea with Natasha Leggero and Moshe KasherGochujang MamáGoogle Chrome DevelopersGordon RamsayGrilled Greek Chicken - Garlic, Lemon & Herb Grilled Chicken RecipeHBOHere's Why the Bugatti Veyron Is the Coolest Car of the 2000sHey Laowinners! My Chinese wife has heard of Amish people before, but she never knew she would have a chance to visit them at some point. She was fascinated by their way of life, and how they don'...Hip Hop Music - TopicHomemade Meatloaf Recipe - Laura Vitale - Laura in the Kitchen Episode 552HOW - TO  S1 • E2How Newark Got Lead In Its Water, And What It Means For The Rest Of America (HBO)How to cook a ALL AMERICAN THANKSGIVINGHow to cook a CHRISTMAS FEASTHow to cook a HANGOVER CURE FEASTHow to cook a SUPER SAIYAN FEASTHow To Cook the Perfect Prime Rib RoastHow to Make Danish Christmas Rice PuddingHow To Make Pot Au Feu: the mother recipe of French soups ( Tutorial for beginners)How To Make Scones | Jamie Oliver | ADI Design A Website In Less Than 1 Hour! | Web Design Challenge | Web Design Guide | mmtutsInstant Pot Roast (Best Ever - Literally)Is the Instant Pot Worth It? — The Kitchen Gadget Test ShowJamie OliverJason Momoa Hasn't Seen Aquaman Yet! | The Graham Norton ShowJeff Ross & David Attell Roast Kimmel AudienceJeff Ross Talks to Mexican Immigrants Deported from America - Jeff Ross Roasts the BorderJerry Seinfeld: Kevin Hart Is ‘Going To Be Fine’ After Oscars Fallout | TODAYJimmy Kimmel LiveJimmy Kimmel LiveJimmy Kimmel LiveJimmy Kimmel LiveJimmy Kimmel LiveJimmy Kimmel LiveJimmy Kimmel LiveJimmy Kimmel LiveJimmy O. Yang's Crazy Tinder DateJoe Rogan - Anthony Cumia on Artie LangeJoe Rogan - Ted Nugent is a Good Guy!Joe Rogan | Can You Get Salmonella From Eating Eggs?Joe Rogan Experience #1216 - Sir Roger PenroseJoe Rogan Shares Crazy Baboon StoriesJoe Rogan: Weasels are Badass!Joe Rogan's Hilarious Jennifer Lopez RantJoe Wong: Building A Wall Didn't Work For ChinaJoin me on my day in a life on a weekend during Halloween and Pumpkin season! ❤ Luba Music by Chillhop: http://chillhop.com/listen Birocratic - Tony's Belated Breakfast: https://soundcloud.com/bi...JRE ClipsJRE ClipsJRE ClipsJRE ClipsJRE ClipsJRE ClipsJRE ClipsJudge asks prosecutors: Could Flynn have been charged with treason?Judge delays Michael Flynn sentencing after blistering rebukeJWoww Gets Estranged Husband Booted From Home | TMZ LiveKansas City, MO Blizzard Impacts Region - 11/25/2018Kanye West - Glastonbury 2015 (Full Show HD)Kodak Black - TestimonyKyle Shanahan 'Nick Mullens Has Shown He Can Play QB in this League' | San Francisco 49ersKyle Shanahan 'Yesterday was Nick Mullens' Best Game' | San Francisco 49erslaowhy86laowhy86LastWeekTonightLate Night with Seth MeyersLate Night with Seth MeyersLaura in the KitchenLife of LubaLife of LubaLinus Tech TipsLinus Tech TipsLinus Tech TipsLinus Tech TipsLIVE NOWLive! 49ers vs Broncos NFL 2018 Week 14 PredictionsLOBSTER BEACH BBQ! And Unique Kenyan Street Food in Malindi, Kenya!Mark WiensMark WiensMark WiensMashedMistakes Everyone Makes Using The Slow CookermmtutsMOVING UPSTREAM  S2 • E1MunchiesNancy And Chuck Are: Democrats On The OffensiveNew York Cheesecake RecipeNFLNFL 2018-19 Week 14 Denver Broncos -- San Francisco 49ersNFL Full Games 2018 / 2019No CloutNot a Very Merry Christmas for Donald TrumpOFFICIAL TRAILER | Ryan Hansen Solves Crimes on Television* Season 2Penny Marshall dead at 75Pilot - (Ep 1)Popular uploadsPopulist Revolution - Will It Go Left Or Right? - Candace Owens & Russell BrandPowerfulJREPremiumPremiumPremiumPremiumPressure LuckPRIME TIME  S1 • E16Priya Makes Pav Bhaji | From the Test Kitchen | Bon AppétitQuang TranQuang TranQuang TranQuang TranRARE Noodles of Saigon, Vietnam! All the Best Hidden Noodles You've Never Seen!Recently uploadedRecommendedRecommended channel for youRecommended channel for youRecommended channel for youRecommended channel for youRecommended channel for youRecommended channel for youRecommended videos for youRecommended videos for youRecommended videos for youRecommended videos for youRecommended videos for youRecommended videos for youRecommended videos for youRecommended videos for youRecommended videos for youRecommended videos for youRecommended videos for youRecommended videos for youRecommended videos for youRED CARDS  S1 • E6reflectivehatemoshRiFF RAFF Teal Tone Lobster (WSHH Exclusive - Official Music Video)Rivian R1T (2020) - World's First Electric PickUp TruckRoadieRon Burgundy Interviews Peyton Manning | SportsCenter | ESPN ArchivesRonbo SportsRussell BrandRYAN HANSEN SOLVES CRIMES ON TELEVISION  S1 • E1Ryan Hansen Solves Crimes on Television*Ryan Hansen Solves Crimes on Television*Ryan Hansen Solves Crimes on Television*Ryan Hansen Solves Crimes on Television* - OFFICIAL TRAILERRyan Reynolds Has Had Enough of 'Frozen'San Francisco 49ersSan Francisco 49ersSarah Sanders asked why Michael Flynn isn't a 'rat'Saturday Night Live viewers also watch...Seth MacFarlane on His Childhood Cartoons & Family GuySeth MacFarlane Smoked Weed with His ParentsShannon FRUSTRATED Packers LOSS TO Bears 17-24; Aaron Rodgers 35-42, 274 Yds, Int✦ NFL Gameday PrimeSicilian Christmas Pizza (Sfincione) - Food WishesSICKO MODE but I don't think I got the right versionSlow Cooker Beef Pot Roast Recipe - How to Make Beef Pot Roast in a Slow CookerSNL star Pete Davidson appears on camera hours after disturbing postSpanish Garlic Soup - Sopa de Ajo Recipe - Bread and Garlic SoupSteak - TopicStephen Miller and Rudy Giuliani Try to Defend Trump: A Closer LookStephen Miller Has A Bad Hair DayStormChasingVideoStreamed 1 week agoStreet FoodStreet food - TopicStreet Food in Gilgit + PAKISTANI VILLAGE FOOD | Ultra Happiness in Gilgit-Baltistan, Pakistan!SZECHUAN Seafood EXTREME - INSANE Chinese Seafood TOUR in Chengdu, China - SPICY CHINESE SEAFOOD!!!T-ROY COOKSTalk Shows - TopicTasting the World’s First Test-Tube SteakTeam CocoThai Street Food - Street Food Thailand - Street Food BangkokThe 2019 Bentley Continental GT Is a $250,000 Ultra-Luxury CoupeThe Best Cheesesteak In Philadelphia | Best Of The BestThe Daily Show with Trevor NoahThe Food RangerThe Garage Converting Classic Cars to Electric Vehicles | Freethink DIY ScienceThe Graham Norton ShowTHE KITCHEN GADGET TEST SHOW  S1 • E7The Late Late Show with James CordenThe Late Show with Stephen ColbertThe Late Show with Stephen ColbertThe Late Show with Stephen ColbertThe Late Show with Stephen ColbertThe Late Show with Stephen ColbertThe Late Show with Stephen ColbertThe Late Show with Stephen ColbertThe Mueller Russia investigation's key players: Michael Cohen, Michael Flynn and Paul ManafortThe President Is Facing 17 InvestigationsThe Roast of Donald Trump (2011) FullThe Secrets Behind New York's Most Famous Spicy Noodle Dish — Prime TimeThe Troubling Death of an NBA HopefulTheEllenShowThis 3D Printed Rotary Engine Is Genius - Mazda RX-7This guy should get FIRED!! - $1500 Gaming PC Secret Shopper pt3TigerBellyClipsTMZLiveTODAYTrump's Boarder Tweet, the White House Christmas Reception - MonologueTrump’s New Chief of Staff & Stephen Miller’s New Hairline | The Daily ShowUnique Food in Baltistan - 14 TRADITIONAL DISHES in Skardu | Pakistani Food in Gilgit-Baltistan!Urban Stealth Truck Camping 2.0Vanilla custard cream filled doughnut | Honeykki 꿀키VICEVICE NewsVICE SportsWall Street JournalWe Stole Tampons from the Cashier-less Amazon Go StoreWhat's your Favourite Programming Language? (sound check Q) - ComputerphileWORLDSTARHIPHOPWORTH IT  S5 • E8YouTube OriginalsYouTube OriginalsYouTube Originals"

    naturalLanguageUnderstanding = NaturalLanguageUnderstandingV1(
    version='2018-11-16',
    iam_apikey='',
    url='https://gateway.watsonplatform.net/natural-language-understanding/api')

    response = naturalLanguageUnderstanding.analyze(
    text= text,
    features=Features(
        concepts=ConceptsOptions(limit=10),
        categories=CategoriesOptions(limit=10),
        sentiment=SentimentOptions(document=True),
        emotion=EmotionOptions(document=True),
        entities=EntitiesOptions(emotion=True, sentiment=True, limit=30),
        keywords=KeywordsOptions(emotion=True, sentiment=True, limit=30))).get_result()


    print(json.dumps(response, indent=2))
    return JsonResponse(response)


def charts(request, *args, **kwargs):
        return render(request, 'project_2/charts.html',{})