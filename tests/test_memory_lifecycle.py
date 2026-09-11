from hivemem.core.memory_lifecycle import MemoryLifecycle
from hivemem.models import Memory, MemoryStatus, MemoryType


def test_archive_low_retention_memory():
    memory = Memory(
        id="temporary",
        content="Temporary memory",
        memory_type=MemoryType.EPISODIC,
        importance=0.0,
        confidence=0.0,
    )

    lifecycle = MemoryLifecycle()
    archived = lifecycle.archive([memory])

    assert archived == [memory]
    assert memory.status == MemoryStatus.ARCHIVED


def test_delete_archived_memory():
    memory = Memory(
        id="archived",
        content="Old memory",
        memory_type=MemoryType.EPISODIC,
        status=MemoryStatus.ARCHIVED,
    )

    deleted = MemoryLifecycle().delete_archived([memory])

    assert deleted == [memory]
    assert memory.status == MemoryStatus.DELETED
