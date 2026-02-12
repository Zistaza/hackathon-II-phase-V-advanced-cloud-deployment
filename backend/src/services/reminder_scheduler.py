"""
Reminder scheduler utility using Dapr Jobs API
"""
from dapr.clients import DaprClient
from datetime import datetime, timedelta
from typing import Optional
import re
import logging

logger = logging.getLogger(__name__)


def parse_reminder_time(reminder_time: str, due_date: datetime) -> datetime:
    """
    Parse reminder time string and calculate scheduled time

    Args:
        reminder_time: Relative time string (e.g., "1h", "2d", "1w")
        due_date: Task due date

    Returns:
        datetime: Scheduled reminder time (UTC)

    Raises:
        ValueError: If reminder_time format is invalid
    """
    # Parse reminder_time pattern: <number><unit>
    # Units: h (hours), d (days), w (weeks)
    match = re.match(r'^(\d+)([hdw])$', reminder_time)

    if not match:
        raise ValueError(
            f"Invalid reminder_time format: {reminder_time}. "
            "Expected format: <number><h|d|w> (e.g., '1h', '2d', '1w')"
        )

    amount = int(match.group(1))
    unit = match.group(2)

    # Calculate time delta
    if unit == 'h':
        delta = timedelta(hours=amount)
    elif unit == 'd':
        delta = timedelta(days=amount)
    elif unit == 'w':
        delta = timedelta(weeks=amount)
    else:
        raise ValueError(f"Invalid time unit: {unit}")

    # Calculate scheduled time (due_date - delta)
    scheduled_time = due_date - delta

    # Validate scheduled time is in the future
    if scheduled_time < datetime.utcnow():
        raise ValueError(
            f"Reminder time {scheduled_time.isoformat()} is in the past. "
            "Please set a due date further in the future or reduce reminder advance time."
        )

    return scheduled_time


async def schedule_reminder(
    task_id: str,
    user_id: str,
    task_title: str,
    due_date: datetime,
    reminder_time: str
) -> str:
    """
    Schedule a reminder job using Dapr Jobs API

    Args:
        task_id: Task ID
        user_id: User ID
        task_title: Task title for notification
        due_date: Task due date
        reminder_time: Relative reminder time (e.g., "1h")

    Returns:
        str: Job ID

    Raises:
        ValueError: If reminder_time is invalid or scheduled time is in past
        Exception: If Dapr Jobs API fails
    """
    try:
        # Parse reminder time and calculate scheduled time
        scheduled_time = parse_reminder_time(reminder_time, due_date)

        # Generate unique job ID
        job_id = f"reminder-{task_id}-{int(scheduled_time.timestamp())}"

        # Prepare job data
        job_data = {
            "task_id": task_id,
            "user_id": user_id,
            "task_title": task_title,
            "due_date": due_date.isoformat(),
            "reminder_message": f"Task '{task_title}' is due in {reminder_time}",
            "scheduled_time": scheduled_time.isoformat()
        }

        # Schedule job via Dapr Jobs API
        async with DaprClient() as client:
            # Note: Dapr Jobs API uses HTTP endpoint
            # POST http://localhost:3500/v1.0-alpha1/jobs/{jobName}
            await client.invoke_method(
                app_id="dapr",
                method_name=f"v1.0-alpha1/jobs/{job_id}",
                data={
                    "schedule": scheduled_time.isoformat(),
                    "data": job_data,
                    "dueTime": scheduled_time.isoformat()
                },
                http_verb="POST"
            )

        logger.info(
            f"Scheduled reminder job {job_id} for task {task_id} "
            f"at {scheduled_time.isoformat()}"
        )

        return job_id

    except ValueError as e:
        logger.error(f"Invalid reminder configuration: {str(e)}")
        raise

    except Exception as e:
        logger.error(f"Failed to schedule reminder for task {task_id}: {str(e)}")
        raise


async def cancel_reminder(job_id: str) -> bool:
    """
    Cancel a scheduled reminder job

    Args:
        job_id: Job ID to cancel

    Returns:
        bool: True if cancelled successfully

    Raises:
        Exception: If Dapr Jobs API fails
    """
    try:
        async with DaprClient() as client:
            # DELETE http://localhost:3500/v1.0-alpha1/jobs/{jobName}
            await client.invoke_method(
                app_id="dapr",
                method_name=f"v1.0-alpha1/jobs/{job_id}",
                http_verb="DELETE"
            )

        logger.info(f"Cancelled reminder job {job_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to cancel reminder job {job_id}: {str(e)}")
        raise


async def get_reminder_status(job_id: str) -> Optional[dict]:
    """
    Get status of a scheduled reminder job

    Args:
        job_id: Job ID to check

    Returns:
        dict: Job status information or None if not found

    Raises:
        Exception: If Dapr Jobs API fails
    """
    try:
        async with DaprClient() as client:
            # GET http://localhost:3500/v1.0-alpha1/jobs/{jobName}
            response = await client.invoke_method(
                app_id="dapr",
                method_name=f"v1.0-alpha1/jobs/{job_id}",
                http_verb="GET"
            )

        return response.json() if response else None

    except Exception as e:
        logger.warning(f"Failed to get reminder job status for {job_id}: {str(e)}")
        return None
