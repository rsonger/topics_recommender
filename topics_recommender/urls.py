from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path("", TemplateView.as_view(template_name="topics_recommender/start.html"), name="index"),
    path("start/", TemplateView.as_view(template_name="topics_recommender/start.html"), name="start"),
    path("startv2/", TemplateView.as_view(template_name="topics_recommender/startv2.html"), name="startv2"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("end/", TemplateView.as_view(template_name="topics_recommender/logout.html"), name="end"),
    path("searchv2/", views.SearchView.as_view(num_topics=5), name="searchv2"),
]