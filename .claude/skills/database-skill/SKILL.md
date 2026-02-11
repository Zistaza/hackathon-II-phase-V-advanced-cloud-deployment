---
name: database-skill
description: Design and manage database schemas, tables, and migrations for Neon Serverless PostgreSQL.
---

# Database Skill

## Instructions

1. **Schema design**
   - Define normalized database schemas
   - Design tables with clear relationships
   - Use appropriate data types and constraints
   - Ensure schemas support multi-user applications

2. **Table creation**
   - Create tables using SQLModel or SQLAlchemy
   - Define primary keys, foreign keys, and indexes
   - Ensure referential integrity between tables
   - Support extensibility for future features

3. **Migrations**
   - Generate and manage database migrations
   - Apply schema changes safely without data loss
   - Maintain versioned migration history
   - Support rollback strategies when possible

4. **Neon PostgreSQL integration**
   - Configure connections for Neon Serverless PostgreSQL
   - Ensure secure connection handling
   - Optimize schema for serverless usage patterns

5. **Reusability**
   - Expose reusable functions for schema and migration tasks
   - Ensure compatibility with Database Agent and Backend Agent

## Best Practices
- Use clear and consistent naming conventions
- Avoid storing sensitive data in plain text
- Index frequently queried columns
- Keep migrations small and incremental
- Design schemas with future scaling in mind

## Example Structure
```python
class DatabaseSkill:
    def create_tables(self):
        # Define SQLModel or SQLAlchemy models
        pass

    def generate_migration(self):
        # Create migration scripts
        pass

    def apply_migrations(self):
        # Apply pending migrations safely
        pass

    def define_schema(self):
        # Central place for schema definitions
        pass