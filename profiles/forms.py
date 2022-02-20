from .models import Profile
from django import forms
from django.contrib.auth.models import User


class ProfileModelForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'bio', 'avatar')

