from __future__ import annotations

from datetime import datetime, timezone

from hivemem.core.forgetting import calculate_retention_score
from hivemem.models import Memory, MemoryStatus


class MemoryLifecycle:
    def __init__(self, archive_threshold: float = 0.35):
        self.archive_threshold = archive_threshold

    def archive_candidates(
        self,
        memories: list[Memory],
        now: datetime | None = None,
    ) -> list[Memory]:
        now = now or datetime.now(timezone.utc)

        return [
            memory
            for memory in memories
            if calculate_retention_score(memory, now) < self.archive_threshold
        ]

    def archive(
        self,
        memories: list[Memory],
        now: datetime | None = None,
    ) -> list[Memory]:
        candidates = self.archive_candidates(memories, now)

        for memory in candidates:
            memory.status = MemoryStatus.ARCHIVED

        return candidates

    def delete_archived(
        self,
        memories: list[Memory],
    ) -> list[Memory]:
        deleted = []

        for memory in memories:
            if memory.status == MemoryStatus.ARCHIVED:
                memory.status = MemoryStatus.DELETED
                deleted.append(memory)

        return deleted
