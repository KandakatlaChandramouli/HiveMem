from __future__ import annotations

from pathlib import Path

from hivemem.consolidation import Consolidator
from hivemem.episodic_memory import EpisodicMemory
from hivemem.forgetting import ForgettingEngine
from hivemem.memory_router import MemoryRouter
from hivemem.models import Memory, MemoryQuery, MemoryResult, MemoryType
from hivemem.semantic_memory import SemanticMemory
from hivemem.working_memory import WorkingMemory


class HiveMemory:
    def __init__(self, db_path: str | Path = "hivemem.db"):
        self.working_memory = WorkingMemory()
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory(db_path)
        self.router = MemoryRouter(
            working_memory=self.working_memory,
            episodic_memory=self.episodic_memory,
            semantic_memory=self.semantic_memory,
        )
        self.consolidator = Consolidator(
            working_memory=self.working_memory,
            episodic_memory=self.episodic_memory,
            semantic_memory=self.semantic_memory,
        )
        self.forgetting = ForgettingEngine(
            working_memory=self.working_memory,
            episodic_memory=self.episodic_memory,
            semantic_memory=self.semantic_memory,
        )

    def remember(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.WORKING,
        importance: float = 0.5,
        confidence: float = 1.0,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> Memory:
        memory = Memory(
            content=content,
            memory_type=memory_type,
            importance=importance,
            confidence=confidence,
            tags=tags or [],
            metadata=metadata or {},
        )

        if memory_type == MemoryType.WORKING:
            return self.working_memory.add(memory)

        if memory_type == MemoryType.EPISODIC:
            return self.episodic_memory.add(memory)

        return self.semantic_memory.add(memory)

    def recall(self, query: str, limit: int = 10) -> list[MemoryResult]:
        return self.router.search(
            MemoryQuery(
                query=query,
                limit=limit,
            )
        )

    def consolidate(self) -> list[Memory]:
        memories = self.consolidator.consolidate()
        for memory in self.semantic_memory.all():
            self.semantic_memory.add(memory)
        return memories

    def forget(self, threshold: float = 0.2) -> int:
        return self.forgetting.run(threshold=threshold)

    def stats(self) -> dict[str, int]:
        return {
            "working": len(self.working_memory.all()),
            "episodic": len(self.episodic_memory.all()),
            "semantic": self.semantic_memory.count(),
        }

    def close(self) -> None:
        self.semantic_memory.close()
