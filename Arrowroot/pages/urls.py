from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),

    # 👇 Add these new pages
    path('account/', views.account_profile_view, name='account_profile'),
    path('planting/', views.planting_view, name='planting'),
    path('cultural/', views.cultural_view, name='cultural'),
    path('historical/', views.historical_view, name='historical'),
    path('economic/', views.economic_view, name='economic'),
]
