from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select
from ..models.user import CurrentUser
from ..middleware.auth import get_current_user
from ..models.user_model import User
from ..database import get_session
from ..models.task_model import Task, TaskCreate, TaskUpdate, TaskResponse
from ..events.publishers import get_task_event_publisher
from datetime import datetime
from uuid import UUID

router = APIRouter()


@router.get("/{user_id}/tasks", response_model=List[TaskResponse])
async def get_tasks(
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get all tasks for the authenticated user

    Args:
        user_id: User ID from URL path
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        List of tasks belonging to the user
    """
    # Verify that the user_id in the URL matches the user_id from the JWT
    # This ensures multi-tenant data isolation
    if user_id != current_user.user_id:
        # Log the mismatch for debugging
        print(f"DEBUG: User ID mismatch in get tasks - URL user_id: {user_id}, JWT user_id: {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access another user's tasks"
        )

    # Query the database for tasks belonging to the current user
    statement = select(Task).where(Task.user_id == current_user.user_id)
    results = session.exec(statement)
    tasks = results.all()

    return [TaskResponse.from_task(task) for task in tasks]


@router.post("/{user_id}/tasks", response_model=TaskResponse)
async def create_task(
    user_id: str,
    task: TaskCreate,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user

    Args:
        user_id: User ID from URL path
        task: Task data to create
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        Created task
    """
    # Verify that the user_id in the URL matches the user_id from the JWT
    if user_id != current_user.user_id:
        # Log the mismatch for debugging
        print(f"DEBUG: User ID mismatch in task creation - URL user_id: {user_id}, JWT user_id: {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot create tasks for another user"
        )

    # Create a new task record in the database with Phase V features
    db_task = Task(
        title=task.title,
        description=task.description,
        completed=task.completed,
        priority=task.priority if hasattr(task, 'priority') else "medium",
        tags=task.tags if hasattr(task, 'tags') else [],
        due_date=task.due_date if hasattr(task, 'due_date') else None,
        recurrence_pattern=task.recurrence_pattern if hasattr(task, 'recurrence_pattern') else "none",
        reminder_time=task.reminder_time if hasattr(task, 'reminder_time') else None,
        user_id=current_user.user_id
    )

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Publish task.created event
    try:
        publisher = get_task_event_publisher()
        await publisher.publish_task_created(
            task_id=UUID(db_task.id),
            title=db_task.title,
            created_by=UUID(current_user.user_id),
            description=db_task.description,
            status="completed" if db_task.completed else "pending",
            priority=db_task.priority,
            due_date=db_task.due_date,
            tags=db_task.tags,
            user_id=UUID(current_user.user_id),
        )
    except Exception as e:
        # Log the error but don't fail the request
        print(f"Warning: Failed to publish task.created event: {e}")

    return TaskResponse.from_task(db_task)


@router.get("/{user_id}/tasks/{id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific task for the authenticated user

    Args:
        user_id: User ID from URL path
        id: Task ID to retrieve
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        Specific task if it belongs to the user
    """
    # Verify that the user_id in the URL matches the user_id from the JWT
    if user_id != current_user.user_id:
        # Log the mismatch for debugging
        print(f"DEBUG: User ID mismatch in get task by ID - URL user_id: {user_id}, JWT user_id: {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot access another user's task"
        )

    # Query for the specific task in the database
    statement = select(Task).where(Task.id == id, Task.user_id == current_user.user_id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskResponse.from_task(db_task)


@router.put("/{user_id}/tasks/{id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    id: str,
    task_update: TaskUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update a specific task for the authenticated user

    Args:
        user_id: User ID from URL path
        id: Task ID to update
        task_update: Updated task data
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        Updated task
    """
    # Verify that the user_id in the URL matches the user_id from the JWT
    if user_id != current_user.user_id:
        # Log the mismatch for debugging
        print(f"DEBUG: User ID mismatch in update task - URL user_id: {user_id}, JWT user_id: {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot update another user's task"
        )

    # Query for the specific task in the database
    statement = select(Task).where(Task.id == id, Task.user_id == current_user.user_id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update the task with provided fields
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db_task.updated_at = datetime.utcnow()
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Publish task.updated event
    try:
        publisher = get_task_event_publisher()
        await publisher.publish_task_updated(
            task_id=UUID(db_task.id),
            updated_fields=update_data,
            updated_by=UUID(current_user.user_id),
            user_id=UUID(current_user.user_id),
        )
    except Exception as e:
        # Log the error but don't fail the request
        print(f"Warning: Failed to publish task.updated event: {e}")

    return TaskResponse.from_task(db_task)


@router.delete("/{user_id}/tasks/{id}")
async def delete_task(
    user_id: str,
    id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Delete a specific task for the authenticated user

    Args:
        user_id: User ID from URL path
        id: Task ID to delete
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        Success message
    """
    # Verify that the user_id in the URL matches the user_id from the JWT
    if user_id != current_user.user_id:
        # Log the mismatch for debugging
        print(f"DEBUG: User ID mismatch in delete task - URL user_id: {user_id}, JWT user_id: {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot delete another user's task"
        )

    # Query for the specific task in the database
    statement = select(Task).where(Task.id == id, Task.user_id == current_user.user_id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Delete the task from the database
    session.delete(db_task)
    session.commit()

    # Publish task.deleted event
    try:
        publisher = get_task_event_publisher()
        await publisher.publish_task_deleted(
            task_id=UUID(db_task.id),
            deleted_by=UUID(current_user.user_id),
            user_id=UUID(current_user.user_id),
        )
    except Exception as e:
        # Log the error but don't fail the request
        print(f"Warning: Failed to publish task.deleted event: {e}")

    return {"message": f"Task {id} deleted successfully"}


@router.patch("/{user_id}/tasks/{id}/complete")
async def toggle_task_completion(
    user_id: str,
    id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle completion status of a specific task for the authenticated user

    Args:
        user_id: User ID from URL path
        id: Task ID to toggle
        current_user: Authenticated user from JWT token
        session: Database session

    Returns:
        Updated completion status
    """
    # Verify that the user_id in the URL matches the user_id from the JWT
    if user_id != current_user.user_id:
        # Log the mismatch for debugging
        print(f"DEBUG: User ID mismatch in toggle task completion - URL user_id: {user_id}, JWT user_id: {current_user.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Cannot modify another user's task"
        )

    # Query for the specific task in the database
    statement = select(Task).where(Task.id == id, Task.user_id == current_user.user_id)
    db_task = session.exec(statement).first()

    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Toggle the completion status
    db_task.completed = not db_task.completed
    db_task.updated_at = datetime.utcnow()

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Publish task.completed event if task was just completed
    if db_task.completed:
        try:
            publisher = get_task_event_publisher()
            await publisher.publish_task_completed(
                task_id=UUID(db_task.id),
                completed_by=UUID(current_user.user_id),
                user_id=UUID(current_user.user_id),
            )
        except Exception as e:
            # Log the error but don't fail the request
            print(f"Warning: Failed to publish task.completed event: {e}")

    return {"id": db_task.id, "completed": db_task.completed, "message": f"Task {id} completion status updated"}