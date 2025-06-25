"""Seed initial game content (animals and sentences) into Firestore.

If the collections already contain items, does nothing so the seeding is idempotent.
Run manually:   python -m backend.scripts.seed_games
Or called from FastAPI startup event:   await seed_if_empty()
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any

from google.cloud.firestore_v1.async_client import AsyncClient

# We reuse the internal helper that respects emulator credentials
from shared.dependencies import _create_async_client  # type: ignore

CURRENT_DIR = Path(__file__).parent

# Filenames relative to this script
ANIMALS_FILE = CURRENT_DIR / "animals.json"
SENTENCES_FILE = CURRENT_DIR / "sentences.json"


async def _seed_collection(db: AsyncClient, items: List[Dict[str, Any]], kind: str) -> None:
    """Seed a single collection (`animals` or `sentences`) if it's empty."""
    coll_ref = db.collection("content").document(kind).collection("items")

    # Check if already seeded (idempotent)
    existing_docs = [doc async for doc in coll_ref.limit(1).stream()]
    if existing_docs:
        print(f"[seed_games] Collection '{kind}' already contains data – skipping seeding.")
        return

    batch = db.batch()
    for item in items:
        doc_id = item["id"]
        payload = {k: v for k, v in item.items() if k != "id"}
        payload["version"] = 1  # initial content version
        doc_ref = coll_ref.document(doc_id)
        batch.set(doc_ref, payload)
    await batch.commit()
    print(f"[seed_games] Seeded {len(items)} documents into '{kind}'.")


def _load_json(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


async def seed_if_empty() -> None:
    """Seed both animals and sentences collections if empty."""
    db = _create_async_client()
    await _seed_collection(db, _load_json(ANIMALS_FILE), "animals")
    await _seed_collection(db, _load_json(SENTENCES_FILE), "sentences")


# ---------------------------------------------------------------------------
# Entry point to run as a standalone script
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(seed_if_empty())
