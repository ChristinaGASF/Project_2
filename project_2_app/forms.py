from django import forms
from project_2_app.models import UserProfileInfo
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):

    email = forms.CharField(max_length=75, required=True)
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username','email','password')

    '''
    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError(u'Email addresses must be unique.')
        return email
    #'''
        


class UserProfileInfoForm(forms.ModelForm):

    class Meta:
        model = UserProfileInfo
        fields = ('profile_pic',)