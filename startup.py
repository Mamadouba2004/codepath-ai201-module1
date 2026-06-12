"""Cold-start guard: build chroma_db/ from chunks.json if it doesn't exist."""
from pathlib import Path


def build_if_needed():
    db_dir = Path("chroma_db")
    if not db_dir.exists() or not any(db_dir.iterdir()):
        import embed
        embed.main()
