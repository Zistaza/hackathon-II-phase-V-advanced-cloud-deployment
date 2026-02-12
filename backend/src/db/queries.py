"""
Query builders for advanced task filtering, searching, and sorting
"""
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import Query
from backend.src.models.task import Task, TaskPriority, TaskStatus
from datetime import datetime, timedelta
from typing import Optional, List


def build_search_query(base_query: Query, search_term: str) -> Query:
    """
    Build full-text search query using PostgreSQL tsvector

    Args:
        base_query: Base SQLAlchemy query
        search_term: Search keyword(s)

    Returns:
        Query with search filter applied
    """
    if not search_term or search_term.strip() == "":
        return base_query

    # Use PostgreSQL full-text search with ts_rank for relevance
    search_query = func.plainto_tsquery('english', search_term)

    return base_query.where(
        func.to_tsvector('english',
            func.coalesce(Task.title, '') + ' ' + func.coalesce(Task.description, '')
        ).op('@@')(search_query)
    ).order_by(
        desc(func.ts_rank(
            func.to_tsvector('english',
                func.coalesce(Task.title, '') + ' ' + func.coalesce(Task.description, '')
            ),
            search_query
        ))
    )


def build_filter_query(
    base_query: Query,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    tags: Optional[List[str]] = None,
    due_date_filter: Optional[str] = None
) -> Query:
    """
    Build filter query for tasks based on multiple criteria

    Args:
        base_query: Base SQLAlchemy query
        status: Filter by task status (complete/incomplete)
        priority: Filter by priority level
        tags: Filter by tags (AND logic - task must have all specified tags)
        due_date_filter: Filter by due date range (overdue/today/this_week/this_month)

    Returns:
        Query with filters applied
    """
    filters = []

    # Status filter
    if status:
        filters.append(Task.status == status)

    # Priority filter
    if priority:
        filters.append(Task.priority == priority)

    # Tags filter (AND logic - task must contain all specified tags)
    if tags and len(tags) > 0:
        # Use JSONB containment operator (@>)
        filters.append(Task.tags.op('@>')(tags))

    # Due date filter
    if due_date_filter:
        now = datetime.utcnow()

        if due_date_filter == "overdue":
            filters.append(and_(
                Task.due_date.isnot(None),
                Task.due_date < now,
                Task.status == TaskStatus.INCOMPLETE
            ))

        elif due_date_filter == "today":
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            filters.append(and_(
                Task.due_date >= today_start,
                Task.due_date < today_end
            ))

        elif due_date_filter == "this_week":
            week_start = now - timedelta(days=now.weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            week_end = week_start + timedelta(days=7)
            filters.append(and_(
                Task.due_date >= week_start,
                Task.due_date < week_end
            ))

        elif due_date_filter == "this_month":
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                month_end = month_start.replace(year=now.year + 1, month=1)
            else:
                month_end = month_start.replace(month=now.month + 1)
            filters.append(and_(
                Task.due_date >= month_start,
                Task.due_date < month_end
            ))

    # Apply all filters with AND logic
    if filters:
        return base_query.where(and_(*filters))

    return base_query


def build_sort_query(
    base_query: Query,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> Query:
    """
    Build sort query for tasks

    Args:
        base_query: Base SQLAlchemy query
        sort_by: Field to sort by (created_at/due_date/priority/status)
        sort_order: Sort direction (asc/desc)

    Returns:
        Query with sorting applied
    """
    # Map sort fields to Task model attributes
    sort_fields = {
        "created_at": Task.created_at,
        "due_date": Task.due_date,
        "priority": Task.priority,
        "status": Task.status,
        "updated_at": Task.updated_at,
        "completed_at": Task.completed_at
    }

    # Priority ordering (urgent > high > medium > low)
    priority_order = {
        TaskPriority.URGENT: 4,
        TaskPriority.HIGH: 3,
        TaskPriority.MEDIUM: 2,
        TaskPriority.LOW: 1
    }

    sort_field = sort_fields.get(sort_by, Task.created_at)

    # Special handling for priority sorting
    if sort_by == "priority":
        if sort_order == "asc":
            # Low to Urgent
            return base_query.order_by(asc(Task.priority))
        else:
            # Urgent to Low
            return base_query.order_by(desc(Task.priority))

    # Handle NULL values for due_date (put NULLs last)
    if sort_by == "due_date":
        if sort_order == "asc":
            return base_query.order_by(asc(sort_field.nullslast()))
        else:
            return base_query.order_by(desc(sort_field.nullslast()))

    # Standard sorting
    if sort_order == "asc":
        return base_query.order_by(asc(sort_field))
    else:
        return base_query.order_by(desc(sort_field))


def build_combined_query(
    user_id: str,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    tags: Optional[List[str]] = None,
    due_date_filter: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    limit: int = 50,
    offset: int = 0
) -> Query:
    """
    Build complete query with all filters, search, and sorting

    Args:
        user_id: User ID to filter tasks
        status: Filter by task status
        priority: Filter by priority level
        tags: Filter by tags
        due_date_filter: Filter by due date range
        search: Search term for full-text search
        sort_by: Field to sort by
        sort_order: Sort direction
        limit: Maximum number of results
        offset: Number of results to skip (pagination)

    Returns:
        Complete query ready for execution
    """
    # Start with base query filtered by user_id
    query = select(Task).where(Task.user_id == user_id)

    # Apply filters
    query = build_filter_query(query, status, priority, tags, due_date_filter)

    # Apply search (if provided, search takes precedence for ordering)
    if search:
        query = build_search_query(query, search)
    else:
        # Apply sorting only if no search (search has its own relevance ordering)
        query = build_sort_query(query, sort_by, sort_order)

    # Apply pagination
    query = query.limit(limit).offset(offset)

    return query
