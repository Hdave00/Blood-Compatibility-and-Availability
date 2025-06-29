from django.urls import path

from . import views

urlpatterns = [
    path("inheritance/", views.inheritance_page, name="inheritance_page"),
]
