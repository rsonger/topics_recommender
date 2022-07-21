from django.db import models
from django.utils import timezone

from parler.models import TranslatableModel, TranslatedFields

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

class CTTResponse(models.Model):
    submitted_at = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self):
        return f"Submitted at {timezone.localtime(self.submitted_at)}"

    class Meta:
        verbose_name = "CTT Response"

class CTTIdea(TranslatableModel):
    id = models.IntegerField(primary_key=True)
    translations = TranslatedFields(
        content=models.TextField(null=True, blank=True)
    )

    def __str__(self):
        return f"{self.id}. {self.content}"

    class Meta:
        verbose_name = "idea"

class CTTCategory(models.Model):
    title = models.CharField(max_length=64, blank=False, null=False)
    ideas = models.ManyToManyField(
        CTTIdea,
        related_name="categories"
    )
    language_code = models.CharField(max_length=2, null=False, blank=False)
    response = models.ForeignKey(
        CTTResponse,
        related_name="category_titles",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"
