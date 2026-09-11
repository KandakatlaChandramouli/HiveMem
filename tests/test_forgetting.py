from hivemem.core.forgetting import calculate_retention_score, should_archive
from hivemem.models import Memory, MemoryType


def test_retention_score_is_bounded():
    memory = Memory(
        id="memory-1",
        content="Important information",
        memory_type=MemoryType.EPISODIC,
        importance=1.0,
        confidence=1.0,
    )

    score = calculate_retention_score(memory)

    assert 0.0 <= score <= 1.0


def test_low_importance_memory_can_be_archived():
    memory = Memory(
        id="memory-2",
        content="Temporary information",
        memory_type=MemoryType.EPISODIC,
        importance=0.0,
        confidence=0.0,
    )

    assert should_archive(memory)
