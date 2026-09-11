from __future__ import annotations

from uuid import uuid4

from hivemem.models import Memory, MemoryType


class MemoryConsolidator:
    def consolidate(
        self,
        episodic_memories: list[Memory],
        semantic_memories: list[Memory],
    ) -> list[Memory]:
        existing = {
            memory.content.lower().strip(): memory
            for memory in semantic_memories
        }

        new_semantic_memories: list[Memory] = []

        for episode in episodic_memories:
            key = episode.content.lower().strip()

            if key in existing:
                semantic = existing[key]
                semantic.confidence = min(
                    1.0,
                    semantic.confidence + 0.05,
                )
                semantic.metadata["evidence_count"] = (
                    semantic.metadata.get("evidence_count", 1) + 1
                )
                semantic.metadata["source_episode_ids"] = list(
                    set(
                        semantic.metadata.get("source_episode_ids", [])
                        + [episode.id]
                    )
                )
                continue

            semantic = Memory(
                id=f"semantic-{uuid4()}",
                content=episode.content,
                memory_type=MemoryType.SEMANTIC,
                importance=episode.importance,
                confidence=min(1.0, episode.confidence + 0.1),
                source_session=episode.source_session,
                tags=list(episode.tags),
                metadata={
                    "evidence_count": 1,
                    "source_episode_ids": [episode.id],
                    "consolidated_from": "episodic",
                },
            )

            existing[key] = semantic
            new_semantic_memories.append(semantic)

        return new_semantic_memories
