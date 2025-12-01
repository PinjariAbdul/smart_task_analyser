# Task Priority Manager

## What is this?

This is a task management application that helps you figure out which tasks to work on first. It analyzes your tasks based on due dates, importance, effort required, and dependencies to calculate a priority score (0-100) for each task.

## How does it work?

The priority scoring algorithm considers four main factors:

1. **Urgency**: Tasks that are due soon or past due get higher priority
2. **Importance**: You rate tasks from 1-10 based on importance
3. **Effort**: Tasks that take less time might get a boost (quick wins)
4. **Dependencies**: Tasks that block other tasks are prioritized

### Different ways to prioritize

You can choose from four different approaches:

1. **Quick Wins**: Focus on tasks that take less time
2. **High Impact**: Focus on the most important tasks
3. **Urgent First**: Focus on tasks with nearest deadlines
4. **Balanced**: Considers all factors together

### Dependency checking

The system checks for circular dependencies (like task A depending on task B, which depends on task A) and will alert you if it finds any.

## Design decisions

- **Simple but effective**: I chose a straightforward approach that's easy to understand rather than complex algorithms
- **Fast responses**: The system prioritizes speed so you get results quickly
- **Works everywhere**: Designed to be flexible enough for different types of tasks

## Backend setup

### What you need

- Python 3.8 or higher
- Django 4.2.7
- Django REST Framework 3.14.0

### API endpoints

1. **POST `/api/tasks/analyze/`** - Process tasks and return them sorted by priority
2. **POST `/api/tasks/suggest/`** - Get the top 3 tasks to focus on

### Running the backend

1. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install required packages:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Go to the backend folder:
   ```bash
   cd backend
   ```

4. Set up the database:
   ```bash
   python manage.py migrate
   ```

5. Start the server:
   ```bash
   python manage.py runserver
   ```

## Frontend

The frontend uses plain HTML, CSS, and JavaScript with no frameworks.

### What you can do

- Add tasks one by one or import JSON
- Choose how to prioritize your tasks
- See color-coded results with priority scores
- Works on desktop and mobile

### Using the frontend

1. Open `frontend/index.html` in your browser
2. Add your tasks
3. Pick a prioritization method
4. Click "Prioritize Tasks" to see results

## Testing

The project includes tests for:

1. Checking that tasks are sorted correctly
2. Making sure urgent tasks get priority
3. Testing dependency cycle detection

### Running tests

Go to the backend directory and run:

```bash
python manage.py test
```

## Possible improvements

Ideas for future development:
- Visual dependency graphs
- Better date handling (weekends, holidays)
- Eisenhower Matrix view
- Learning from user feedback

## Final notes

This task manager helps you focus on what matters most. The code is clean, tested, and ready to use or extend.