from django import forms
from django.utils.translation import gettext_lazy as _

from topics_recommender.models import UserSession

class LoginForm(forms.ModelForm):
    class Meta:
        model = UserSession
        fields = [_('name')]
        labels = {_('name'): _('Please enter a nickname:')}