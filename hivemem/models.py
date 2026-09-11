from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MemoryType(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class MemoryStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Memory(BaseModel):
    id: str
    content: str = Field(min_length=1)
    memory_type: MemoryType
    created_at: datetime = Field(default_factory=utc_now)
    last_accessed_at: datetime = Field(default_factory=utc_now)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    access_count: int = Field(default=0, ge=0)
    source_session: str | None = None
    tags: list[str] = Field(default_factory=list)
    status: MemoryStatus = MemoryStatus.ACTIVE
    metadata: dict[str, Any] = Field(default_factory=dict)

    def touch(self) -> None:
        self.last_accessed_at = utc_now()
        self.access_count += 1


class MemoryQuery(BaseModel):
    query: str = Field(min_length=1)
    memory_types: list[MemoryType] | None = None
    limit: int = Field(default=5, ge=1, le=100)


class MemoryResult(BaseModel):
    memory: Memory
    score: float = Field(ge=0.0, le=1.0)
    source: str
