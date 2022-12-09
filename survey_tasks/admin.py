from django.contrib import admin

from parler.admin import TranslatableAdmin

from survey_tasks.models import RecommenderResponse, RecommenderResponseV2
from survey_tasks.models import DATResponse, DATWord
from survey_tasks.models import CTTCategory, CTTResponse, CTTIdea

class RecommenderResponseAdmin(admin.ModelAdmin):
    model = RecommenderResponse
    readonly_fields = ("topic1", "topic2", "topic3")

admin.site.register(RecommenderResponse, RecommenderResponseAdmin)

class RecommenderResponseAdminV2(admin.ModelAdmin):
    model = RecommenderResponseV2
    readonly_fields = ("topic1", "topic2", "topic3", "topic4", "topic5")

admin.site.register(RecommenderResponseV2, RecommenderResponseAdminV2)

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