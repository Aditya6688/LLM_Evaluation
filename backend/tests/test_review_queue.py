import pytest

from backend.healing.review_queue import ReviewQueueService


@pytest.mark.asyncio
async def test_create_and_list_review_item(db_session):
    service = ReviewQueueService(db_session)

    item = await service.create_review_item(
        eval_result_id="eval-123",
        reason="Faithfulness below threshold",
    )

    assert item.id is not None
    assert item.status == "pending"
    assert item.reason == "Faithfulness below threshold"

    items = await service.list_items(status="pending")
    assert len(items) == 1
    assert items[0].id == item.id


@pytest.mark.asyncio
async def test_resolve_review_item(db_session):
    service = ReviewQueueService(db_session)

    item = await service.create_review_item(
        eval_result_id="eval-456",
        reason="Test reason",
    )

    resolved = await service.resolve_item(
        item_id=item.id,
        status="resolved",
        resolution_note="Fixed the prompt",
    )

    assert resolved.status == "resolved"
    assert resolved.resolution_note == "Fixed the prompt"
    assert resolved.resolved_at is not None


@pytest.mark.asyncio
async def test_resolve_nonexistent_item(db_session):
    service = ReviewQueueService(db_session)
    result = await service.resolve_item("nonexistent-id", "resolved")
    assert result is None


@pytest.mark.asyncio
async def test_get_stats(db_session):
    service = ReviewQueueService(db_session)

    await service.create_review_item("e1", "reason 1")
    await service.create_review_item("e2", "reason 2")
    item = await service.create_review_item("e3", "reason 3")
    await service.resolve_item(item.id, "dismissed")

    stats = await service.get_stats()
    assert stats["pending"] == 2
    assert stats["dismissed"] == 1
