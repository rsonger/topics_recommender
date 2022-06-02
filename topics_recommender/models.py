import uuid
from django.db import models
from django.utils import timezone

class Topic(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    short_description = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    featured = models.BooleanField(default=False)

    def __str__(self):
        if len(self.short_description) > 50:
            return f"{self.display_name} -- {self.short_description[:50]}..."
        else: 
            return f"{self.display_name} -- {self.short_description}"

class UserSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64, blank=True, default="")
    started_at = models.DateTimeField(auto_now_add=True, blank=False)
    finished_at = models.DateTimeField(null=True)

    def __str__(self) -> str:
        blip = f"Started at {timezone.localtime(self.started_at)}"
        if self.name:
            blip = f"{self.name} -- {blip}" 
        return blip

    class Meta:
        verbose_name = "User Session"