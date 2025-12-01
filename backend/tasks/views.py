from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .serializers import TaskSerializer
from .scoring import sort_tasks_by_priority, detect_circular_dependencies

class AnalyzeTasksView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            # Parse JSON data
            data = json.loads(request.body)
            tasks_data = data.get('tasks', [])
            
            # Validate tasks
            validated_tasks = []
            errors = []
            
            for i, task_data in enumerate(tasks_data):
                serializer = TaskSerializer(data=task_data)
                if serializer.is_valid():
                    validated_tasks.append(serializer.validated_data)
                else:
                    errors.append(f"Task {i}: {serializer.errors}")
            
            if errors:
                return JsonResponse({'error': 'Validation failed', 'details': errors}, status=400)
            
            # Check for circular dependencies
            cycle_result = detect_circular_dependencies(validated_tasks)
            if cycle_result['has_cycle']:
                return JsonResponse({
                    'error': 'Circular dependencies detected',
                    'cycle_details': cycle_result['cycle_details']
                }, status=400)
            
            # Get strategy and weights from request
            strategy = data.get('strategy', 'smart_balance')
            weights = data.get('weights', {})
            
            # Sort tasks by priority
            sorted_tasks = sort_tasks_by_priority(validated_tasks, strategy, weights)
            
            return JsonResponse({'tasks': sorted_tasks})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class SuggestTasksView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            # Parse JSON data
            data = json.loads(request.body)
            tasks_data = data.get('tasks', [])
            
            # Validate tasks
            validated_tasks = []
            errors = []
            
            for i, task_data in enumerate(tasks_data):
                serializer = TaskSerializer(data=task_data)
                if serializer.is_valid():
                    validated_tasks.append(serializer.validated_data)
                else:
                    errors.append(f"Task {i}: {serializer.errors}")
            
            if errors:
                return JsonResponse({'error': 'Validation failed', 'details': errors}, status=400)
            
            # Check for circular dependencies
            cycle_result = detect_circular_dependencies(validated_tasks)
            if cycle_result['has_cycle']:
                return JsonResponse({
                    'error': 'Circular dependencies detected',
                    'cycle_details': cycle_result['cycle_details']
                }, status=400)
            
            # Sort tasks by priority using smart balance strategy
            sorted_tasks = sort_tasks_by_priority(validated_tasks, 'smart_balance')
            
            # Return top 3 tasks
            top_tasks = sorted_tasks[:3]
            
            return JsonResponse({'tasks': top_tasks})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

# Function-based views for URL routing
analyze_tasks = AnalyzeTasksView.as_view()
suggest_tasks = SuggestTasksView.as_view()
