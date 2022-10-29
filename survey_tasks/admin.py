from django.contrib import admin

from parler.admin import TranslatableAdmin

from topics_recommender.models import Topic

from survey_tasks.models import RecommenderResponse
from survey_tasks.models import DATResponse, DATWord
from survey_tasks.models import CTTCategory, CTTResponse, CTTIdea

# Models for recommendation task responses
# class TopicInline(admin.StackedInline):
#     model = Topic

# class RecommenderResponseInline(admin.ModelAdmin):
#     inlines = [TopicInline]

class RecommenderResponseAdmin(admin.ModelAdmin):
    model = RecommenderResponse
    readonly_fields = ("topic1", "topic2", "topic3")

admin.site.register(RecommenderResponse, RecommenderResponseAdmin) #, RecommenderResponseInline)

# Models for creativity task responses
class DATWordInline(admin.StackedInline):
    model = DATWord
    max_num = 10
    min_num = 10

class DATResponseAdmin(admin.ModelAdmin):
    inlines = [DATWordInline]

admin.site.register(DATResponse, DATResponseAdmin)
admin.site.register(DATWord)

# Models for grouping task responses
class CTTCategoryInline(admin.StackedInline):
    model = CTTCategory
    max_num = 5
    min_num = 1

class CTTResponseAdmin(admin.ModelAdmin):
    inlines = [CTTCategoryInline]

admin.site.register(CTTResponse, CTTResponseAdmin)
admin.site.register(CTTIdea, TranslatableAdmin)
admin.site.register(CTTCategory)