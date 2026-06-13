from django.urls import path
from . import public_views
from .content import views as content_views

urlpatterns = [
    path("", public_views.HomeView.as_view(), name="home"),
    path("rooms/", public_views.RoomListView.as_view(), name="rooms"),
    path("rooms/<slug:slug>/", public_views.RoomDetailView.as_view(), name="room_detail"),
    path("about/", content_views.AboutView.as_view(), name="about"),
    path("gallery/", public_views.GalleryView.as_view(), name="gallery"),
    path("booking/", public_views.BookingSelectView.as_view(), name="booking"),
    path("book/search/", public_views.BookingSearchView.as_view(), name="booking_search"),
    path("newsletter/subscribe/", public_views.NewsletterSubscribeView.as_view(), name="newsletter_subscribe"),
]
