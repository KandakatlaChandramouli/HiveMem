from __future__ import annotations

from hivemem.models import Memory, MemoryStatus


class SemanticMemory:
    def __init__(self):
        self._memories: dict[str, Memory] = {}

    def add(self, memory: Memory) -> Memory:
        self._memories[memory.id] = memory
        return memory

    def all(self) -> list[Memory]:
        return [
            memory
            for memory in self._memories.values()
            if memory.status == MemoryStatus.ACTIVE
        ]

    def search(self, query: str, limit: int = 5) -> list[Memory]:
        words = {
            word.strip(".,!?;:\"'()[]{}").lower()
            for word in query.split()
            if word.strip(".,!?;:\"'()[]{}")
        }

        scored = []

        for memory in self.all():
            content_words = {
                word.strip(".,!?;:\"'()[]{}").lower()
                for word in memory.content.split()
                if word.strip(".,!?;:\"'()[]{}")
            }

            score = len(words & content_words)

            if score > 0:
                scored.append((score, memory))

        scored.sort(key=lambda item: item[0], reverse=True)

        return [memory for _, memory in scored[:limit]]

    def get(self, memory_id: str) -> Memory | None:
        return self._memories.get(memory_id)

    def count(self) -> int:
        return len(self.all())
