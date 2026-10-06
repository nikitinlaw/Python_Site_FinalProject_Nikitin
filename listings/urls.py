from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("listing/<int:pk>/", views.listing_detail, name="listing_detail"),
    path("create/", views.create_listing, name="create_listing"),
    path("listing/<int:pk>/review/", views.add_review, name="add_review"),
    path("my/", views.my_listings, name="my_listings"),
    path("edit/<int:pk>/", views.edit_listing, name="edit_listing"),
    path("delete/<int:pk>/", views.delete_listing, name="delete_listing"),
]
