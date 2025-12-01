from django.test import TestCase
from django.test import Client
from django.urls import reverse
import json
from .scoring import sort_tasks_by_priority, detect_circular_dependencies

class TaskAnalyzerTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.sample_tasks = [
            {
                'id': 'task1',
                'title': 'Urgent task',
                'due_date': '2025-11-30',
                'estimated_hours': 2,
                'importance': 9,
                'dependencies': []
            },
            {
                'id': 'task2',
                'title': 'Less urgent task',
                'due_date': '2025-12-15',
                'estimated_hours': 5,
                'importance': 5,
                'dependencies': []
            },
            {
                'id': 'task3',
                'title': 'Quick win task',
                'due_date': '2025-12-05',
                'estimated_hours': 1,
                'importance': 7,
                'dependencies': []
            }
        ]
    
    def test_task_sorting_correctness(self):
        """Test that tasks are sorted correctly by priority score"""
        sorted_tasks = sort_tasks_by_priority(self.sample_tasks, 'smart_balance')
        
        # Check that we get the right number of tasks
        self.assertEqual(len(sorted_tasks), 3)
        
        # Check that tasks are sorted in descending order by priority score
        for i in range(len(sorted_tasks) - 1):
            self.assertGreaterEqual(sorted_tasks[i]['priority_score'], sorted_tasks[i + 1]['priority_score'])
    
    def test_deadline_urgency_boost(self):
        """Test that past-due tasks receive an urgency boost"""
        import datetime
        from datetime import timedelta
        
        # Create a past-due task
        past_due_task = {
            'id': 'past_due_task',
            'title': 'Past due task',
            'due_date': (datetime.date.today() - timedelta(days=2)).isoformat(),
            'estimated_hours': 3,
            'importance': 5,
            'dependencies': []
        }
        
        # Create a future due task
        future_due_task = {
            'id': 'future_due_task',
            'title': 'Future task',
            'due_date': (datetime.date.today() + timedelta(days=10)).isoformat(),
            'estimated_hours': 3,
            'importance': 5,
            'dependencies': []
        }
        
        tasks = [past_due_task, future_due_task]
        sorted_tasks = sort_tasks_by_priority(tasks, 'deadline')
        
        # Past due task should have higher priority when using deadline strategy
        self.assertGreater(sorted_tasks[0]['priority_score'], sorted_tasks[1]['priority_score'])
        self.assertIn('past due', sorted_tasks[0]['explanation'].lower())
    
    def test_circular_dependency_detection(self):
        """Test that circular dependencies are detected correctly"""
        # Create tasks with circular dependency
        tasks_with_cycle = [
            {
                'id': 'taskA',
                'title': 'Task A',
                'due_date': '2025-12-01',
                'estimated_hours': 2,
                'importance': 5,
                'dependencies': ['taskB']
            },
            {
                'id': 'taskB',
                'title': 'Task B',
                'due_date': '2025-12-02',
                'estimated_hours': 3,
                'importance': 5,
                'dependencies': ['taskC']
            },
            {
                'id': 'taskC',
                'title': 'Task C',
                'due_date': '2025-12-03',
                'estimated_hours': 1,
                'importance': 5,
                'dependencies': ['taskA']  # Creates cycle: A -> B -> C -> A
            }
        ]
        
        # Test cycle detection
        result = detect_circular_dependencies(tasks_with_cycle)
        self.assertTrue(result['has_cycle'])
        self.assertIn('taskA', result['cycle_details'])
        self.assertIn('taskB', result['cycle_details'])
        self.assertIn('taskC', result['cycle_details'])
        
        # Test with no cycle
        tasks_without_cycle = [
            {
                'id': 'taskX',
                'title': 'Task X',
                'due_date': '2025-12-01',
                'estimated_hours': 2,
                'importance': 5,
                'dependencies': []
            },
            {
                'id': 'taskY',
                'title': 'Task Y',
                'due_date': '2025-12-02',
                'estimated_hours': 3,
                'importance': 5,
                'dependencies': ['taskX']  # Y depends on X - no cycle
            }
        ]
        
        result = detect_circular_dependencies(tasks_without_cycle)
        self.assertFalse(result['has_cycle'])
        self.assertEqual(len(result['cycle_details']), 0)
    
    def test_analyze_api_endpoint(self):
        """Test the analyze API endpoint"""
        data = {
            'tasks': self.sample_tasks,
            'strategy': 'smart_balance'
        }
        
        response = self.client.post(
            '/api/tasks/analyze/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('tasks', response_data)
        self.assertEqual(len(response_data['tasks']), 3)
        
        # Check that tasks are sorted by priority
        tasks = response_data['tasks']
        for i in range(len(tasks) - 1):
            self.assertGreaterEqual(tasks[i]['priority_score'], tasks[i + 1]['priority_score'])
    
    def test_suggest_api_endpoint(self):
        """Test the suggest API endpoint"""
        data = {
            'tasks': self.sample_tasks
        }
        
        response = self.client.post(
            '/api/tasks/suggest/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('tasks', response_data)
        # Should return at most 3 tasks
        self.assertLessEqual(len(response_data['tasks']), 3)
