from django.urls import path
from survey_tasks.views import RecommenderView, DATView, CTTView

urlpatterns = [
    path("submit/", RecommenderView.as_view(), name="submit"),
    path("dat/", DATView.as_view(), name="dat"),
    path("ctt/", CTTView.as_view(), name="ctt"),
]