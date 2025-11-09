# Exercise 5: Complete Server

## Objective

Build a comprehensive MCP server that combines tools, resources, and prompts into a cohesive application, demonstrating production-ready patterns and best practices.

## What You'll Learn

- Integrating tools, resources, and prompts
- Production-ready error handling
- Configuration management
- Logging best practices
- Testing MCP servers
- Deployment considerations

## Background

This final exercise brings together everything you've learned. You'll build a complete task management server that demonstrates how to structure a real-world MCP application.

The server will provide:
- **Tools**: Create, read, update, delete tasks
- **Resources**: Access task data and statistics
- **Prompts**: Templates for task management workflows

## Setup

```bash
cd exercises/05-complete-server

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv add "mcp[cli]"
```

## Task

Create a task management server with the following capabilities:

### Tools
1. `create_task` - Create a new task
2. `list_tasks` - List all tasks with optional filtering
3. `update_task` - Update an existing task
4. `delete_task` - Delete a task
5. `get_task_stats` - Get statistics about tasks

### Resources
1. `tasks://all` - All tasks as JSON
2. `tasks://stats` - Task statistics
3. `tasks://by-status/{status}` - Tasks filtered by status

### Prompts
1. `plan_day` - Template for daily planning
2. `review_week` - Template for weekly review
3. `prioritize_tasks` - Template for task prioritization

## Implementation Guide

### Step 1: Set up the data model

Create `task_manager.py`:

```python
from mcp.server.fastmcp import FastMCP
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("task-manager")

# Data model
@dataclass
class Task:
    id: str
    title: str
    description: str
    status: str  # "todo", "in_progress", "done"
    priority: str  # "low", "medium", "high"
    created_at: str
    updated_at: str
    
    def to_dict(self) -> dict:
        return asdict(self)

# In-memory storage (in production, use a database)
tasks: Dict[str, Task] = {}
task_counter = 0
```

### Step 2: Implement helper functions

```python
def generate_task_id() -> str:
    """Generate a unique task ID."""
    global task_counter
    task_counter += 1
    return f"task-{task_counter}"

def get_current_timestamp() -> str:
    """Get current timestamp as ISO format string."""
    return datetime.now().isoformat()

def validate_status(status: str) -> bool:
    """Validate task status."""
    return status in ["todo", "in_progress", "done"]

def validate_priority(priority: str) -> bool:
    """Validate task priority."""
    return priority in ["low", "medium", "high"]
```

### Step 3: Implement tools

```python
@mcp.tool()
async def create_task(
    title: str,
    description: str = "",
    priority: str = "medium"
) -> str:
    """Create a new task.
    
    Args:
        title: Task title
        description: Task description (optional)
        priority: Task priority - "low", "medium", or "high" (default: "medium")
    """
    if not validate_priority(priority):
        return f"Error: Invalid priority '{priority}'. Must be 'low', 'medium', or 'high'."
    
    task_id = generate_task_id()
    timestamp = get_current_timestamp()
    
    task = Task(
        id=task_id,
        title=title,
        description=description,
        status="todo",
        priority=priority,
        created_at=timestamp,
        updated_at=timestamp
    )
    
    tasks[task_id] = task
    logger.info(f"Created task {task_id}: {title}")
    
    return f"Created task {task_id}: {title}"

@mcp.tool()
async def list_tasks(status: Optional[str] = None, priority: Optional[str] = None) -> str:
    """List all tasks with optional filtering.
    
    Args:
        status: Filter by status - "todo", "in_progress", or "done" (optional)
        priority: Filter by priority - "low", "medium", or "high" (optional)
    """
    if not tasks:
        return "No tasks found."
    
    filtered_tasks = list(tasks.values())
    
    if status:
        if not validate_status(status):
            return f"Error: Invalid status '{status}'."
        filtered_tasks = [t for t in filtered_tasks if t.status == status]
    
    if priority:
        if not validate_priority(priority):
            return f"Error: Invalid priority '{priority}'."
        filtered_tasks = [t for t in filtered_tasks if t.priority == priority]
    
    if not filtered_tasks:
        return "No tasks match the filters."
    
    result = []
    for task in filtered_tasks:
        result.append(
            f"[{task.id}] {task.title} "
            f"(Status: {task.status}, Priority: {task.priority})"
        )
    
    return "\n".join(result)

@mcp.tool()
async def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None
) -> str:
    """Update an existing task.
    
    Args:
        task_id: ID of the task to update
        title: New title (optional)
        description: New description (optional)
        status: New status - "todo", "in_progress", or "done" (optional)
        priority: New priority - "low", "medium", or "high" (optional)
    """
    if task_id not in tasks:
        return f"Error: Task {task_id} not found."
    
    task = tasks[task_id]
    
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if status is not None:
        if not validate_status(status):
            return f"Error: Invalid status '{status}'."
        task.status = status
    if priority is not None:
        if not validate_priority(priority):
            return f"Error: Invalid priority '{priority}'."
        task.priority = priority
    
    task.updated_at = get_current_timestamp()
    logger.info(f"Updated task {task_id}")
    
    return f"Updated task {task_id}"

@mcp.tool()
async def delete_task(task_id: str) -> str:
    """Delete a task.
    
    Args:
        task_id: ID of the task to delete
    """
    if task_id not in tasks:
        return f"Error: Task {task_id} not found."
    
    task = tasks.pop(task_id)
    logger.info(f"Deleted task {task_id}: {task.title}")
    
    return f"Deleted task {task_id}: {task.title}"

@mcp.tool()
async def get_task_stats() -> str:
    """Get statistics about tasks."""
    if not tasks:
        return "No tasks to analyze."
    
    total = len(tasks)
    by_status = {"todo": 0, "in_progress": 0, "done": 0}
    by_priority = {"low": 0, "medium": 0, "high": 0}
    
    for task in tasks.values():
        by_status[task.status] += 1
        by_priority[task.priority] += 1
    
    return f"""Task Statistics:

Total Tasks: {total}

By Status:
- To Do: {by_status['todo']}
- In Progress: {by_status['in_progress']}
- Done: {by_status['done']}

By Priority:
- High: {by_priority['high']}
- Medium: {by_priority['medium']}
- Low: {by_priority['low']}

Completion Rate: {(by_status['done'] / total * 100):.1f}%
"""
```

### Step 4: Implement resources

```python
@mcp.resource("tasks://all")
async def get_all_tasks() -> str:
    """Get all tasks as JSON."""
    if not tasks:
        return json.dumps({"tasks": []}, indent=2)
    
    task_list = [task.to_dict() for task in tasks.values()]
    return json.dumps({"tasks": task_list}, indent=2)

@mcp.resource("tasks://stats")
async def get_stats_resource() -> str:
    """Get task statistics as JSON."""
    if not tasks:
        return json.dumps({"total": 0, "by_status": {}, "by_priority": {}}, indent=2)
    
    total = len(tasks)
    by_status = {"todo": 0, "in_progress": 0, "done": 0}
    by_priority = {"low": 0, "medium": 0, "high": 0}
    
    for task in tasks.values():
        by_status[task.status] += 1
        by_priority[task.priority] += 1
    
    stats = {
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
        "completion_rate": round(by_status['done'] / total * 100, 1) if total > 0 else 0
    }
    
    return json.dumps(stats, indent=2)

@mcp.resource("tasks://by-status/{status}")
async def get_tasks_by_status(status: str) -> str:
    """Get tasks filtered by status.
    
    Args:
        status: Status to filter by ("todo", "in_progress", or "done")
    """
    if not validate_status(status):
        return json.dumps({"error": f"Invalid status: {status}"}, indent=2)
    
    filtered = [task.to_dict() for task in tasks.values() if task.status == status]
    return json.dumps({"status": status, "tasks": filtered}, indent=2)
```

### Step 5: Implement prompts

```python
@mcp.prompt()
async def plan_day() -> str:
    """Template for daily task planning."""
    return """Let's plan your day effectively!

## Morning Review (5 minutes)

1. Review all tasks and their priorities
2. Identify urgent and important tasks
3. Check for any blockers or dependencies

## Daily Goals

Select 3-5 tasks to focus on today:
- [ ] High priority task 1
- [ ] High priority task 2
- [ ] Medium priority task 3

## Time Blocking

Allocate specific time blocks:
- Morning (9-12): [Focus work on highest priority]
- Afternoon (1-4): [Secondary tasks]
- End of day (4-5): [Quick wins and planning tomorrow]

## Success Criteria

What does a successful day look like?
- Completed high priority tasks
- Made progress on key projects
- No urgent items left unaddressed

Use the task management tools to update task statuses as you progress!
"""

@mcp.prompt()
async def review_week() -> str:
    """Template for weekly task review."""
    return """Weekly Task Review

## Completed This Week

Review all tasks marked as "done":
- What went well?
- What took longer than expected?
- What can be improved?

## In Progress

Review tasks still in progress:
- Are they blocked?
- Do they need to be re-prioritized?
- Should any be broken into smaller tasks?

## Planning Next Week

1. Review upcoming priorities
2. Create new tasks for next week
3. Set realistic goals
4. Identify potential blockers

## Metrics

- Tasks completed: [Check stats]
- Completion rate: [Check stats]
- Average time per task: [Estimate]

## Action Items

- [ ] Archive completed tasks
- [ ] Update priorities
- [ ] Create tasks for next week
- [ ] Schedule time blocks

Use get_task_stats to see your progress!
"""

@mcp.prompt()
async def prioritize_tasks() -> str:
    """Template for task prioritization using Eisenhower Matrix."""
    return """Task Prioritization - Eisenhower Matrix

Categorize your tasks into four quadrants:

## Urgent & Important (Do First)
Tasks that need immediate attention and have significant impact.
- Deadlines today or tomorrow
- Critical bugs or issues
- Important meetings

Action: Do these immediately

## Important but Not Urgent (Schedule)
Tasks that are important for long-term goals but don't have immediate deadlines.
- Strategic planning
- Skill development
- Relationship building

Action: Schedule specific time blocks

## Urgent but Not Important (Delegate)
Tasks that need to be done soon but don't require your specific expertise.
- Some emails and messages
- Routine tasks
- Some meetings

Action: Delegate if possible, or batch process

## Neither Urgent nor Important (Eliminate)
Tasks that don't contribute to your goals.
- Busy work
- Time wasters
- Unnecessary tasks

Action: Consider eliminating or postponing

## Prioritization Process

1. List all current tasks
2. Categorize each task into a quadrant
3. Update task priorities accordingly:
   - Urgent & Important → High priority
   - Important but Not Urgent → Medium priority
   - Urgent but Not Important → Low priority
   - Neither → Consider deleting

Use update_task to adjust priorities based on this analysis!
"""
```

### Step 6: Add the main function

```python
def main():
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
```

## Testing

### Manual Testing Workflow

1. Create some tasks:
```
create_task("Write documentation", "Complete the README", "high")
create_task("Fix bug #123", "Memory leak in parser", "high")
create_task("Update dependencies", "", "low")
```

2. List tasks:
```
list_tasks()
list_tasks(status="todo")
list_tasks(priority="high")
```

3. Update a task:
```
update_task("task-1", status="in_progress")
```

4. Get statistics:
```
get_task_stats()
```

5. Access resources:
- View `tasks://all`
- View `tasks://stats`
- View `tasks://by-status/todo`

6. Use prompts:
- Use `plan_day` prompt
- Use `prioritize_tasks` prompt

### Using MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv --directory /absolute/path/to/05-complete-server run task_manager.py
```

## Best Practices Demonstrated

1. **Data Validation**: All inputs are validated
2. **Error Handling**: Graceful error messages
3. **Logging**: Proper logging to stderr
4. **Type Hints**: Complete type annotations
5. **Documentation**: Comprehensive docstrings
6. **Separation of Concerns**: Clear separation between tools, resources, and prompts
7. **Consistent API**: Predictable function signatures
8. **User Feedback**: Clear success/error messages

## Production Considerations

### Database Integration

Replace in-memory storage with a database:

```python
import sqlite3

def init_db():
    conn = sqlite3.connect('tasks.db')
    # Create tables, etc.
    
# Use database operations instead of dict
```

### Configuration

Add environment-based configuration:

```python
import os

CONFIG = {
    "database_url": os.getenv("DATABASE_URL", "sqlite:///tasks.db"),
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
}
```

### Error Handling

Add more sophisticated error handling:

```python
from typing import Union, Tuple

def safe_operation() -> Tuple[bool, str]:
    try:
        # Operation
        return True, "Success"
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        return False, f"Error: {str(e)}"
```

### Testing

Add unit tests:

```python
import pytest

def test_create_task():
    result = await create_task("Test", "Description", "high")
    assert "Created task" in result
```

## Verification Checklist

- [ ] All tools are implemented and working
- [ ] All resources are accessible
- [ ] All prompts provide useful templates
- [ ] Input validation is comprehensive
- [ ] Error messages are clear and helpful
- [ ] Logging is appropriate
- [ ] No `print()` statements
- [ ] Type hints are complete
- [ ] Docstrings are comprehensive
- [ ] Server runs without errors

## Challenge Extensions

1. Add task dependencies (task A must complete before task B)
2. Implement task tags/categories
3. Add due dates and reminders
4. Create a task search tool
5. Add task history/audit log
6. Implement task templates
7. Add collaboration features (assign tasks to users)
8. Create recurring tasks
9. Add time tracking
10. Export tasks to different formats (CSV, JSON, Markdown)

## Solution

Check `solution.py` for a complete implementation.

## Congratulations!

You've completed all five exercises and learned how to build production-ready MCP servers! You now understand:

- Tools for executing functions
- Resources for exposing data
- Prompts for guiding users
- Best practices for MCP development
- Production considerations

## Next Steps

- Build your own MCP server for your use case
- Contribute to the MCP ecosystem
- Share your servers with the community
- Explore advanced MCP features

Check out the [MCP documentation](https://modelcontextprotocol.io) for more information!
