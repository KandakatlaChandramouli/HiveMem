from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from hivemem.models import Memory, MemoryStatus


class EpisodicMemory:
    def __init__(self, db_path: str = "hivemem.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self):
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed_at TEXT NOT NULL,
                    importance REAL NOT NULL,
                    confidence REAL NOT NULL,
                    access_count INTEGER NOT NULL,
                    source_session TEXT,
                    tags TEXT NOT NULL,
                    status TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )
                """
            )

    def add(self, memory: Memory) -> Memory:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO memories (
                    id, content, memory_type, created_at, last_accessed_at,
                    importance, confidence, access_count, source_session,
                    tags, status, metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    memory.id,
                    memory.content,
                    memory.memory_type.value,
                    memory.created_at.isoformat(),
                    memory.last_accessed_at.isoformat(),
                    memory.importance,
                    memory.confidence,
                    memory.access_count,
                    memory.source_session,
                    json.dumps(memory.tags),
                    memory.status.value,
                    json.dumps(memory.metadata),
                ),
            )
        return memory

    def all(self) -> list[Memory]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM memories
                WHERE status = ?
                ORDER BY created_at ASC
                """,
                (MemoryStatus.ACTIVE.value,),
            ).fetchall()

        return [self._row_to_memory(row) for row in rows]

    def search(self, query: str, limit: int = 5) -> list[Memory]:
        words = [word.lower() for word in query.split() if word.strip()]
        memories = self.all()

        scored = []
        for memory in memories:
            content = memory.content.lower()
            score = sum(word in content for word in words)
            if score > 0:
                scored.append((score, memory))

        scored.sort(key=lambda item: item[0], reverse=True)
        results = []

        for _, memory in scored[:limit]:
            memory.touch()
            self.add(memory)
            results.append(memory)

        return results

    def count(self) -> int:
        with self._connect() as connection:
            return connection.execute(
                "SELECT COUNT(*) FROM memories WHERE status = ?",
                (MemoryStatus.ACTIVE.value,),
            ).fetchone()[0]

    def _row_to_memory(self, row: sqlite3.Row) -> Memory:
        return Memory(
            id=row["id"],
            content=row["content"],
            memory_type=row["memory_type"],
            created_at=row["created_at"],
            last_accessed_at=row["last_accessed_at"],
            importance=row["importance"],
            confidence=row["confidence"],
            access_count=row["access_count"],
            source_session=row["source_session"],
            tags=json.loads(row["tags"] or "[]"),
            status=row["status"],
            metadata=json.loads(row["metadata"] or "{}"),
        )
