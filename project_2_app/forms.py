from django import forms
from project_2_app.models import UserProfileInfo
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):

    email = forms.CharField(max_length=75, required=True)
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password=forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username','email','password')

    def clean(self):
        #cleaned_data = super(UserForm, self).clean()
        cleaned_data = self.cleaned_data
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("passwords do not match")


class UserProfileInfoForm(forms.ModelForm):

    class Meta:
        model = UserProfileInfo
        fields = ('profile_pic',)