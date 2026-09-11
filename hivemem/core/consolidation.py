from hivemem.models import Memory, MemoryType


class MemoryConsolidator:
    def consolidate(
        self,
        episodic_memories: list[Memory],
        semantic_memories: list[Memory],
    ) -> list[Memory]:
        existing = {
            memory.content.lower(): memory
            for memory in semantic_memories
        }

        new_semantic_memories: list[Memory] = []

        for episode in episodic_memories:
            key = episode.content.lower().strip()

            if key in existing:
                existing_memory = existing[key]
                existing_memory.confidence = min(
                    1.0,
                    existing_memory.confidence + 0.05,
                )
                existing_memory.metadata["evidence_count"] = (
                    existing_memory.metadata.get("evidence_count", 1) + 1
                )
                continue

            semantic_memory = Memory(
                id=f"semantic-{episode.id}",
                content=episode.content,
                memory_type=MemoryType.SEMANTIC,
                importance=episode.importance,
                confidence=episode.confidence,
                source_session=episode.source_session,
                tags=episode.tags.copy(),
                metadata={
                    "evidence_count": 1,
                    "source_memory_ids": [episode.id],
                },
            )

            new_semantic_memories.append(semantic_memory)
            existing[key] = semantic_memory

        return new_semantic_memories
