from hivemem.core import EpisodicMemory, MemoryRouter, SemanticMemory, WorkingMemory
from hivemem.models import Memory, MemoryQuery, MemoryType


def test_router_retrieves_relevant_memory(tmp_path):
    router = MemoryRouter(
        working_memory=WorkingMemory(),
        episodic_memory=EpisodicMemory(str(tmp_path / "memory.db")),
        semantic_memory=SemanticMemory(),
    )

    router.add(
        Memory(
            id="episode-1",
            content="The user prefers Python.",
            memory_type=MemoryType.EPISODIC,
        )
    )

    results = router.recall(MemoryQuery(query="Python"))

    assert len(results) == 1
    assert results[0].memory.id == "episode-1"
