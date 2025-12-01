from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.contrib.auth.models import User
from django.db import transaction
import json
import firebase_admin
from firebase_admin import auth
from datetime import datetime, date

from .models import UserProfile, UserSettings, UserUsage

@method_decorator(csrf_exempt, name='dispatch')
class CheckTokenView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            token = data.get('token')
            
            if not token:
                return JsonResponse({'error': 'Token is required'}, status=400)
            
            # Verify Firebase token
            try:
                decoded_token = auth.verify_id_token(token)
                firebase_uid = decoded_token['uid']
                email = decoded_token.get('email')
                display_name = decoded_token.get('display_name', '')
                photo_url = decoded_token.get('photo_url', '')
                
                # Get or create user
                user = self.get_or_create_user(firebase_uid, email, display_name, photo_url)
                
                # Generate Django token or use existing
                # For now, return user info (in production, use JWT)
                return JsonResponse({
                    'valid': True,
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'display_name': user.profile.display_name,
                    'photo_url': user.profile.photo_url
                })
                
            except firebase_admin.exceptions.FirebaseError as e:
                return JsonResponse({'error': f'Invalid token: {str(e)}'}, status=401)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def get_or_create_user(self, firebase_uid, email, display_name, photo_url):
        """Get or create Django user from Firebase data"""
        with transaction.atomic():
            # Check if user profile exists
            try:
                profile = UserProfile.objects.get(firebase_uid=firebase_uid)
                return profile.user
            except UserProfile.DoesNotExist:
                pass
            
            # Create new user
            username = email.split('@')[0] if email else f"user_{firebase_uid[:8]}"
            
            # Ensure unique username
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}_{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=None  # No password for Firebase users
            )
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                firebase_uid=firebase_uid,
                display_name=display_name,
                photo_url=photo_url,
                email_verified=True
            )
            
            # Create user settings
            UserSettings.objects.create(user=user)
            
            return user

@permission_classes([IsAuthenticated])
class UserProfileView(View):
    def get(self, request):
        try:
            profile = request.user.profile
            return JsonResponse({
                'user_id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'display_name': profile.display_name,
                'photo_url': profile.photo_url,
                'phone_number': profile.phone_number,
                'email_verified': profile.email_verified,
                'created_at': profile.created_at.isoformat()
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def put(self, request):
        try:
            data = json.loads(request.body)
            profile = request.user.profile
            
            # Update profile fields
            if 'display_name' in data:
                profile.display_name = data['display_name']
            if 'photo_url' in data:
                profile.photo_url = data['photo_url']
            if 'phone_number' in data:
                profile.phone_number = data['phone_number']
            
            profile.save()
            
            return JsonResponse({'message': 'Profile updated successfully'})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@permission_classes([IsAuthenticated])
class UserSettingsView(View):
    def get(self, request):
        try:
            settings = request.user.settings
            return JsonResponse({
                'theme': settings.theme,
                'default_model': settings.default_model,
                'language': settings.language,
                'timezone': settings.timezone,
                'notifications_enabled': settings.notifications_enabled,
                'auto_save_chats': settings.auto_save_chats,
                'max_chats_per_day': settings.max_chats_per_day,
                'preferred_voice': settings.preferred_voice,
                'voice_speed': settings.voice_speed
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def put(self, request):
        try:
            data = json.loads(request.body)
            settings = request.user.settings
            
            # Update settings fields
            updatable_fields = [
                'theme', 'default_model', 'language', 'timezone',
                'notifications_enabled', 'auto_save_chats', 'max_chats_per_day',
                'preferred_voice', 'voice_speed'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(settings, field, data[field])
            
            settings.save()
            
            return JsonResponse({'message': 'Settings updated successfully'})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@permission_classes([IsAuthenticated])
class UserUsageView(View):
    def get(self, request):
        try:
            # Get usage for last 30 days
            from datetime import timedelta
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            usage_records = UserUsage.objects.filter(
                user=request.user,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('-date')
            
            usage_data = []
            for record in usage_records:
                usage_data.append({
                    'date': record.date.isoformat(),
                    'messages_sent': record.messages_sent,
                    'tokens_used': record.tokens_used,
                    'files_uploaded': record.files_uploaded,
                    'voice_calls': record.voice_calls,
                    'cost_incurred': float(record.cost_incurred)
                })
            
            # Calculate totals
            totals = {
                'total_messages': sum(r['messages_sent'] for r in usage_data),
                'total_tokens': sum(r['tokens_used'] for r in usage_data),
                'total_files': sum(r['files_uploaded'] for r in usage_data),
                'total_voice_calls': sum(r['voice_calls'] for r in usage_data),
                'total_cost': sum(r['cost_incurred'] for r in usage_data)
            }
            
            return JsonResponse({
                'usage': usage_data,
                'totals': totals,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
