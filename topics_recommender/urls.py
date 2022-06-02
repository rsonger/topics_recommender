from django.urls import path
from . import views

urlpatterns = [
    path("", views.TopicsListView.as_view(), name="index"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]