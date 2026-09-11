from hivemem.engine import HiveMemory
from hivemem.models import MemoryType


def test_remember_and_recall(tmp_path):
    engine = HiveMemory(str(tmp_path / "memory.db"))

    engine.remember(
        "The user prefers Python for backend development.",
        memory_type=MemoryType.EPISODIC,
        importance=0.9,
    )

    results = engine.recall("Python backend")

    assert results
    assert "Python" in results[0].memory.content


def test_consolidation_creates_semantic_memory(tmp_path):
    engine = HiveMemory(str(tmp_path / "memory.db"))

    engine.remember(
        "HiveMem stores long-term memories.",
        memory_type=MemoryType.EPISODIC,
    )

    created = engine.consolidate()

    assert len(created) == 1
    assert created[0].memory_type == MemoryType.SEMANTIC
    assert len(engine.semantic_memory.all()) == 1


def test_stats(tmp_path):
    engine = HiveMemory(str(tmp_path / "memory.db"))

    engine.remember("Test memory.")

    stats = engine.stats()

    assert stats["episodic"] == 1
    assert stats["working"] == 0
