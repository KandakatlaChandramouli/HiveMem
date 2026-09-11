from collections import deque

from hivemem.models import Memory, MemoryType


class WorkingMemory:
    def __init__(self, capacity: int = 20):
        if capacity < 1:
            raise ValueError("capacity must be greater than zero")

        self.capacity = capacity
        self._items: deque[Memory] = deque(maxlen=capacity)

    def add(self, memory: Memory) -> Memory:
        memory.memory_type = MemoryType.WORKING
        self._items.append(memory)
        return memory

    def get_recent(self, limit: int = 10) -> list[Memory]:
        return list(self._items)[-limit:]

    def all(self) -> list[Memory]:
        return list(self._items)

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)
