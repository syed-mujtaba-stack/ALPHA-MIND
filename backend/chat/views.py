from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
import json
import requests
import uuid
from datetime import datetime

from .models import ChatSession, ChatMessage, MessageRating

@method_decorator(csrf_exempt, name='dispatch')
@permission_classes([IsAuthenticated])
class SendChatView(View):
    async def post(self, request):
        try:
            data = json.loads(request.body)
            message = data.get('message')
            model = data.get('model', 'gpt-3.5-turbo')
            session_id = data.get('session_id')
            
            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            
            # Get or create session
            if session_id:
                session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            else:
                # Create new session with message as title
                title = message[:50] + ('...' if len(message) > 50 else '')
                session = ChatSession.objects.create(
                    user=request.user,
                    title=title,
                    model=model
                )
            
            # Save user message
            user_message = ChatMessage.objects.create(
                session=session,
                role='user',
                content=message
            )
            
            # Get AI response from AI Engine
            try:
                ai_response = await self.get_ai_response(message, model, session)
                
                # Save AI response
                ai_message = ChatMessage.objects.create(
                    session=session,
                    role='assistant',
                    content=ai_response['content'],
                    model=model,
                    token_count=ai_response.get('token_count')
                )
                
                return JsonResponse({
                    'session_id': str(session.id),
                    'user_message_id': str(user_message.id),
                    'ai_message_id': str(ai_message.id),
                    'ai_response': ai_response['content']
                })
                
            except Exception as e:
                return JsonResponse({'error': f'AI service error: {str(e)}'}, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    async def get_ai_response(self, message, model, session):
        """Get response from AI Engine"""
        try:
            # Get message history
            messages = [{'role': msg.role, 'content': msg.content} 
                       for msg in session.messages.all()]
            
            # Call AI Engine
            ai_engine_url = 'http://localhost:4000/chat'
            payload = {
                'messages': messages + [{'role': 'user', 'content': message}],
                'model': model,
                'max_tokens': 1000,
                'temperature': 0.7
            }
            
            response = requests.post(ai_engine_url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            token_count = data.get('usage', {}).get('total_tokens', 0)
            
            return {
                'content': content,
                'token_count': token_count
            }
            
        except requests.RequestException as e:
            raise Exception(f"Failed to connect to AI Engine: {str(e)}")
        except Exception as e:
            raise Exception(f"AI processing error: {str(e)}")

@permission_classes([IsAuthenticated])
class ChatHistoryView(View):
    def get(self, request, session_id):
        try:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            messages = []
            
            for msg in session.messages.all():
                messages.append({
                    'id': str(msg.id),
                    'role': msg.role,
                    'content': msg.content,
                    'token_count': msg.token_count,
                    'model': msg.model,
                    'created_at': msg.created_at.isoformat()
                })
            
            return JsonResponse({
                'session_id': str(session.id),
                'title': session.title,
                'model': session.model,
                'created_at': session.created_at.isoformat(),
                'messages': messages
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
@permission_classes([IsAuthenticated])
class SaveSessionView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            title = data.get('title')
            messages = data.get('messages', [])
            
            if not title:
                return JsonResponse({'error': 'Title is required'}, status=400)
            
            # Create new session
            session = ChatSession.objects.create(
                user=request.user,
                title=title,
                model='gpt-3.5-turbo'
            )
            
            # Save messages
            for msg_data in messages:
                ChatMessage.objects.create(
                    session=session,
                    role=msg_data['role'],
                    content=msg_data['content'],
                    model=msg_data.get('model', ''),
                    token_count=msg_data.get('token_count')
                )
            
            return JsonResponse({
                'session_id': str(session.id),
                'message': 'Session saved successfully'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@permission_classes([IsAuthenticated])
class ChatSessionsView(View):
    def get(self, request):
        try:
            sessions = []
            
            for session in request.user.chat_sessions.all():
                sessions.append({
                    'id': str(session.id),
                    'title': session.title,
                    'model': session.model,
                    'created_at': session.created_at.isoformat(),
                    'updated_at': session.updated_at.isoformat(),
                    'message_count': session.messages.count()
                })
            
            return JsonResponse({'sessions': sessions})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@permission_classes([IsAuthenticated])
class SessionDetailView(View):
    def get(self, request, session_id):
        try:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            
            return JsonResponse({
                'id': str(session.id),
                'title': session.title,
                'model': session.model,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat()
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@permission_classes([IsAuthenticated])
class DeleteSessionView(View):
    def delete(self, request, session_id):
        try:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            session.delete()
            
            return JsonResponse({'message': 'Session deleted successfully'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
@permission_classes([IsAuthenticated])
class RateMessageView(View):
    def post(self, request, message_id):
        try:
            data = json.loads(request.body)
            rating = data.get('rating')
            feedback = data.get('feedback', '')
            
            if rating not in [1, 2]:
                return JsonResponse({'error': 'Invalid rating'}, status=400)
            
            message = get_object_or_404(ChatMessage, id=message_id, session__user=request.user)
            
            # Update or create rating
            MessageRating.objects.update_or_create(
                message=message,
                defaults={
                    'rating': rating,
                    'feedback': feedback
                }
            )
            
            return JsonResponse({'message': 'Message rated successfully'})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
