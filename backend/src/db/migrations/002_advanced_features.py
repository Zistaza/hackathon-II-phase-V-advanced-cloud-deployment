"""Add advanced features to tasks table

Revision ID: 002_advanced_features
Revises: 001_initial_schema
Create Date: 2026-02-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR

# revision identifiers, used by Alembic.
revision = '002_advanced_features'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns
    op.add_column('tasks', sa.Column('priority', sa.String(10), nullable=False, server_default='medium'))
    op.add_column('tasks', sa.Column('tags', JSONB, nullable=False, server_default='[]'))
    op.add_column('tasks', sa.Column('due_date', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_pattern', sa.String(20), nullable=False, server_default='none'))
    op.add_column('tasks', sa.Column('reminder_time', sa.String(50), nullable=True))
    op.add_column('tasks', sa.Column('search_vector', TSVECTOR, nullable=True))

    # Create indexes
    op.create_index('idx_tasks_priority', 'tasks', ['user_id', 'priority'])
    op.create_index('idx_tasks_tags', 'tasks', ['tags'], postgresql_using='gin')
    op.create_index('idx_tasks_search', 'tasks', ['search_vector'], postgresql_using='gin')
    op.create_index('idx_tasks_due_date', 'tasks', ['user_id', 'due_date'])
    op.create_index('idx_tasks_status_priority', 'tasks', ['user_id', 'status', 'priority'])

    # Create trigger for search_vector
    op.execute("""
        CREATE TRIGGER tasks_search_vector_update BEFORE INSERT OR UPDATE
        ON tasks FOR EACH ROW EXECUTE FUNCTION
        tsvector_update_trigger(search_vector, 'pg_catalog.english', title, description);
    """)

    # Update existing rows to populate search_vector
    op.execute("""
        UPDATE tasks
        SET search_vector = to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(description, ''))
        WHERE search_vector IS NULL;
    """)


def downgrade():
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS tasks_search_vector_update ON tasks")

    # Drop indexes
    op.drop_index('idx_tasks_status_priority', 'tasks')
    op.drop_index('idx_tasks_due_date', 'tasks')
    op.drop_index('idx_tasks_search', 'tasks')
    op.drop_index('idx_tasks_tags', 'tasks')
    op.drop_index('idx_tasks_priority', 'tasks')

    # Drop columns
    op.drop_column('tasks', 'search_vector')
    op.drop_column('tasks', 'reminder_time')
    op.drop_column('tasks', 'recurrence_pattern')
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'tags')
    op.drop_column('tasks', 'priority')
