from datetime import datetime, timezone
from math import exp

from hivemem.models import Memory


def calculate_retention_score(
    memory: Memory,
    now: datetime | None = None,
) -> float:
    now = now or datetime.now(timezone.utc)

    age_days = max(
        (now - memory.last_accessed_at).total_seconds() / 86400,
        0.0,
    )

    recency = exp(-age_days / 30)
    access_frequency = min(memory.access_count / 10, 1.0)

    score = (
        0.40 * memory.importance
        + 0.25 * memory.confidence
        + 0.20 * recency
        + 0.15 * access_frequency
    )

    return round(min(max(score, 0.0), 1.0), 4)


def should_archive(memory: Memory, threshold: float = 0.35) -> bool:
    return calculate_retention_score(memory) < threshold
