from hivemem.models import Memory, MemoryType


class SemanticMemory:
    def __init__(self):
        self._items: dict[str, Memory] = {}

    def add(self, memory: Memory) -> Memory:
        memory.memory_type = MemoryType.SEMANTIC
        self._items[memory.id] = memory
        return memory

    def get(self, memory_id: str) -> Memory | None:
        return self._items.get(memory_id)

    def all(self) -> list[Memory]:
        return list(self._items.values())

    def search(self, text: str, limit: int = 10) -> list[Memory]:
        text_lower = text.lower()
        matches = [
            memory
            for memory in self._items.values()
            if text_lower in memory.content.lower()
        ]
        return matches[:limit]

    def clear(self) -> None:
        self._items.clear()
