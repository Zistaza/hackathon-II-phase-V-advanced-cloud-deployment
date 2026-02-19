"""Add Phase V advanced features (tags, due_date, recurrence, reminders, search)

Revision ID: a854b7a35228
Revises: de25f85aaa58
Create Date: 2026-02-14 00:57:52.701512

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a854b7a35228'
down_revision: Union[str, Sequence[str], None] = 'de25f85aaa58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns for Phase V features
    op.add_column('tasks', sa.Column('tags', sa.dialects.postgresql.JSONB, nullable=False, server_default='[]'))
    op.add_column('tasks', sa.Column('due_date', sa.TIMESTAMP(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_pattern', sa.String(20), nullable=False, server_default='none'))
    op.add_column('tasks', sa.Column('reminder_time', sa.String(50), nullable=True))
    op.add_column('tasks', sa.Column('search_vector', sa.dialects.postgresql.TSVECTOR, nullable=True))

    # Create indexes for performance (only for columns that exist)
    op.create_index('idx_tasks_tags', 'tasks', ['tags'], postgresql_using='gin')
    op.create_index('idx_tasks_search', 'tasks', ['search_vector'], postgresql_using='gin')
    op.create_index('idx_tasks_due_date', 'tasks', ['user_id', 'due_date'])

    # Create trigger for automatic search_vector updates
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


def downgrade() -> None:
    """Downgrade schema."""
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS tasks_search_vector_update ON tasks")

    # Drop indexes
    op.execute("DROP INDEX IF EXISTS idx_tasks_due_date")
    op.execute("DROP INDEX IF EXISTS idx_tasks_search")
    op.execute("DROP INDEX IF EXISTS idx_tasks_tags")

    # Drop columns
    op.drop_column('tasks', 'search_vector')
    op.drop_column('tasks', 'reminder_time')
    op.drop_column('tasks', 'recurrence_pattern')
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'tags')
