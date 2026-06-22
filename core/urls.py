from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("setup/", views.setup_view, name="setup"),
    path("", views.rating_view, name="rating"),
    path("reasons/<str:rating>/", views.get_reasons_view, name="get_reasons"),
    path("submit/", views.submit_response, name="submit"),
    path("cleaner-log/", views.cleaner_log_view, name="cleaner_log"),
]
