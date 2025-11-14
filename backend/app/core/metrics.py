"""Metrics storage and retrieval using Redis and Prometheus."""

import logging
import json
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, asdict
import redis
from redis.exceptions import RedisError
from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)

# ===============================================================================
# PROMETHEUS METRICS FOR TELEMETRY
# ===============================================================================

telemetry_events_total = Counter(
    "telemetry_events_processed_total",
    "Total telemetry events processed",
    ["event_type", "status"],
)

telemetry_processing_time = Histogram(
    "telemetry_event_processing_seconds", "Time to process telemetry event"
)

telemetry_batch_size = Histogram(
    "telemetry_batch_size", "Number of events in telemetry batches"
)

telemetry_duplicates_total = Counter(
    "telemetry_duplicates_total", "Total duplicate telemetry events detected"
)


@dataclass
class InferenceMetrics:
    """Inference performance metrics."""

    student_id: str
    skill_type: Optional[str]
    inference_time_ms: float
    success: bool
    error_message: Optional[str]
    timestamp: str  # ISO format


class MetricsStore:
    """Redis-backed metrics storage with fallback to in-memory."""

    def __init__(self, redis_url: Optional[str] = None, max_memory_size: int = 1000):
        """
        Initialize metrics store.

        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379/0)
            max_memory_size: Maximum number of metrics to keep in memory fallback
        """
        self.redis_url = redis_url
        self.max_memory_size = max_memory_size
        self.redis_client: Optional[redis.Redis] = None
        self.memory_fallback: List[InferenceMetrics] = []
        self.use_redis = False

        # Try to connect to Redis
        if redis_url:
            try:
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_timeout=2,
                    socket_connect_timeout=2,
                )
                # Test connection
                self.redis_client.ping()
                self.use_redis = True
                logger.info("Connected to Redis for metrics storage")
            except (RedisError, Exception) as e:
                logger.warning(
                    f"Failed to connect to Redis: {e}. Using in-memory fallback."
                )
                self.redis_client = None
                self.use_redis = False
        else:
            logger.info("No Redis URL provided. Using in-memory metrics storage.")

    def record_metric(
        self,
        student_id: str,
        inference_time_ms: float,
        skill_type: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ):
        """
        Record an inference metric.

        Args:
            student_id: Student ID
            inference_time_ms: Time taken for inference in milliseconds
            skill_type: Optional skill type
            success: Whether inference succeeded
            error_message: Optional error message if failed
        """
        metrics = InferenceMetrics(
            student_id=student_id,
            skill_type=skill_type,
            inference_time_ms=inference_time_ms,
            success=success,
            error_message=error_message,
            timestamp=datetime.utcnow().isoformat(),
        )

        if self.use_redis and self.redis_client:
            try:
                self._record_to_redis(metrics)
            except (RedisError, Exception) as e:
                logger.error(
                    f"Failed to record metrics to Redis: {e}. Using memory fallback."
                )
                self._record_to_memory(metrics)
        else:
            self._record_to_memory(metrics)

    def _record_to_redis(self, metrics: InferenceMetrics):
        """Record metrics to Redis using a sorted set."""
        if not self.redis_client:
            return

        # Use sorted set with timestamp as score for time-based queries
        key = "inference_metrics"
        value = json.dumps(asdict(metrics))
        score = datetime.fromisoformat(metrics.timestamp).timestamp()

        self.redis_client.zadd(key, {value: score})

        # Keep only last 10,000 metrics (configurable)
        self.redis_client.zremrangebyrank(key, 0, -10001)

    def _record_to_memory(self, metrics: InferenceMetrics):
        """Record metrics to in-memory list."""
        self.memory_fallback.append(metrics)

        # Keep only last N metrics
        if len(self.memory_fallback) > self.max_memory_size:
            self.memory_fallback.pop(0)

    def get_recent_metrics(self, limit: int = 100) -> List[InferenceMetrics]:
        """
        Get recent metrics.

        Args:
            limit: Maximum number of metrics to return

        Returns:
            List of recent metrics, newest first
        """
        if self.use_redis and self.redis_client:
            try:
                return self._get_from_redis(limit)
            except (RedisError, Exception) as e:
                logger.error(
                    f"Failed to get metrics from Redis: {e}. Using memory fallback."
                )
                return self._get_from_memory(limit)
        else:
            return self._get_from_memory(limit)

    def _get_from_redis(self, limit: int) -> List[InferenceMetrics]:
        """Get metrics from Redis."""
        if not self.redis_client:
            return []

        key = "inference_metrics"
        # Get most recent entries (highest scores)
        results = self.redis_client.zrevrange(key, 0, limit - 1)

        metrics = []
        for result in results:
            try:
                data = json.loads(result)
                metrics.append(InferenceMetrics(**data))
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"Failed to parse metric: {e}")
                continue

        return metrics

    def _get_from_memory(self, limit: int) -> List[InferenceMetrics]:
        """Get metrics from memory."""
        return list(reversed(self.memory_fallback[-limit:]))

    def get_metrics_summary(self) -> dict:
        """
        Get aggregated metrics summary.

        Returns:
            Dictionary with summary statistics
        """
        metrics = self.get_recent_metrics(limit=10000)  # Last 10k for summary

        if not metrics:
            return {
                "total_inferences": 0,
                "successful_inferences": 0,
                "failed_inferences": 0,
                "avg_inference_time_ms": 0.0,
                "max_inference_time_ms": 0.0,
                "min_inference_time_ms": 0.0,
                "p95_inference_time_ms": 0.0,
                "success_rate": 0.0,
            }

        total = len(metrics)
        successful = sum(1 for m in metrics if m.success)
        failed = total - successful

        times = [m.inference_time_ms for m in metrics if m.success]
        if times:
            avg_time = sum(times) / len(times)
            max_time = max(times)
            min_time = min(times)

            # Calculate P95
            sorted_times = sorted(times)
            p95_index = int(len(sorted_times) * 0.95)
            p95_time = (
                sorted_times[p95_index] if p95_index < len(sorted_times) else max_time
            )
        else:
            avg_time = max_time = min_time = p95_time = 0.0

        return {
            "total_inferences": total,
            "successful_inferences": successful,
            "failed_inferences": failed,
            "avg_inference_time_ms": avg_time,
            "max_inference_time_ms": max_time,
            "min_inference_time_ms": min_time,
            "p95_inference_time_ms": p95_time,
            "success_rate": successful / total if total > 0 else 0.0,
        }

    def clear_metrics(self):
        """Clear all metrics (use with caution)."""
        if self.use_redis and self.redis_client:
            try:
                self.redis_client.delete("inference_metrics")
                logger.info("Cleared metrics from Redis")
            except (RedisError, Exception) as e:
                logger.error(f"Failed to clear Redis metrics: {e}")

        self.memory_fallback.clear()
        logger.info("Cleared in-memory metrics")


# Global metrics store instance
_metrics_store: Optional[MetricsStore] = None


def get_metrics_store(redis_url: Optional[str] = None) -> MetricsStore:
    """
    Get or create global metrics store.

    Args:
        redis_url: Redis connection URL

    Returns:
        MetricsStore instance
    """
    global _metrics_store

    if _metrics_store is None:
        _metrics_store = MetricsStore(redis_url=redis_url)

    return _metrics_store
