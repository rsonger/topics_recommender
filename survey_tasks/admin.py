from django.contrib import admin

from survey_tasks.models import DATResponse, DATWord

class DATWordInline(admin.StackedInline):
    model = DATWord
    max_num = 10
    min_num = 10

class DATResponseAdmin(admin.ModelAdmin):
    inlines = [DATWordInline]

admin.site.register(DATResponse, DATResponseAdmin)
admin.site.register(DATWord)