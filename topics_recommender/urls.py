from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path("", views.TopicsListView.as_view(), name="index"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("start/", TemplateView.as_view(template_name="topics_recommender/start.html"), name="start"),
]