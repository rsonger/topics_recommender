from django import forms

from topics_recommender.models import UserSession

class LoginForm(forms.ModelForm):
    class Meta:
        model = UserSession
        fields = ['name']
        labels = {'name': 'Please enter a nickname:'}