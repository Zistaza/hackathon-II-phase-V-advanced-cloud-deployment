#!/usr/bin/env python3
"""
End-to-End Testing Script
Tasks: T111, T112
Tests all 7 user stories in sequence
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import httpx

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
JWT_TOKEN = os.getenv("JWT_TOKEN", "")
USER_ID = "test-user"

if not JWT_TOKEN:
    print("❌ ERROR: JWT_TOKEN environment variable not set")
    print("Please set: export JWT_TOKEN='your-jwt-token'")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}


async def test_user_story_1_reminders():
    """Test User Story 1: Due Dates & Reminders"""
    print("\n=== User Story 1: Due Dates & Reminders ===")

    async with httpx.AsyncClient() as client:
        # Create task with due date and reminder
        due_date = (datetime.utcnow() + timedelta(hours=2)).isoformat()
        response = await client.post(
            f"{BASE_URL}/api/tasks",
            headers=headers,
            json={
                "title": "Test Task with Reminder",
                "description": "This task has a reminder",
                "due_date": due_date,
                "reminder_time": "1h"
            }
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Task created: {data.get('task_id')}")
            print(f"✅ Reminder scheduled: {data.get('reminder_scheduled')}")
            return data.get('task_id')
        else:
            print(f"❌ Failed to create task: {response.text}")
            return None


async def test_user_story_2_priorities():
    """Test User Story 2: Priorities"""
    print("\n=== User Story 2: Priorities ===")

    async with httpx.AsyncClient() as client:
        # Create tasks with different priorities
        priorities = ["low", "medium", "high", "urgent"]
        task_ids = []

        for priority in priorities:
            response = await client.post(
                f"{BASE_URL}/api/tasks",
                headers=headers,
                json={
                    "title": f"Task with {priority} priority",
                    "priority": priority
                }
            )

            if response.status_code == 200:
                task_id = response.json().get('task_id')
                task_ids.append(task_id)
                print(f"✅ Created {priority} priority task: {task_id}")
            else:
                print(f"❌ Failed to create {priority} task")

        # Filter by priority
        response = await client.get(
            f"{BASE_URL}/api/tasks?priority=urgent",
            headers=headers
        )

        if response.status_code == 200:
            tasks = response.json().get('tasks', [])
            urgent_count = len([t for t in tasks if t['priority'] == 'urgent'])
            print(f"✅ Filter by urgent: {urgent_count} tasks found")
        else:
            print(f"❌ Failed to filter by priority")

        # Sort by priority
        response = await client.get(
            f"{BASE_URL}/api/tasks?sort_by=priority&sort_order=desc",
            headers=headers
        )

        if response.status_code == 200:
            tasks = response.json().get('tasks', [])
            print(f"✅ Sort by priority: {len(tasks)} tasks returned")
        else:
            print(f"❌ Failed to sort by priority")

        return task_ids


async def test_user_story_3_search():
    """Test User Story 3: Full-Text Search"""
    print("\n=== User Story 3: Full-Text Search ===")

    async with httpx.AsyncClient() as client:
        # Create tasks with searchable content
        await client.post(
            f"{BASE_URL}/api/tasks",
            headers=headers,
            json={
                "title": "Project Alpha Implementation",
                "description": "Implement core features for Project Alpha"
            }
        )

        await client.post(
            f"{BASE_URL}/api/tasks",
            headers=headers,
            json={
                "title": "Project Beta Testing",
                "description": "Test all features for Project Beta"
            }
        )

        # Search for "project"
        response = await client.get(
            f"{BASE_URL}/api/tasks?search=project",
            headers=headers
        )

        if response.status_code == 200:
            tasks = response.json().get('tasks', [])
            print(f"✅ Search 'project': {len(tasks)} tasks found")
        else:
            print(f"❌ Search failed")

        # Search for "alpha"
        response = await client.get(
            f"{BASE_URL}/api/tasks?search=alpha",
            headers=headers
        )

        if response.status_code == 200:
            tasks = response.json().get('tasks', [])
            print(f"✅ Search 'alpha': {len(tasks)} tasks found")
        else:
            print(f"❌ Search failed")


async def test_user_story_4_filtering_sorting():
    """Test User Story 4: Advanced Filtering & Sorting"""
    print("\n=== User Story 4: Advanced Filtering & Sorting ===")

    async with httpx.AsyncClient() as client:
        # Combined filter
        response = await client.get(
            f"{BASE_URL}/api/tasks?status=incomplete&priority=high&sort_by=due_date&sort_order=asc",
            headers=headers
        )

        if response.status_code == 200:
            tasks = response.json().get('tasks', [])
            print(f"✅ Combined filter: {len(tasks)} tasks found")
        else:
            print(f"❌ Combined filter failed")

        # Due date filter
        response = await client.get(
            f"{BASE_URL}/api/tasks?due_date_filter=this_week",
            headers=headers
        )

        if response.status_code == 200:
            tasks = response.json().get('tasks', [])
            print(f"✅ Due date filter (this_week): {len(tasks)} tasks found")
        else:
            print(f"❌ Due date filter failed")


async def test_user_story_5_tags():
    """Test User Story 5: Tags"""
    print("\n=== User Story 5: Tags ===")

    async with httpx.AsyncClient() as client:
        # Create task with tags
        response = await client.post(
            f"{BASE_URL}/api/tasks",
            headers=headers,
            json={
                "title": "Tagged Task",
                "tags": ["work", "urgent", "client"]
            }
        )

        if response.status_code == 200:
            task_id = response.json().get('task_id')
            print(f"✅ Task with tags created: {task_id}")
        else:
            print(f"❌ Failed to create tagged task")

        # Filter by single tag
        response = await client.get(
            f"{BASE_URL}/api/tasks?tags=work",
            headers=headers
        )

        if response.status_code == 200:
            tasks = response.json().get('tasks', [])
            print(f"✅ Filter by tag 'work': {len(tasks)} tasks found")
        else:
            print(f"❌ Tag filter failed")

        # Filter by multiple tags (AND logic)
        response = await client.get(
            f"{BASE_URL}/api/tasks?tags=work,urgent",
            headers=headers
        )

        if response.status_code == 200:
            tasks = response.json().get('tasks', [])
            print(f"✅ Filter by tags 'work' AND 'urgent': {len(tasks)} tasks found")
        else:
            print(f"❌ Multiple tag filter failed")


async def test_user_story_6_recurring():
    """Test User Story 6: Recurring Tasks"""
    print("\n=== User Story 6: Recurring Tasks ===")

    async with httpx.AsyncClient() as client:
        # Create recurring task
        due_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
        response = await client.post(
            f"{BASE_URL}/api/tasks",
            headers=headers,
            json={
                "title": "Daily Standup",
                "description": "Team standup meeting",
                "due_date": due_date,
                "recurrence_pattern": "daily"
            }
        )

        if response.status_code == 200:
            task_id = response.json().get('task_id')
            print(f"✅ Recurring task created: {task_id}")

            # Complete the task
            response = await client.post(
                f"{BASE_URL}/api/tasks/{task_id}/complete",
                headers=headers
            )

            if response.status_code == 200:
                print(f"✅ Task completed")
                print(f"⏳ Waiting 10 seconds for next instance generation...")
                await asyncio.sleep(10)

                # Check if next instance was created
                response = await client.get(
                    f"{BASE_URL}/api/tasks?search=Daily Standup",
                    headers=headers
                )

                if response.status_code == 200:
                    tasks = response.json().get('tasks', [])
                    incomplete_tasks = [t for t in tasks if t['status'] == 'incomplete']
                    if len(incomplete_tasks) > 0:
                        print(f"✅ Next instance generated: {incomplete_tasks[0]['task_id']}")
                    else:
                        print(f"❌ Next instance not found (may need more time)")
            else:
                print(f"❌ Failed to complete task")
        else:
            print(f"❌ Failed to create recurring task")


async def test_user_story_7_realtime_sync():
    """Test User Story 7: Real-Time Multi-Client Sync"""
    print("\n=== User Story 7: Real-Time Multi-Client Sync ===")
    print("⚠️  Manual testing required:")
    print("1. Open application in two browser tabs")
    print("2. Authenticate in both tabs")
    print("3. Create a task in tab 1")
    print("4. Verify task appears in tab 2 within 2 seconds")
    print("5. Update task priority in tab 2")
    print("6. Verify update appears in tab 1 within 2 seconds")
    print()
    print("WebSocket endpoint: ws://localhost:8000/ws/{user_id}?token={jwt_token}")


async def run_all_tests():
    """Run all user story tests in sequence"""
    print("=== Phase-V End-to-End Testing ===")
    print(f"Base URL: {BASE_URL}")
    print(f"User ID: {USER_ID}")
    print(f"Start time: {datetime.utcnow().isoformat()}")
    print()

    try:
        # Test each user story
        await test_user_story_1_reminders()
        await test_user_story_2_priorities()
        await test_user_story_3_search()
        await test_user_story_4_filtering_sorting()
        await test_user_story_5_tags()
        await test_user_story_6_recurring()
        await test_user_story_7_realtime_sync()

        print("\n=== Test Summary ===")
        print("✅ All automated tests completed")
        print("⚠️  Manual validation required for:")
        print("   - Reminder delivery (wait for scheduled time)")
        print("   - Recurring task generation (wait 10+ seconds)")
        print("   - Real-time sync (open multiple browser tabs)")
        print()
        print("Next steps:")
        print("1. Run performance tests: ./scripts/test-performance.sh")
        print("2. Run idempotency tests: python scripts/test-idempotency.py")
        print("3. Run security tests: python scripts/test-security.py")

    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
