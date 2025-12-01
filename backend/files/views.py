from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
import json
import requests
import mimetypes
import PyPDF2
from PIL import Image
import pandas as pd
from io import BytesIO
import time

from .models import FileUpload, FileAnalysis, FileQuery

@method_decorator(csrf_exempt, name='dispatch')
@permission_classes([IsAuthenticated])
class FileUploadView(View):
    def post(self, request):
        try:
            if 'file' not in request.FILES:
                return JsonResponse({'error': 'No file provided'}, status=400)
            
            uploaded_file = request.FILES['file']
            
            # Validate file
            if uploaded_file.size > 50 * 1024 * 1024:  # 50MB limit
                return JsonResponse({'error': 'File too large (max 50MB)'}, status=400)
            
            # Determine file type and mime type
            mime_type, _ = mimetypes.guess_type(uploaded_file.name)
            file_type = self.get_file_type(uploaded_file.name, mime_type)
            
            if file_type not in ['pdf', 'image', 'excel', 'text']:
                return JsonResponse({'error': 'Unsupported file type'}, status=400)
            
            # Create file upload record
            with transaction.atomic():
                file_upload = FileUpload.objects.create(
                    user=request.user,
                    file=uploaded_file,
                    original_name=uploaded_file.name,
                    file_type=file_type,
                    file_size=uploaded_file.size,
                    mime_type=mime_type or 'application/octet-stream'
                )
            
            return JsonResponse({
                'file_id': str(file_upload.id),
                'original_name': file_upload.original_name,
                'file_type': file_upload.file_type,
                'file_size': file_upload.file_size,
                'uploaded_at': file_upload.uploaded_at.isoformat()
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def get_file_type(self, filename, mime_type):
        """Determine file type from name and mime type"""
        ext = filename.lower().split('.')[-1]
        
        if ext in ['pdf'] or mime_type == 'application/pdf':
            return 'pdf'
        elif ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'] or mime_type.startswith('image/'):
            return 'image'
        elif ext in ['xlsx', 'xls', 'csv'] or mime_type in [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
            'text/csv'
        ]:
            return 'excel'
        elif ext in ['txt', 'md', 'py', 'js', 'html', 'css'] or mime_type.startswith('text/'):
            return 'text'
        
        return 'unknown'

@permission_classes([IsAuthenticated])
class FileListView(View):
    def get(self, request):
        try:
            files = FileUpload.objects.filter(user=request.user).order_by('-uploaded_at')
            
            files_data = []
            for file_obj in files:
                file_data = {
                    'id': str(file_obj.id),
                    'original_name': file_obj.original_name,
                    'file_type': file_obj.file_type,
                    'file_size': file_obj.file_size,
                    'size_display': file_obj.size_display,
                    'mime_type': file_obj.mime_type,
                    'uploaded_at': file_obj.uploaded_at.isoformat()
                }
                
                # Include analysis if available
                if hasattr(file_obj, 'analysis'):
                    file_data['analysis'] = {
                        'summary': file_obj.analysis.summary[:200] + '...' if len(file_obj.analysis.summary) > 200 else file_obj.analysis.summary,
                        'insights_count': len(file_obj.analysis.insights),
                        'analysis_model': file_obj.analysis.analysis_model,
                        'created_at': file_obj.analysis.created_at.isoformat()
                    }
                
                files_data.append(file_data)
            
            return JsonResponse({'files': files_data})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@permission_classes([IsAuthenticated])
class FileDetailView(View):
    def get(self, request, file_id):
        try:
            file_obj = get_object_or_404(FileUpload, id=file_id, user=request.user)
            
            file_data = {
                'id': str(file_obj.id),
                'original_name': file_obj.original_name,
                'file_type': file_obj.file_type,
                'file_size': file_obj.file_size,
                'size_display': file_obj.size_display,
                'mime_type': file_obj.mime_type,
                'uploaded_at': file_obj.uploaded_at.isoformat()
            }
            
            # Include analysis if available
            if hasattr(file_obj, 'analysis'):
                file_data['analysis'] = {
                    'summary': file_obj.analysis.summary,
                    'insights': file_obj.analysis.insights,
                    'metadata': file_obj.analysis.metadata,
                    'analysis_model': file_obj.analysis.analysis_model,
                    'analysis_time': file_obj.analysis.analysis_time,
                    'token_count': file_obj.analysis.token_count,
                    'cost': float(file_obj.analysis.cost),
                    'created_at': file_obj.analysis.created_at.isoformat()
                }
            
            return JsonResponse(file_data)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@permission_classes([IsAuthenticated])
class FileDeleteView(View):
    def delete(self, request, file_id):
        try:
            file_obj = get_object_or_404(FileUpload, id=file_id, user=request.user)
            
            # Delete file from storage and database
            file_obj.file.delete()
            file_obj.delete()
            
            return JsonResponse({'message': 'File deleted successfully'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
@permission_classes([IsAuthenticated])
class FileAnalyzeView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            file_id = data.get('file_id')
            query = data.get('query', 'Analyze this file and provide a comprehensive summary')
            model = data.get('model', 'gpt-4-vision-preview')
            
            if not file_id:
                return JsonResponse({'error': 'File ID is required'}, status=400)
            
            file_obj = get_object_or_404(FileUpload, id=file_id, user=request.user)
            
            # Extract content from file
            start_time = time.time()
            content = self.extract_file_content(file_obj)
            
            if not content:
                return JsonResponse({'error': 'Could not extract content from file'}, status=400)
            
            # Get AI analysis
            try:
                analysis_result = self.get_ai_analysis(content, query, model)
                analysis_time = time.time() - start_time
                
                # Save analysis
                analysis = FileAnalysis.objects.create(
                    file_upload=file_obj,
                    summary=analysis_result['summary'],
                    insights=analysis_result['insights'],
                    metadata=analysis_result.get('metadata', {}),
                    analysis_model=model,
                    analysis_time=analysis_time,
                    token_count=analysis_result.get('token_count'),
                    cost=analysis_result.get('cost', 0)
                )
                
                return JsonResponse({
                    'analysis_id': str(analysis.id),
                    'summary': analysis.summary,
                    'insights': analysis.insights,
                    'metadata': analysis.metadata,
                    'analysis_model': analysis.analysis_model,
                    'analysis_time': analysis.analysis_time,
                    'token_count': analysis.token_count,
                    'cost': float(analysis.cost),
                    'created_at': analysis.created_at.isoformat()
                })
                
            except Exception as e:
                return JsonResponse({'error': f'AI analysis failed: {str(e)}'}, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def extract_file_content(self, file_obj):
        """Extract text content from uploaded file"""
        try:
            file_obj.file.seek(0)
            
            if file_obj.file_type == 'pdf':
                return self.extract_pdf_content(file_obj.file)
            elif file_obj.file_type == 'image':
                return f"Image file: {file_obj.original_name}"
            elif file_obj.file_type == 'excel':
                return self.extract_excel_content(file_obj.file)
            elif file_obj.file_type == 'text':
                return file_obj.file.read().decode('utf-8', errors='ignore')
            
            return None
            
        except Exception as e:
            print(f"Error extracting content: {e}")
            return None
    
    def extract_pdf_content(self, pdf_file):
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            content = ""
            
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
            
            return content[:10000]  # Limit to 10k characters
            
        except Exception as e:
            print(f"Error extracting PDF content: {e}")
            return None
    
    def extract_excel_content(self, excel_file):
        """Extract data from Excel file"""
        try:
            if excel_file.name.endswith('.csv'):
                df = pd.read_csv(excel_file)
            else:
                df = pd.read_excel(excel_file)
            
            # Convert to string representation
            content = f"Excel file: {excel_file.name}\n"
            content += f"Shape: {df.shape}\n"
            content += f"Columns: {list(df.columns)}\n\n"
            content += df.head(100).to_string()  # First 100 rows
            
            return content[:10000]  # Limit to 10k characters
            
        except Exception as e:
            print(f"Error extracting Excel content: {e}")
            return None
    
    def get_ai_analysis(self, content, query, model):
        """Get AI analysis of file content"""
        try:
            ai_engine_url = 'http://localhost:4000/chat'
            payload = {
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a helpful AI assistant that analyzes uploaded files. Provide comprehensive summaries and insights.'
                    },
                    {
                        'role': 'user',
                        'content': f"File Content:\n\n{content}\n\nQuery: {query}"
                    }
                ],
                'model': model,
                'max_tokens': 2000,
                'temperature': 0.3
            }
            
            response = requests.post(ai_engine_url, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            ai_response = data['choices'][0]['message']['content']
            
            # Parse response (in production, use structured output)
            summary = ai_response
            insights = [ai_response]  # Simplified for now
            
            return {
                'summary': summary,
                'insights': insights,
                'metadata': {'content_length': len(content)},
                'token_count': data.get('usage', {}).get('total_tokens', 0),
                'cost': 0.01  # Placeholder
            }
            
        except Exception as e:
            raise Exception(f"AI analysis error: {str(e)}")
