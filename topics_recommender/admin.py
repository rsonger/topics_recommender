from django.contrib import admin
from .models import Topic, UserSession

# Register your models here.
admin.site.register(Topic)
admin.site.register(UserSession)