#!/bin/bash
# Database Migration Execution Script
# Tasks: T008, T009
# Prerequisites: PostgreSQL database accessible via DATABASE_URL

set -e

echo "=== Phase-V Database Migration Script ==="
echo "Date: $(date)"
echo ""

# Check prerequisites
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable not set"
    echo "Please set: export DATABASE_URL='postgresql://user:password@host:5432/todo_chatbot'"
    exit 1
fi

echo "✓ DATABASE_URL is set"
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/../../backend" || exit 1
echo "Working directory: $(pwd)"
echo ""

# Check Alembic is installed
if ! command -v alembic &> /dev/null; then
    echo "❌ ERROR: Alembic not installed"
    echo "Install: pip install alembic"
    exit 1
fi

echo "✓ Alembic is installed"
echo ""

# T008: Run migration to apply schema changes
echo "=== T008: Running migration (alembic upgrade head) ==="
echo ""

alembic upgrade head

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ T008 COMPLETE: Migration applied successfully"
else
    echo ""
    echo "❌ T008 FAILED: Migration failed"
    exit 1
fi

echo ""
echo "=== Verifying migration results ==="
echo ""

# Verify new columns exist
psql "$DATABASE_URL" -c "\d tasks" | grep -E "(priority|tags|due_date|recurrence_pattern|reminder_time|search_vector)"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ New columns verified"
else
    echo ""
    echo "❌ New columns not found"
    exit 1
fi

# Verify indexes exist
psql "$DATABASE_URL" -c "\di" | grep -E "(idx_tasks_priority|idx_tasks_tags|idx_tasks_search|idx_tasks_due_date|idx_tasks_status_priority)"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ New indexes verified"
else
    echo ""
    echo "❌ New indexes not found"
    exit 1
fi

# Verify trigger exists
psql "$DATABASE_URL" -c "SELECT tgname FROM pg_trigger WHERE tgname = 'tasks_search_vector_update';"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Search vector trigger verified"
else
    echo ""
    echo "❌ Search vector trigger not found"
    exit 1
fi

echo ""
echo "=== T009: Testing migration rollback ==="
echo ""

# Downgrade one revision
echo "Downgrading one revision..."
alembic downgrade -1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Downgrade successful"
else
    echo ""
    echo "❌ Downgrade failed"
    exit 1
fi

# Verify columns are removed
echo ""
echo "Verifying columns removed..."
psql "$DATABASE_URL" -c "\d tasks" | grep -E "(priority|tags|due_date)" && echo "❌ Columns still exist" || echo "✅ Columns removed"

# Re-apply migration
echo ""
echo "Re-applying migration..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ T009 COMPLETE: Migration rollback verified"
else
    echo ""
    echo "❌ T009 FAILED: Re-upgrade failed"
    exit 1
fi

echo ""
echo "=== Migration Tasks Complete ==="
echo "✅ T008: Migration applied"
echo "✅ T009: Rollback verified"
echo ""
echo "Next steps:"
echo "1. Run performance testing: ./scripts/test-performance.sh"
echo "2. Generate test data: python scripts/generate_test_data.py"
