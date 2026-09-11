from __future__ import annotations

from uuid import uuid4

from hivemem.core import (
    EpisodicMemory,
    MemoryConsolidator,
    MemoryRouter,
    SemanticMemory,
    WorkingMemory,
    calculate_retention_score,
)
from hivemem.models import Memory, MemoryQuery, MemoryResult, MemoryType


class HiveMemory:
    def __init__(
        self,
        db_path: str = "hivemem.db",
        working_capacity: int = 20,
    ):
        self.working_memory = WorkingMemory(capacity=working_capacity)
        self.episodic_memory = EpisodicMemory(db_path)
        self.semantic_memory = SemanticMemory()
        self.router = MemoryRouter(
            working_memory=self.working_memory,
            episodic_memory=self.episodic_memory,
            semantic_memory=self.semantic_memory,
        )
        self.consolidator = MemoryConsolidator()

    def remember(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.EPISODIC,
        importance: float = 0.5,
        confidence: float = 0.5,
        source_session: str | None = None,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> Memory:
        memory = Memory(
            id=str(uuid4()),
            content=content,
            memory_type=memory_type,
            importance=importance,
            confidence=confidence,
            source_session=source_session,
            tags=tags or [],
            metadata=metadata or {},
        )
        return self.router.add(memory)

    def recall(
        self,
        query: str,
        limit: int = 5,
        memory_types: list[MemoryType] | None = None,
    ) -> list[MemoryResult]:
        return self.router.recall(
            MemoryQuery(
                query=query,
                limit=limit,
                memory_types=memory_types,
            )
        )

    def consolidate(self) -> list[Memory]:
        new_memories = self.consolidator.consolidate(
            self.episodic_memory.all(),
            self.semantic_memory.all(),
        )

        for memory in new_memories:
            self.semantic_memory.add(memory)

        return new_memories

    def stats(self) -> dict:
        return {
            "working": len(self.working_memory),
            "episodic": self.episodic_memory.count(),
            "semantic": len(self.semantic_memory.all()),
        }

    def retention_report(self) -> list[dict]:
        memories = (
            self.episodic_memory.all()
            + self.semantic_memory.all()
        )

        return [
            {
                "id": memory.id,
                "content": memory.content,
                "type": memory.memory_type.value,
                "retention_score": calculate_retention_score(memory),
            }
            for memory in memories
        ]
