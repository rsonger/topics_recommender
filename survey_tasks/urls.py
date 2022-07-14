from django.urls import path
from django.views.generic import TemplateView
from survey_tasks.views import DATView

urlpatterns = [
    path("dat/", DATView.as_view(), name="dat"),
    path("grouping/", TemplateView.as_view(template_name="survey_tasks/grouping.html"), name="grouping"),
]