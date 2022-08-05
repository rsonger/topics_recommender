from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path("", TemplateView.as_view(template_name="topics_recommender/start.html"), name="index"),
    path("start/", TemplateView.as_view(template_name="topics_recommender/start.html"), name="start"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("end/", TemplateView.as_view(template_name="topics_recommender/logout.html"), name="end")
]