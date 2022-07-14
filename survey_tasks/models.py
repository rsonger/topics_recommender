from django.db import models
from django.utils import timezone

class DATResponse(models.Model):
    submitted_at = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self):
        return f"Submitted at {timezone.localtime(self.submitted_at)}"

    class Meta:
        verbose_name = "DAT Response"

class DATWord(models.Model):
    value = models.CharField(max_length=32, blank=False, null=False)
    language_code = models.CharField(max_length=2, null=False, blank=False)
    response = models.ForeignKey(
        DATResponse, 
        related_name="words",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.value

    class Meta:
        verbose_name = "word"