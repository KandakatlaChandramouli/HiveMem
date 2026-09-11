from hivemem.core.consolidation import MemoryConsolidator
from hivemem.models import Memory, MemoryType


def test_consolidation_creates_semantic_memory():
    episode = Memory(
        id="episode-1",
        content="Python is useful for backend development.",
        memory_type=MemoryType.EPISODIC,
        confidence=0.8,
    )

    result = MemoryConsolidator().consolidate([episode], [])

    assert len(result) == 1
    assert result[0].memory_type == MemoryType.SEMANTIC
    assert result[0].metadata["source_episode_ids"] == ["episode-1"]


def test_consolidation_increases_confidence_for_duplicate():
    semantic = Memory(
        id="semantic-1",
        content="Python is useful for backend development.",
        memory_type=MemoryType.SEMANTIC,
        confidence=0.5,
    )

    episode = Memory(
        id="episode-2",
        content="Python is useful for backend development.",
        memory_type=MemoryType.EPISODIC,
    )

    result = MemoryConsolidator().consolidate([episode], [semantic])

    assert result == []
    assert semantic.confidence == 0.55
    assert semantic.metadata["evidence_count"] == 2
