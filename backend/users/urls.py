from django.urls import path
from . import views

urlpatterns = [
    path('check/', views.CheckTokenView.as_view(), name='check-token'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('settings/', views.UserSettingsView.as_view(), name='user-settings'),
    path('usage/', views.UserUsageView.as_view(), name='user-usage'),
]
