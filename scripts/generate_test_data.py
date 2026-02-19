#!/usr/bin/env python3
"""
Generate test data for performance testing
Tasks: T055, T064, T073, T113
Generates 10,000 tasks with varied attributes for performance validation
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import random

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from src.database import get_session
from src.models.task import Task, TaskStatus, TaskPriority, RecurrencePattern
from uuid import uuid4


PRIORITIES = [TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH, TaskPriority.URGENT]
STATUSES = [TaskStatus.INCOMPLETE, TaskStatus.COMPLETE]
RECURRENCE_PATTERNS = [RecurrencePattern.NONE, RecurrencePattern.DAILY, RecurrencePattern.WEEKLY, RecurrencePattern.MONTHLY]

TAG_POOL = [
    "work", "personal", "urgent", "important", "meeting", "project",
    "client", "internal", "research", "development", "testing", "bug",
    "feature", "documentation", "review", "planning", "design", "deployment"
]

TITLE_TEMPLATES = [
    "Complete {} project proposal",
    "Review {} documentation",
    "Fix {} bug in production",
    "Implement {} feature",
    "Test {} integration",
    "Deploy {} to production",
    "Update {} configuration",
    "Refactor {} codebase",
    "Optimize {} performance",
    "Debug {} issue"
]

DESCRIPTION_TEMPLATES = [
    "This task involves working on {} with focus on {}. Priority is {} due to {}.",
    "Need to address {} for {} project. Expected completion by {}.",
    "Critical {} work required for {} initiative. Stakeholders: {}.",
    "Routine {} maintenance for {} system. No blockers identified.",
    "Strategic {} planning for {} quarter. Dependencies: {}."
]


async def generate_test_data(count: int = 10000, user_id: str = "test-user"):
    """Generate test tasks for performance testing"""

    print(f"=== Generating {count} test tasks ===")
    print(f"User ID: {user_id}")
    print(f"Start time: {datetime.utcnow().isoformat()}")
    print()

    async with get_session() as session:
        tasks_created = 0
        batch_size = 100

        for i in range(0, count, batch_size):
            batch_tasks = []

            for j in range(batch_size):
                task_num = i + j
                if task_num >= count:
                    break

                # Generate varied task attributes
                priority = random.choice(PRIORITIES)
                status = random.choice(STATUSES)
                recurrence = random.choice(RECURRENCE_PATTERNS)

                # Generate 0-5 tags per task
                num_tags = random.randint(0, 5)
                tags = random.sample(TAG_POOL, num_tags) if num_tags > 0 else []

                # Generate title with searchable content
                title = random.choice(TITLE_TEMPLATES).format(f"Task{task_num}")

                # Generate description with searchable content
                description = random.choice(DESCRIPTION_TEMPLATES).format(
                    random.choice(["analysis", "implementation", "testing", "deployment"]),
                    random.choice(["Q1", "Q2", "Q3", "Q4"]),
                    random.choice(["high", "medium", "low"])
                )

                # Generate due date (50% of tasks have due dates)
                due_date = None
                if random.random() > 0.5:
                    days_offset = random.randint(-30, 90)  # Past and future dates
                    due_date = datetime.utcnow() + timedelta(days=days_offset)

                # Create task
                task = Task(
                    id=str(uuid4()),
                    user_id=user_id,
                    title=title,
                    description=description,
                    status=status,
                    priority=priority,
                    tags=tags,
                    due_date=due_date,
                    recurrence_pattern=recurrence,
                    reminder_time=None,  # Don't schedule reminders for test data
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 365)),
                    updated_at=datetime.utcnow(),
                    completed_at=datetime.utcnow() if status == TaskStatus.COMPLETE else None
                )

                batch_tasks.append(task)

            # Bulk insert batch
            session.add_all(batch_tasks)
            await session.commit()

            tasks_created += len(batch_tasks)

            if tasks_created % 1000 == 0:
                print(f"Progress: {tasks_created}/{count} tasks created ({tasks_created/count*100:.1f}%)")

        print()
        print(f"✅ Successfully created {tasks_created} test tasks")
        print(f"End time: {datetime.utcnow().isoformat()}")
        print()

        # Print statistics
        print("=== Test Data Statistics ===")

        # Count by priority
        for priority in PRIORITIES:
            result = await session.execute(
                f"SELECT COUNT(*) FROM tasks WHERE user_id = '{user_id}' AND priority = '{priority.value}'"
            )
            count = result.scalar()
            print(f"Priority {priority.value}: {count} tasks")

        # Count by status
        for status in STATUSES:
            result = await session.execute(
                f"SELECT COUNT(*) FROM tasks WHERE user_id = '{user_id}' AND status = '{status.value}'"
            )
            count = result.scalar()
            print(f"Status {status.value}: {count} tasks")

        # Count with tags
        result = await session.execute(
            f"SELECT COUNT(*) FROM tasks WHERE user_id = '{user_id}' AND jsonb_array_length(tags) > 0"
        )
        count = result.scalar()
        print(f"Tasks with tags: {count}")

        # Count with due dates
        result = await session.execute(
            f"SELECT COUNT(*) FROM tasks WHERE user_id = '{user_id}' AND due_date IS NOT NULL"
        )
        count = result.scalar()
        print(f"Tasks with due dates: {count}")

        print()
        print("Next steps:")
        print("1. Run performance tests: ./scripts/test-performance.sh")
        print("2. Verify search performance: psql $DATABASE_URL -f scripts/test-search-performance.sql")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate test data for performance testing")
    parser.add_argument("--count", type=int, default=10000, help="Number of tasks to generate")
    parser.add_argument("--user-id", type=str, default="test-user", help="User ID for test tasks")

    args = parser.parse_args()

    asyncio.run(generate_test_data(args.count, args.user_id))
