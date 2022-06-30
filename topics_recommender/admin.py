from django.contrib import admin
from parler.admin import TranslatableAdmin

from topics_recommender.models import Topic, UserSession

# Register your models here.
admin.site.register(Topic, TranslatableAdmin)
admin.site.register(UserSession)