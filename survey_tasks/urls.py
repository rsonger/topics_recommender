from django.urls import path
from django.apps import apps
from survey_tasks.views import RecommenderView, DATView, CTTView

v2_model = apps.get_model("survey_tasks", "RecommenderResponseV2")

urlpatterns = [
    path("submit/", RecommenderView.as_view(), name="submit"),
    path("submitv2/", RecommenderView.as_view(
        num_topics=5, 
        response_model=v2_model), 
        name="submitv2"
    ),
    path("dat/", DATView.as_view(), name="dat"),
    path("ctt/", CTTView.as_view(), name="ctt"),
]