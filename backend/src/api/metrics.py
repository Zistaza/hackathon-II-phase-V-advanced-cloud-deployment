"""
Prometheus metrics collection for Phase-V Advanced Features
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import APIRouter
from fastapi.responses import Response
import time

router = APIRouter()

# Task operation metrics
task_operations_total = Counter(
    'task_operations_total',
    'Total number of task operations',
    ['operation', 'status']
)

task_operation_duration = Histogram(
    'task_operation_duration_seconds',
    'Duration of task operations',
    ['operation'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

# Search and query metrics
search_query_duration = Histogram(
    'search_query_duration_seconds',
    'Duration of search queries',
    buckets=[0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
)

filter_query_duration = Histogram(
    'filter_query_duration_seconds',
    'Duration of filter queries',
    buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
)

sort_query_duration = Histogram(
    'sort_query_duration_seconds',
    'Duration of sort queries',
    buckets=[0.05, 0.1, 0.2, 0.5, 1.0]
)

# Event processing metrics
events_published_total = Counter(
    'events_published_total',
    'Total number of events published',
    ['event_type', 'topic']
)

events_consumed_total = Counter(
    'events_consumed_total',
    'Total number of events consumed',
    ['event_type', 'consumer']
)

event_processing_duration = Histogram(
    'event_processing_duration_seconds',
    'Duration of event processing',
    ['event_type', 'consumer'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

event_processing_errors = Counter(
    'event_processing_errors_total',
    'Total number of event processing errors',
    ['event_type', 'consumer', 'error_type']
)

# Reminder metrics
reminders_scheduled_total = Counter(
    'reminders_scheduled_total',
    'Total number of reminders scheduled',
    ['status']
)

reminders_triggered_total = Counter(
    'reminders_triggered_total',
    'Total number of reminders triggered',
    ['status']
)

reminder_delivery_duration = Histogram(
    'reminder_delivery_duration_seconds',
    'Duration from scheduled time to delivery',
    buckets=[1, 5, 10, 30, 60, 120, 300]
)

reminder_scheduling_errors = Counter(
    'reminder_scheduling_errors_total',
    'Total number of reminder scheduling errors',
    ['error_type']
)

# Recurring task metrics
recurring_tasks_generated_total = Counter(
    'recurring_tasks_generated_total',
    'Total number of recurring task instances generated',
    ['pattern', 'status']
)

recurring_task_generation_duration = Histogram(
    'recurring_task_generation_duration_seconds',
    'Duration of recurring task generation',
    ['pattern'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Multi-client sync metrics
websocket_connections_active = Gauge(
    'websocket_connections_active',
    'Number of active WebSocket connections'
)

task_sync_latency = Histogram(
    'task_sync_latency_seconds',
    'Latency from state change to client update',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Consumer lag metrics
consumer_lag_messages = Gauge(
    'consumer_lag_messages',
    'Number of messages in consumer lag',
    ['consumer', 'topic']
)

# Dead letter queue metrics
dlq_messages_total = Counter(
    'dlq_messages_total',
    'Total number of messages sent to DLQ',
    ['topic', 'reason']
)


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint

    Returns:
        Response: Prometheus metrics in text format
    """
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )


# Utility functions for recording metrics

def record_task_operation(operation: str, status: str, duration: float):
    """Record a task operation metric"""
    task_operations_total.labels(operation=operation, status=status).inc()
    task_operation_duration.labels(operation=operation).observe(duration)


def record_search_query(duration: float):
    """Record a search query metric"""
    search_query_duration.observe(duration)


def record_filter_query(duration: float):
    """Record a filter query metric"""
    filter_query_duration.observe(duration)


def record_sort_query(duration: float):
    """Record a sort query metric"""
    sort_query_duration.observe(duration)


def record_event_published(event_type: str, topic: str):
    """Record an event publication metric"""
    events_published_total.labels(event_type=event_type, topic=topic).inc()


def record_event_consumed(event_type: str, consumer: str, duration: float):
    """Record an event consumption metric"""
    events_consumed_total.labels(event_type=event_type, consumer=consumer).inc()
    event_processing_duration.labels(event_type=event_type, consumer=consumer).observe(duration)


def record_event_error(event_type: str, consumer: str, error_type: str):
    """Record an event processing error"""
    event_processing_errors.labels(
        event_type=event_type,
        consumer=consumer,
        error_type=error_type
    ).inc()


def record_reminder_scheduled(status: str):
    """Record a reminder scheduling metric"""
    reminders_scheduled_total.labels(status=status).inc()


def record_reminder_triggered(status: str, delivery_duration: float):
    """Record a reminder trigger metric"""
    reminders_triggered_total.labels(status=status).inc()
    reminder_delivery_duration.observe(delivery_duration)


def record_reminder_error(error_type: str):
    """Record a reminder scheduling error"""
    reminder_scheduling_errors.labels(error_type=error_type).inc()


def record_recurring_task_generated(pattern: str, status: str, duration: float):
    """Record a recurring task generation metric"""
    recurring_tasks_generated_total.labels(pattern=pattern, status=status).inc()
    recurring_task_generation_duration.labels(pattern=pattern).observe(duration)


def set_websocket_connections(count: int):
    """Set the number of active WebSocket connections"""
    websocket_connections_active.set(count)


def record_task_sync_latency(latency: float):
    """Record task sync latency"""
    task_sync_latency.observe(latency)


def set_consumer_lag(consumer: str, topic: str, lag: int):
    """Set consumer lag for a topic"""
    consumer_lag_messages.labels(consumer=consumer, topic=topic).set(lag)


def record_dlq_message(topic: str, reason: str):
    """Record a message sent to DLQ"""
    dlq_messages_total.labels(topic=topic, reason=reason).inc()
