from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),  # admin dashboard
    path("user/dashboard/", views.user_dashboard, name="user_dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("analytics/", views.analytics_dashboard, name="analytics"),
    path("download/<str:file_name>/", views.track_download, name="download"),
    path("account/", views.account_profile, name="account_profile"),
    path("planting/", views.planting_view, name="planting"),
    path("cultural/", views.cultural_view, name="cultural"),
    path("historical/", views.historical_view, name="historical"),
    path("economic/", views.economic_view, name="economic"),
]

