# programs/urls.py
from django.urls import path
from . import views

app_name = "programs"

urlpatterns = [
    path("", views.programs, name="programs"),
    path("create/", views.create_program, name="create_program"),
    path("register/<uuid:public_id>/", views.public_register, name="public_register"),
    path(
        "programs/<int:program_id>/toggle-registration/",
        views.toggle_registration,
        name="toggle_registration"
    ),
]
