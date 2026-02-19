-- Performance Testing SQL Queries
-- Tasks: T055, T064, T073, T113
-- Run with: psql $DATABASE_URL -f scripts/test-performance.sql

\timing on

\echo '=== Phase-V Performance Testing ==='
\echo ''

-- T055: Search query performance (<500ms target)
\echo '=== T055: Full-Text Search Performance Test ==='
\echo 'Target: <500ms for 10,000 tasks'
\echo ''

EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE user_id = 'test-user'
  AND search_vector @@ plainto_tsquery('english', 'project')
ORDER BY ts_rank(search_vector, plainto_tsquery('english', 'project')) DESC
LIMIT 50;

\echo ''
\echo '--- Search with multiple keywords ---'
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE user_id = 'test-user'
  AND search_vector @@ plainto_tsquery('english', 'project implementation')
LIMIT 50;

\echo ''
\echo ''

-- T064: Combined filter + sort performance (<1s target)
\echo '=== T064: Combined Filter + Sort Performance Test ==='
\echo 'Target: <1s for 10,000 tasks'
\echo ''

EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE user_id = 'test-user'
  AND status = 'incomplete'
  AND priority = 'high'
  AND tags @> '["work"]'::jsonb
  AND due_date BETWEEN NOW() AND NOW() + INTERVAL '7 days'
ORDER BY due_date ASC
LIMIT 50;

\echo ''
\echo '--- Complex multi-criteria query ---'
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE user_id = 'test-user'
  AND status = 'incomplete'
  AND priority IN ('high', 'urgent')
  AND tags @> '["urgent"]'::jsonb
ORDER BY priority DESC, due_date ASC
LIMIT 50;

\echo ''
\echo ''

-- T073: Tag filter performance (<200ms target)
\echo '=== T073: Tag Filter Performance Test ==='
\echo 'Target: <200ms for 10,000 tasks'
\echo ''

EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE user_id = 'test-user'
  AND tags @> '["work"]'::jsonb
ORDER BY created_at DESC
LIMIT 50;

\echo ''
\echo '--- Multiple tag filter (AND logic) ---'
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE user_id = 'test-user'
  AND tags @> '["work", "urgent"]'::jsonb
ORDER BY created_at DESC
LIMIT 50;

\echo ''
\echo '--- Tag containment with priority filter ---'
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE user_id = 'test-user'
  AND tags @> '["project"]'::jsonb
  AND priority = 'high'
ORDER BY created_at DESC
LIMIT 50;

\echo ''
\echo ''

-- Additional performance tests
\echo '=== Additional Performance Tests ==='
\echo ''

\echo '--- Priority filter performance ---'
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE user_id = 'test-user'
  AND priority = 'urgent'
ORDER BY created_at DESC
LIMIT 50;

\echo ''
\echo '--- Due date range filter ---'
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE user_id = 'test-user'
  AND due_date BETWEEN NOW() AND NOW() + INTERVAL '30 days'
ORDER BY due_date ASC
LIMIT 50;

\echo ''
\echo '--- Status + priority composite index test ---'
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE user_id = 'test-user'
  AND status = 'incomplete'
  AND priority = 'high'
ORDER BY created_at DESC
LIMIT 50;

\echo ''
\echo ''

-- Index usage verification
\echo '=== Index Usage Verification ==='
\echo ''

SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE tablename = 'tasks'
ORDER BY idx_scan DESC;

\echo ''
\echo ''

-- Performance summary
\echo '=== Performance Test Summary ==='
\echo ''
\echo 'Review the EXPLAIN ANALYZE output above:'
\echo '- T055: Search queries should complete in <500ms'
\echo '- T064: Combined filter+sort should complete in <1s'
\echo '- T073: Tag filters should complete in <200ms'
\echo ''
\echo 'Key metrics to check:'
\echo '- Execution Time: Should meet targets'
\echo '- Index Scans: Should use appropriate indexes'
\echo '- Rows Returned: Should be reasonable for LIMIT 50'
\echo ''
\echo 'If performance targets not met:'
\echo '1. Run VACUUM ANALYZE tasks;'
\echo '2. Check index usage in pg_stat_user_indexes'
\echo '3. Consider adding composite indexes for common query patterns'
\echo '4. Review query plans for sequential scans'
