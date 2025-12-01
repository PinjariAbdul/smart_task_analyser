import datetime
from collections import defaultdict, deque
from datetime import datetime as dt

def calculate_priority_score(task, tasks_dict, strategy='smart_balance', weights=None):
    """
    Calculate priority score for a task based on multiple factors.
    
    Args:
        task (dict): The task to score
        tasks_dict (dict): Dictionary of all tasks by ID
        strategy (str): Strategy to use for scoring
        weights (dict): Custom weights for scoring factors
    
    Returns:
        tuple: (score, explanation)
    """
    if weights is None:
        weights = {}
    
    # Default weights
    default_weights = {
        'urgency': 0.3,
        'importance': 0.3,
        'effort': 0.2,
        'dependencies': 0.2
    }
    
    # Override with custom weights if provided
    for key in default_weights:
        if key in weights:
            default_weights[key] = weights[key]
    
    # Extract task attributes
    due_date_str = task.get('due_date')
    due_date = None
    if due_date_str:
        if isinstance(due_date_str, str):
            # Parse string date (YYYY-MM-DD format)
            due_date = dt.strptime(due_date_str, '%Y-%m-%d').date()
        else:
            # Already a date object
            due_date = due_date_str
    
    importance = task.get('importance', 1)
    estimated_hours = task.get('estimated_hours', 1)
    dependencies = task.get('dependencies', [])
    
    # Calculate urgency score (0-100)
    urgency_score = 50  # Base score
    urgency_explanation = "Neutral urgency"
    
    if due_date:
        today = datetime.date.today()
        days_until_due = (due_date - today).days
        
        if days_until_due < 0:
            # Past due - higher urgency
            urgency_score = min(100, 80 + abs(days_until_due))
            urgency_explanation = f"Task is {abs(days_until_due)} days past due"
        elif days_until_due == 0:
            # Due today
            urgency_score = 70
            urgency_explanation = "Task is due today"
        elif days_until_due <= 3:
            # Due in 1-3 days
            urgency_score = 60 + (3 - days_until_due) * 5
            urgency_explanation = f"Task is due in {days_until_due} days"
        elif days_until_due <= 7:
            # Due in 4-7 days
            urgency_score = 40 + (7 - days_until_due) * 3
            urgency_explanation = f"Task is due in {days_until_due} days"
        else:
            # Due in more than 7 days
            urgency_score = max(10, 30 - (days_until_due // 7))
            urgency_explanation = f"Task is due in {days_until_due} days"
    
    # Calculate effort score (0-100) - lower effort = higher score
    effort_score = max(10, 100 - (estimated_hours * 10))
    effort_score = min(100, effort_score)
    effort_explanation = f"Task requires {estimated_hours} hours of effort"
    
    # Calculate dependency score (0-100) - more dependencies = higher score
    dependency_count = 0
    for t in tasks_dict.values():
        if task.get('id') in t.get('dependencies', []):
            dependency_count += 1
    
    dependency_score = min(100, dependency_count * 20)
    dependency_explanation = f"Task blocks {dependency_count} other tasks"
    
    # Apply different strategies
    explanations = []
    
    if strategy == 'fastest':
        # Prioritize low-effort tasks
        score = effort_score
        explanations.append("Prioritized based on effort (Fastest Wins strategy)")
        explanations.append(effort_explanation)
    elif strategy == 'impact':
        # Prioritize importance
        score = importance * 10
        explanations.append("Prioritized based on importance (High Impact strategy)")
        explanations.append(f"Task importance level: {importance}/10")
    elif strategy == 'deadline':
        # Prioritize based on due date
        score = urgency_score
        explanations.append("Prioritized based on deadline (Deadline Driven strategy)")
        explanations.append(urgency_explanation)
    else:  # smart_balance
        # Balanced approach
        score = (
            urgency_score * default_weights['urgency'] +
            importance * 10 * default_weights['importance'] +
            effort_score * default_weights['effort'] +
            dependency_score * default_weights['dependencies']
        )
        explanations.append("Balanced priority calculation (Smart Balance strategy)")
        explanations.append(urgency_explanation)
        explanations.append(effort_explanation)
        explanations.append(dependency_explanation)
    
    # Ensure score is within bounds
    score = max(0, min(100, score))
    
    return score, "; ".join(explanations)


def detect_circular_dependencies(tasks):
    """
    Detect circular dependencies in tasks using DFS.
    
    Args:
        tasks (list): List of task dictionaries
    
    Returns:
        dict: {'has_cycle': bool, 'cycle_details': list}
    """
    # Create adjacency list
    graph = defaultdict(list)
    task_ids = set()
    
    for task in tasks:
        task_id = task.get('id')
        if task_id:
            task_ids.add(task_id)
            dependencies = task.get('dependencies', [])
            for dep in dependencies:
                if dep in task_ids or any(t.get('id') == dep for t in tasks):
                    graph[task_id].append(dep)
    
    # DFS to detect cycles
    visited = set()
    rec_stack = set()
    cycle_nodes = []
    
    def dfs(node, path):
        if node in rec_stack:
            # Found a cycle
            cycle_start = path.index(node)
            return path[cycle_start:] + [node]
        
        if node in visited:
            return None
            
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in graph[node]:
            cycle = dfs(neighbor, path[:])
            if cycle:
                return cycle
                
        rec_stack.remove(node)
        return None
    
    # Check each node
    for task_id in task_ids:
        if task_id not in visited:
            cycle = dfs(task_id, [])
            if cycle:
                cycle_nodes = cycle
                break
    
    return {
        'has_cycle': len(cycle_nodes) > 0,
        'cycle_details': cycle_nodes if cycle_nodes else []
    }


def sort_tasks_by_priority(tasks, strategy='smart_balance', weights=None):
    """
    Sort tasks by priority score.
    
    Args:
        tasks (list): List of task dictionaries
        strategy (str): Strategy to use for scoring
        weights (dict): Custom weights for scoring factors
    
    Returns:
        list: Sorted tasks with scores and explanations
    """
    # Create a dictionary for quick lookup
    tasks_dict = {task.get('id'): task for task in tasks if task.get('id')}
    
    # Score each task
    scored_tasks = []
    for task in tasks:
        score, explanation = calculate_priority_score(task, tasks_dict, strategy, weights)
        task_with_score = task.copy()
        task_with_score['priority_score'] = round(score, 2)
        task_with_score['explanation'] = explanation
        scored_tasks.append(task_with_score)
    
    # Sort by priority score (descending)
    scored_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
    
    return scored_tasks