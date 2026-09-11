from hivemem.core.working_memory import WorkingMemory
from hivemem.models import Memory, MemoryType


def create_memory(number: int) -> Memory:
    return Memory(
        id=f"memory-{number}",
        content=f"Memory {number}",
        memory_type=MemoryType.WORKING,
    )


def test_working_memory_respects_capacity():
    memory = WorkingMemory(capacity=2)

    memory.add(create_memory(1))
    memory.add(create_memory(2))
    memory.add(create_memory(3))

    assert len(memory) == 2
    assert [item.id for item in memory.all()] == ["memory-2", "memory-3"]


def test_working_memory_clear():
    memory = WorkingMemory(capacity=2)

    memory.add(create_memory(1))
    memory.clear()

    assert len(memory) == 0
