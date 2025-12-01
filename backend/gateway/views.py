from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
import json
import requests
from datetime import datetime, timedelta

from .models import AIModel, ModelUsage, ModelPreference, SystemMetrics

@permission_classes([IsAuthenticated])
class ModelListView(View):
    def get(self, request):
        try:
            # Get available models from AI Engine
            models = []
            
            try:
                ai_engine_url = 'http://localhost:4000/models'
                response = requests.get(ai_engine_url, timeout=10)
                response.raise_for_status()
                engine_models = response.json()
                
                for model_data in engine_models:
                    models.append({
                        'id': model_data['id'],
                        'name': model_data['name'],
                        'provider': model_data['provider'],
                        'description': model_data['description'],
                        'context_window': model_data['context_window'],
                        'pricing': model_data['pricing'],
                        'capabilities': model_data['capabilities'],
                        'is_available': model_data['is_available'],
                        'is_local': model_data['is_local']
                    })
                    
            except requests.RequestException:
                # Fallback to database models
                db_models = AIModel.objects.filter(is_available=True)
                for model in db_models:
                    models.append({
                        'id': model.id,
                        'name': model.name,
                        'provider': model.provider,
                        'description': model.description,
                        'context_window': model.context_window,
                        'pricing': {
                            'input': float(model.input_price),
                            'output': float(model.output_price)
                        },
                        'capabilities': model.capabilities,
                        'is_available': model.is_available,
                        'is_local': model.is_local
                    })
            
            return JsonResponse({'models': models})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
@permission_classes([IsAuthenticated])
class SwitchModelView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            model_id = data.get('model_id')
            
            if not model_id:
                return JsonResponse({'error': 'Model ID is required'}, status=400)
            
            # Verify model exists and is available
            try:
                ai_engine_url = f'http://localhost:4000/models'
                response = requests.get(ai_engine_url, timeout=10)
                response.raise_for_status()
                available_models = response.json()
                
                model_exists = any(m['id'] == model_id for m in available_models)
                if not model_exists:
                    return JsonResponse({'error': 'Model not found or unavailable'}, status=404)
                    
            except requests.RequestException:
                # Check database
                if not AIModel.objects.filter(id=model_id, is_available=True).exists():
                    return JsonResponse({'error': 'Model not found or unavailable'}, status=404)
            
            # Update user preference
            preference, created = ModelPreference.objects.get_or_create(
                user=request.user
            )
            
            # Update preferred model
            try:
                if AIModel.objects.filter(id=model_id).exists():
                    preference.preferred_model = AIModel.objects.get(id=model_id)
                else:
                    # Create model in database if it doesn't exist
                    new_model = AIModel.objects.create(
                        id=model_id,
                        name=model_id,
                        provider='openrouter'  # Default provider
                    )
                    preference.preferred_model = new_model
            except:
                pass
            
            preference.save()
            
            return JsonResponse({
                'message': 'Model switched successfully',
                'model_id': model_id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@permission_classes([IsAuthenticated])
class ModelPreferencesView(View):
    def get(self, request):
        try:
            preference, created = ModelPreference.objects.get_or_create(
                user=request.user
            )
            
            response_data = {
                'preferred_model': None,
                'fallback_models': [],
                'max_cost_per_day': float(preference.max_cost_per_day),
                'auto_fallback_enabled': preference.auto_fallback_enabled
            }
            
            if preference.preferred_model:
                response_data['preferred_model'] = {
                    'id': preference.preferred_model.id,
                    'name': preference.preferred_model.name,
                    'provider': preference.preferred_model.provider
                }
            
            for model in preference.fallback_models.all():
                response_data['fallback_models'].append({
                    'id': model.id,
                    'name': model.name,
                    'provider': model.provider
                })
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def put(self, request):
        try:
            data = json.loads(request.body)
            preference, created = ModelPreference.objects.get_or_create(
                user=request.user
            )
            
            # Update preference fields
            if 'preferred_model' in data:
                try:
                    model = AIModel.objects.get(id=data['preferred_model'])
                    preference.preferred_model = model
                except AIModel.DoesNotExist:
                    return JsonResponse({'error': 'Invalid model ID'}, status=400)
            
            if 'fallback_models' in data:
                preference.fallback_models.set(
                    AIModel.objects.filter(id__in=data['fallback_models'])
                )
            
            if 'max_cost_per_day' in data:
                preference.max_cost_per_day = data['max_cost_per_day']
            
            if 'auto_fallback_enabled' in data:
                preference.auto_fallback_enabled = data['auto_fallback_enabled']
            
            preference.save()
            
            return JsonResponse({'message': 'Preferences updated successfully'})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@permission_classes([IsAuthenticated])
class ModelUsageView(View):
    def get(self, request):
        try:
            # Get usage for last 30 days
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
            
            usage_records = ModelUsage.objects.filter(
                user=request.user,
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            ).select_related('model').order_by('-created_at')
            
            usage_data = []
            for record in usage_records:
                usage_data.append({
                    'model': {
                        'id': record.model.id,
                        'name': record.model.name,
                        'provider': record.model.provider
                    },
                    'input_tokens': record.input_tokens,
                    'output_tokens': record.output_tokens,
                    'total_cost': float(record.total_cost),
                    'response_time': record.response_time,
                    'success': record.success,
                    'error_message': record.error_message,
                    'created_at': record.created_at.isoformat()
                })
            
            # Calculate statistics
            total_requests = usage_records.count()
            successful_requests = usage_records.filter(success=True).count()
            total_cost = sum(r.total_cost for r in usage_records)
            avg_response_time = usage_records.aggregate(
                avg_time=Avg('response_time')
            )['avg_time'] or 0
            
            return JsonResponse({
                'usage': usage_data,
                'statistics': {
                    'total_requests': total_requests,
                    'successful_requests': successful_requests,
                    'success_rate': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
                    'total_cost': float(total_cost),
                    'avg_response_time': avg_response_time
                },
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@permission_classes([IsAuthenticated])
class SystemMetricsView(View):
    def get(self, request):
        try:
            # Only admin users can access system metrics
            if not request.user.is_staff:
                return JsonResponse({'error': 'Admin access required'}, status=403)
            
            # Get metrics for last 30 days
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
            
            metrics = SystemMetrics.objects.filter(
                date__gte=start_date,
                date__lte=end_date
            ).order_by('-date')
            
            metrics_data = []
            for metric in metrics:
                metrics_data.append({
                    'date': metric.date.isoformat(),
                    'total_requests': metric.total_requests,
                    'successful_requests': metric.successful_requests,
                    'failed_requests': metric.failed_requests,
                    'total_tokens': metric.total_tokens,
                    'total_cost': float(metric.total_cost),
                    'avg_response_time': metric.avg_response_time,
                    'unique_users': metric.unique_users
                })
            
            # Calculate totals
            totals = {
                'total_requests': sum(m.total_requests for m in metrics),
                'successful_requests': sum(m.successful_requests for m in metrics),
                'failed_requests': sum(m.failed_requests for m in metrics),
                'total_tokens': sum(m.total_tokens for m in metrics),
                'total_cost': sum(m.total_cost for m in metrics),
                'avg_response_time': sum(m.avg_response_time for m in metrics) / len(metrics) if metrics else 0,
                'total_unique_users': sum(m.unique_users for m in metrics)
            }
            
            return JsonResponse({
                'metrics': metrics_data,
                'totals': totals,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
