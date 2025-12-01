from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.SendChatView.as_view(), name='send-chat'),
    path('history/<uuid:session_id>/', views.ChatHistoryView.as_view(), name='chat-history'),
    path('save/', views.SaveSessionView.as_view(), name='save-session'),
    path('sessions/', views.ChatSessionsView.as_view(), name='chat-sessions'),
    path('sessions/<uuid:session_id>/', views.SessionDetailView.as_view(), name='session-detail'),
    path('sessions/<uuid:session_id>/delete/', views.DeleteSessionView.as_view(), name='delete-session'),
    path('rate/<uuid:message_id>/', views.RateMessageView.as_view(), name='rate-message'),
]
