# programs/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_program, name="create_program"),
    path("register/<uuid:public_id>/", views.public_register, name="public_register"),
]
