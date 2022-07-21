from django.urls import path
from survey_tasks.views import DATView, CTTView

urlpatterns = [
    path("dat/", DATView.as_view(), name="dat"),
    path("ctt/", CTTView.as_view(), name="ctt"),
]