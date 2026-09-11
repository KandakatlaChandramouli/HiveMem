from hivemem.models import Memory, MemoryType


def test_memory_defaults():
    memory = Memory(
        id="test-1",
        content="HiveMem is a memory engine.",
        memory_type=MemoryType.EPISODIC,
    )

    assert memory.importance == 0.5
    assert memory.confidence == 0.5
    assert memory.access_count == 0


def test_memory_touch():
    memory = Memory(
        id="test-2",
        content="Important event.",
        memory_type=MemoryType.EPISODIC,
    )

    memory.touch()

    assert memory.access_count == 1
