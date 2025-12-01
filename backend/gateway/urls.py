from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.ModelListView.as_view(), name='model-list'),
    path('switch/', views.SwitchModelView.as_view(), name='switch-model'),
    path('preferences/', views.ModelPreferencesView.as_view(), name='model-preferences'),
    path('usage/', views.ModelUsageView.as_view(), name='model-usage'),
    path('metrics/', views.SystemMetricsView.as_view(), name='system-metrics'),
]
