"""Seed initial achievement catalog into Firestore.

Collection: achievement_catalog
Document ID = achievement id (e.g. "weekly_fifty")
Fields: id, name, description, icon_url

Idempotent: does nothing if the collection is non-empty.
Run manually:
    python -m backend.scripts.seed_achievements
Or called from FastAPI startup.
"""
from __future__ import annotations

import asyncio
from typing import List, Dict, Any
from google.cloud.firestore_v1.async_client import AsyncClient

# Internal helper – respects emulator creds
from shared.dependencies import _create_async_client  # type: ignore

# ---------------------------------------------------------------------------
# Catalog definition (can later be moved to separate JSON or admin panel)
# ---------------------------------------------------------------------------
_CATALOG: List[Dict[str, Any]] = [
    # Weekly score achievement (оставляем для обратной совместимости)
    {
        "id": "weekly_fifty",
        "name": "50 очков за неделю",
        "description": "Набери 50 очков за последние 7 дней",
        "icon_url": None,
        "threshold": 50,
    },
    # Perfect session (все ответы верны)
    {
        "id": "perfect_streak",
        "name": "Идеальная сессия",
        "description": "Заверши игру без ошибок",
        "icon_url": None,
        "threshold": 1,
    },
    # Total score milestones
    {
        "id": "total_score_50",
        "name": "Собрано 50 очков",
        "description": "Набери 50 очков суммарно",
        "icon_url": None,
        "threshold": 50,
    },
    {
        "id": "total_score_100",
        "name": "Собрано 100 очков",
        "description": "Набери 100 очков суммарно",
        "icon_url": None,
        "threshold": 100,
    },
    {
        "id": "total_score_500",
        "name": "Собрано 500 очков",
        "description": "Набери 500 очков суммарно",
        "icon_url": None,
        "threshold": 500,
    },
    # 7-day streak
    {
        "id": "streak_7_days",
        "name": "Серия 7 дней",
        "description": "Играй каждый день 7 дней подряд",
        "icon_url": None,
        "threshold": 7,
    },
]

_COLLECTION_NAME = "achievement_catalog"


async def seed_catalog_if_empty() -> None:
    """Populate collection if it's empty."""
    db: AsyncClient = _create_async_client()
    coll_ref = db.collection(_COLLECTION_NAME)

    # Quick check – if any doc exists, skip seeding
    existing_docs = [doc async for doc in coll_ref.limit(1).stream()]
    if existing_docs:
        print("[seed_achievements] Catalog already seeded – skipping.")
        return

    batch = db.batch()
    for item in _CATALOG:
        doc_ref = coll_ref.document(item["id"])
        batch.set(doc_ref, item)
    await batch.commit()
    print(f"[seed_achievements] Seeded {len(_CATALOG)} achievement definitions.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(seed_catalog_if_empty())
