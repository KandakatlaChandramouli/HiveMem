from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from hivemem.models import Memory, MemoryStatus, MemoryType


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z0-9']+", text.lower())
        if len(token) > 1
    }


class SemanticMemory:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = str(db_path) if db_path is not None else ":memory:"
        self._connection = sqlite3.connect(self.db_path)
        self._connection.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self) -> None:
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS semantic_memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                status TEXT NOT NULL,
                importance REAL NOT NULL,
                confidence REAL NOT NULL,
                tags TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_accessed_at TEXT
            )
            """
        )
        self._connection.commit()

    def _row_to_memory(self, row: sqlite3.Row) -> Memory:
        return Memory(
            id=row["id"],
            content=row["content"],
            memory_type=MemoryType(row["memory_type"]),
            status=MemoryStatus(row["status"]),
            importance=row["importance"],
            confidence=row["confidence"],
            tags=json.loads(row["tags"]),
            metadata=json.loads(row["metadata"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            last_accessed_at=(
                datetime.fromisoformat(row["last_accessed_at"])
                if row["last_accessed_at"]
                else None
            ),
        )

    def add(self, memory: Memory) -> Memory:
        now = _utc_now()
        memory.updated_at = now

        self._connection.execute(
            """
            INSERT INTO semantic_memories (
                id, content, memory_type, status, importance, confidence,
                tags, metadata, created_at, updated_at, last_accessed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                content = excluded.content,
                memory_type = excluded.memory_type,
                status = excluded.status,
                importance = excluded.importance,
                confidence = excluded.confidence,
                tags = excluded.tags,
                metadata = excluded.metadata,
                updated_at = excluded.updated_at,
                last_accessed_at = excluded.last_accessed_at
            """,
            (
                memory.id,
                memory.content,
                memory.memory_type.value,
                memory.status.value,
                memory.importance,
                memory.confidence,
                json.dumps(memory.tags),
                json.dumps(memory.metadata),
                memory.created_at.isoformat(),
                memory.updated_at.isoformat(),
                memory.last_accessed_at.isoformat()
                if memory.last_accessed_at
                else None,
            ),
        )
        self._connection.commit()
        return memory

    def all(self) -> list[Memory]:
        rows = self._connection.execute(
            """
            SELECT *
            FROM semantic_memories
            WHERE status = ?
            ORDER BY importance DESC, updated_at DESC
            """,
            (MemoryStatus.ACTIVE.value,),
        ).fetchall()
        return [self._row_to_memory(row) for row in rows]

    def get(self, memory_id: str) -> Memory | None:
        row = self._connection.execute(
            """
            SELECT *
            FROM semantic_memories
            WHERE id = ?
            """,
            (memory_id,),
        ).fetchone()
        return self._row_to_memory(row) if row else None

    def search(self, query: str, limit: int = 10) -> list[Memory]:
        query_tokens = _tokens(query)
        if not query_tokens:
            return []

        scored: list[tuple[float, Memory]] = []

        for memory in self.all():
            content_tokens = _tokens(memory.content)
            tag_tokens = _tokens(" ".join(memory.tags))
            metadata_tokens = _tokens(json.dumps(memory.metadata))

            overlap = len(query_tokens & content_tokens)
            tag_overlap = len(query_tokens & tag_tokens)
            metadata_overlap = len(query_tokens & metadata_tokens)

            score = (
                overlap * 1.0
                + tag_overlap * 0.5
                + metadata_overlap * 0.25
                + memory.confidence * 0.1
                + memory.importance * 0.1
            )

            if score > 0:
                memory.last_accessed_at = _utc_now()
                self.add(memory)
                scored.append((score, memory))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [memory for _, memory in scored[:limit]]

    def count(self) -> int:
        row = self._connection.execute(
            """
            SELECT COUNT(*)
            FROM semantic_memories
            WHERE status = ?
            """,
            (MemoryStatus.ACTIVE.value,),
        ).fetchone()
        return int(row[0])

    def close(self) -> None:
        self._connection.close()
