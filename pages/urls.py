from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("analytics/", views.analytics_dashboard, name="analytics"),
    path("download/<str:file_name>/", views.track_download, name="download"),
]

