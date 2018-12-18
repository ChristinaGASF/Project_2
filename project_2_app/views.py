from django.shortcuts import render
from .models import Video, Category

# Create your views here.

def video_list(request):
    videos = Video.objects.all()
    return render(request, 'project_2/video_list.html', {'videos': videos})


