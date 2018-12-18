from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.

class UserProfileInfo(models.Model):
    name = models.OneToOneField(User,on_delete=models.CASCADE)
    email = models.CharField(max_length=50)
    profile_pic = models.ImageField(upload_to='profile_pics',blank=True)

    def __str__(self): return self.name.username


class Category(models.Model):
    category_id = models.CharField(max_length=4)
    title = models.CharField(max_length=50)

    def __str__(self): return self.title



class Video(models.Model):
    youtube_id = models.CharField(max_length=20)
    title = models.CharField(max_length=255)
    channel_title = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.TextField()
    thumbnail_url = models.CharField(max_length=100)
    thumbnail_width = models.CharField(max_length=4)
    thumbnail_height = models.CharField(max_length=4)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category')
  
    def __str__(self): return self.title




class Likes(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE,related_name='users')
    video_id = models.ForeignKey(Video,on_delete=models.CASCADE,related_name='videos')
    date = models.DateField(default=datetime.date.today)
    like = models.BooleanField(default=False)
