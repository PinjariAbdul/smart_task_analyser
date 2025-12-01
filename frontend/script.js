// Global tasks array
let tasks = [];

// DOM Elements
const taskForm = document.getElementById('task-form');
const jsonInput = document.getElementById('json-input');
const addJsonTasksBtn = document.getElementById('add-json-tasks');
const analyzeBtn = document.getElementById('analyze-btn');
const resultsContainer = document.getElementById('results-container');
const noResultsMessage = document.getElementById('no-results-message');
const resultsList = document.getElementById('results-list');
const strategySelect = document.getElementById('strategy');

// Event Listeners
taskForm.addEventListener('submit', handleAddTask);
addJsonTasksBtn.addEventListener('click', handleAddJsonTasks);
analyzeBtn.addEventListener('click', handleAnalyzeTasks);

// Add individual task
function handleAddTask(e) {
    e.preventDefault();
    
    const title = document.getElementById('title').value;
    const dueDate = document.getElementById('due-date').value;
    const estimatedHours = parseFloat(document.getElementById('estimated-hours').value);
    const importance = parseInt(document.getElementById('importance').value);
    const dependencies = document.getElementById('dependencies').value
        .split(',')
        .map(dep => dep.trim())
        .filter(dep => dep.length > 0);
    
    // Generate a simple ID
    const id = `task${Date.now()}`;
    
    const task = {
        id,
        title,
        due_date: dueDate,
        estimated_hours: estimatedHours,
        importance,
        dependencies
    };
    
    tasks.push(task);
    
    // Reset form
    taskForm.reset();
    
    // Show confirmation
    alert(`Added: ${title}`);
}

// Add tasks from JSON
function handleAddJsonTasks() {
    try {
        const jsonText = jsonInput.value.trim();
        if (!jsonText) {
            alert('Please enter JSON data');
            return;
        }
        
        const jsonTasks = JSON.parse(jsonText);
        
        if (!Array.isArray(jsonTasks)) {
            alert('JSON must be an array of tasks');
            return;
        }
        
        // Convert field names if needed (due_date to due_date)
        const convertedTasks = jsonTasks.map(task => {
            // If the task already has an ID, use it; otherwise generate one
            if (!task.id) {
                task.id = `task${Date.now()}_${Math.floor(Math.random() * 1000)}`;
            }
            
            // Ensure field names match expected format
            return {
                id: task.id,
                title: task.title,
                due_date: task.due_date || task.dueDate,
                estimated_hours: task.estimated_hours || task.estimatedHours,
                importance: task.importance,
                dependencies: task.dependencies || []
            };
        });
        
        tasks = tasks.concat(convertedTasks);
        
        // Clear input
        jsonInput.value = '';
        
        alert(`Imported ${convertedTasks.length} tasks`);
    } catch (error) {
        alert(`Error parsing JSON: ${error.message}`);
    }
}

// Analyze tasks
function handleAnalyzeTasks() {
    if (tasks.length === 0) {
        alert('Please add tasks first');
        return;
    }
    
    // Show loading state
    noResultsMessage.style.display = 'none';
    resultsList.innerHTML = '<div class="loading">Prioritizing tasks...</div>';
    
    // Get selected strategy
    const strategy = strategySelect.value;
    
    // Prepare data for API
    const requestData = {
        tasks: tasks.map(task => ({
            id: task.id,
            title: task.title,
            due_date: task.due_date,
            estimated_hours: task.estimated_hours,
            importance: task.importance,
            dependencies: task.dependencies
        })),
        strategy: strategy
    };
    
    // Send to backend API
    fetch('http://localhost:8000/api/tasks/analyze/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            displayError(data.error, data.details || data.cycle_details);
        } else {
            displayResults(data.tasks);
        }
    })
    .catch(error => {
        displayError('Connection error', [error.message]);
    });
}

// Display error message
function displayError(title, details) {
    noResultsMessage.style.display = 'none';
    resultsList.innerHTML = `
        <div class="error-message">
            <strong>${title}</strong>
            ${details ? `<p>${details.join ? details.join('<br>') : details}</p>` : ''}
        </div>
    `;
}

// Display results
function displayResults(sortedTasks) {
    noResultsMessage.style.display = 'none';
    
    if (!sortedTasks || sortedTasks.length === 0) {
        resultsList.innerHTML = '<p>No tasks to display</p>';
        return;
    }
    
    resultsList.innerHTML = sortedTasks.map(task => {
        // Determine priority level for styling
        let priorityLevel = 'low-priority';
        if (task.priority_score >= 70) {
            priorityLevel = 'high-priority';
        } else if (task.priority_score >= 40) {
            priorityLevel = 'medium-priority';
        }
        
        return `
            <div class="task-card ${priorityLevel}">
                <div class="task-header">
                    <div class="task-title">${escapeHtml(task.title)}</div>
                    <div class="priority-score">${task.priority_score}</div>
                </div>
                <div class="task-details">
                    <div class="detail-item">
                        <span class="detail-label">Due Date</span>
                        <span class="detail-value">${task.due_date}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Estimated Hours</span>
                        <span class="detail-value">${task.estimated_hours}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Importance</span>
                        <span class="detail-value">${task.importance}/10</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Dependencies</span>
                        <span class="detail-value">${task.dependencies && task.dependencies.length > 0 ? task.dependencies.join(', ') : 'None'}</span>
                    </div>
                </div>
                <div class="explanation">
                    <div class="explanation-title">Why this priority?</div>
                    <div>${escapeHtml(task.explanation)}</div>
                </div>
            </div>
        `;
    }).join('');
}

// Utility function to escape HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    
    return text.toString().replace(/[&<>"']/g, m => map[m]);
}

// Get top 3 suggestions (for future use)
function getSuggestions() {
    if (tasks.length === 0) {
        alert('Please add tasks first');
        return;
    }
    
    // Show loading state
    noResultsMessage.style.display = 'none';
    resultsList.innerHTML = '<div class="loading">Finding top tasks...</div>';
    
    // Prepare data for API
    const requestData = {
        tasks: tasks.map(task => ({
            id: task.id,
            title: task.title,
            due_date: task.due_date,
            estimated_hours: task.estimated_hours,
            importance: task.importance,
            dependencies: task.dependencies
        }))
    };
    
    // Send to backend API
    fetch('http://localhost:8000/api/tasks/suggest/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            displayError(data.error, data.details || data.cycle_details);
        } else {
            displayResults(data.tasks);
        }
    })
    .catch(error => {
        displayError('Connection error', [error.message]);
    });
}