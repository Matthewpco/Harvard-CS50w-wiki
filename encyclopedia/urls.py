from django.urls import path
from . import views
urlpatterns = [
    path("", views.index, name="index"),
    path("<str:page_url>", views.entry, name="entry"),
    path("search/", views.search, name="search"),
    path("new/", views.add_new_entry, name="new"),
    path("edit/<str:page_url>", views.edit_entry, name="edit"),
    path("random/", views.random_page, name="random"),
]
