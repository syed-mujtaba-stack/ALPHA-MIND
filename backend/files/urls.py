from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.FileUploadView.as_view(), name='file-upload'),
    path('analyze/', views.FileAnalyzeView.as_view(), name='file-analyze'),
    path('list/', views.FileListView.as_view(), name='file-list'),
    path('<uuid:file_id>/', views.FileDetailView.as_view(), name='file-detail'),
    path('<uuid:file_id>/delete/', views.FileDeleteView.as_view(), name='file-delete'),
]
