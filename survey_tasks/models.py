from django.db import models
from django.utils import timezone

from parler.models import TranslatableModel, TranslatedFields

from topics_recommender.models import UserSession, Topic

class RecommenderResponse(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    submitted_at = models.DateTimeField(auto_now=True, blank=False)
    user_session = models.ForeignKey(
        UserSession,
        on_delete=models.CASCADE
    )
    topic1 = models.ForeignKey(
        Topic,
        related_name="choice1",
        verbose_name="Topic 1",
        on_delete=models.CASCADE
    )
    topic2 = models.ForeignKey(
        Topic,
        related_name="choice2",
        verbose_name="Topic 2",
        on_delete=models.CASCADE
    )
    topic3 = models.ForeignKey(
        Topic,
        related_name="choice3",
        verbose_name="Topic 3",
        on_delete=models.CASCADE
    )
    sim_score_1_2 = models.FloatField(null=True, verbose_name="Similarity of Topics 1 & 2")
    sim_score_2_3 = models.FloatField(null=True, verbose_name="Similarity of Topics 2 & 3")
    sim_score_3_1 = models.FloatField(null=True, verbose_name="Similarity of Topics 3 & 1")

    def __str__(self):
        return f"Created {timezone.localtime(self.created_at)}"

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Recommender Task Response"

class DATResponse(models.Model):
    submitted_at = models.DateTimeField(auto_now_add=True, blank=False)
    user_session = models.ForeignKey(
        UserSession,
        on_delete=models.CASCADE
    )
    dat_score = models.FloatField(
        verbose_name="DAT Score", 
        blank=True, 
        null=True
    )

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
    user_session = models.ForeignKey(
        UserSession,
        on_delete=models.CASCADE
    )

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
