from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from hivemem.engine import HiveMemory
from hivemem.models import MemoryType

app = typer.Typer(help="HiveMem hierarchical memory engine.")
console = Console()


def get_engine(db: str) -> HiveMemory:
    return HiveMemory(db_path=db)


@app.command()
def remember(
    content: str,
    memory_type: str = typer.Option("episodic", "--type"),
    importance: float = typer.Option(0.5, min=0.0, max=1.0),
    confidence: float = typer.Option(0.5, min=0.0, max=1.0),
    db: str = typer.Option("hivemem.db", "--db"),
):
    engine = get_engine(db)
    memory = engine.remember(
        content=content,
        memory_type=MemoryType(memory_type),
        importance=importance,
        confidence=confidence,
    )
    console.print(f"[green]Stored:[/green] {memory.id}")


@app.command()
def recall(
    query: str,
    limit: int = typer.Option(5, "--limit", min=1, max=100),
    db: str = typer.Option("hivemem.db", "--db"),
):
    engine = get_engine(db)
    results = engine.recall(query, limit)

    table = Table(title=f"Recall: {query}")
    table.add_column("Score")
    table.add_column("Type")
    table.add_column("Content")

    for result in results:
        table.add_row(
            f"{result.score:.2f}",
            result.source,
            result.memory.content,
        )

    console.print(table)


@app.command()
def consolidate(
    db: str = typer.Option("hivemem.db", "--db"),
):
    engine = get_engine(db)
    memories = engine.consolidate()
    console.print(f"[green]Consolidated {len(memories)} memories.[/green]")


@app.command()
def stats(
    db: str = typer.Option("hivemem.db", "--db"),
):
    engine = get_engine(db)
    console.print(json.dumps(engine.stats(), indent=2))


@app.command()
def retention(
    db: str = typer.Option("hivemem.db", "--db"),
):
    engine = get_engine(db)
    console.print(json.dumps(engine.retention_report(), indent=2))


if __name__ == "__main__":
    app()
