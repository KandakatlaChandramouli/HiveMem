from pathlib import Path

from hivemem.engine import HiveMemory
from hivemem.models import MemoryType
from hivemem.semantic_memory import SemanticMemory


def test_semantic_memory_persists(tmp_path: Path):
    db_path = tmp_path / "semantic.db"

    first = SemanticMemory(db_path)
    memory = first.add(
        __import__("hivemem.models", fromlist=["Memory"]).Memory(
            content="Python is useful for automation",
            memory_type=MemoryType.SEMANTIC,
            importance=0.9,
            confidence=0.95,
        )
    )
    first.close()

    second = SemanticMemory(db_path)
    assert second.get(memory.id) is not None
    assert second.count() == 1
    assert second.search("automation")[0].content == "Python is useful for automation"
    second.close()


def test_engine_persists_semantic_memory(tmp_path: Path):
    db_path = tmp_path / "engine.db"

    first = HiveMemory(db_path)
    first.remember(
        "CBSE English teaching experience",
        memory_type=MemoryType.SEMANTIC,
        importance=0.9,
    )
    first.close()

    second = HiveMemory(db_path)
    assert second.stats()["semantic"] == 1
    assert second.recall("English teaching")
    second.close()
