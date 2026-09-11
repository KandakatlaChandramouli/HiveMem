import sqlite3
from datetime import datetime

from hivemem.models import Memory, MemoryStatus, MemoryType


class EpisodicMemory:
    def __init__(self, database_path: str = "hivemem.db"):
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS episodic_memories (
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
        self.connection.commit()

    def add(self, memory: Memory) -> Memory:
        if memory.memory_type != MemoryType.EPISODIC:
            memory.memory_type = MemoryType.EPISODIC

        self.connection.execute(
            """
            INSERT OR REPLACE INTO episodic_memories (
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
                ",".join(memory.tags),
                memory.status.value,
                "{}",
            ),
        )
        self.connection.commit()
        return memory

    def get(self, memory_id: str) -> Memory | None:
        row = self.connection.execute(
            "SELECT * FROM episodic_memories WHERE id = ?",
            (memory_id,),
        ).fetchone()

        if row is None:
            return None

        return self._row_to_memory(row)

    def all(self) -> list[Memory]:
        rows = self.connection.execute(
            "SELECT * FROM episodic_memories ORDER BY created_at ASC"
        ).fetchall()

        return [self._row_to_memory(row) for row in rows]

    def search(self, text: str, limit: int = 10) -> list[Memory]:
        rows = self.connection.execute(
            """
            SELECT * FROM episodic_memories
            WHERE content LIKE ?
            AND status = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (f"%{text}%", MemoryStatus.ACTIVE.value, limit),
        ).fetchall()

        return [self._row_to_memory(row) for row in rows]

    def close(self) -> None:
        self.connection.close()

    @staticmethod
    def _row_to_memory(row: sqlite3.Row) -> Memory:
        return Memory(
            id=row["id"],
            content=row["content"],
            memory_type=MemoryType(row["memory_type"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            last_accessed_at=datetime.fromisoformat(row["last_accessed_at"]),
            importance=row["importance"],
            confidence=row["confidence"],
            access_count=row["access_count"],
            source_session=row["source_session"],
            tags=row["tags"].split(",") if row["tags"] else [],
            status=MemoryStatus(row["status"]),
        )
