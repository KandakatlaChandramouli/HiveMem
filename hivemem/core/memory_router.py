from hivemem.core.episodic_memory import EpisodicMemory
from hivemem.core.semantic_memory import SemanticMemory
from hivemem.core.working_memory import WorkingMemory
from hivemem.models import Memory, MemoryQuery, MemoryResult, MemoryType


class MemoryRouter:
    def __init__(
        self,
        working_memory: WorkingMemory,
        episodic_memory: EpisodicMemory,
        semantic_memory: SemanticMemory,
    ):
        self.working_memory = working_memory
        self.episodic_memory = episodic_memory
        self.semantic_memory = semantic_memory

    def add(self, memory: Memory) -> Memory:
        if memory.memory_type == MemoryType.WORKING:
            return self.working_memory.add(memory)

        if memory.memory_type == MemoryType.EPISODIC:
            return self.episodic_memory.add(memory)

        return self.semantic_memory.add(memory)

    def recall(self, request: MemoryQuery) -> list[MemoryResult]:
        memories: list[Memory] = []

        allowed_types = request.memory_types

        if not allowed_types or MemoryType.WORKING in allowed_types:
            memories.extend(self.working_memory.get_recent(request.limit))

        if not allowed_types or MemoryType.EPISODIC in allowed_types:
            memories.extend(self.episodic_memory.search(request.query, request.limit))

        if not allowed_types or MemoryType.SEMANTIC in allowed_types:
            memories.extend(self.semantic_memory.search(request.query, request.limit))

        query_words = set(request.query.lower().split())
        results = []

        seen_ids: set[str] = set()

        for memory in memories:
            if memory.id in seen_ids:
                continue

            content_words = set(memory.content.lower().split())
            overlap = len(query_words & content_words)
            score = overlap / max(len(query_words), 1)

            if score > 0:
                results.append(
                    MemoryResult(
                        memory=memory,
                        score=min(score, 1.0),
                        source=memory.memory_type.value,
                    )
                )
                seen_ids.add(memory.id)

        results.sort(key=lambda result: result.score, reverse=True)
        return results[: request.limit]
