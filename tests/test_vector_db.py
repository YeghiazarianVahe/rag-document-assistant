from unittest.mock import patch
from app.services.vector_db import document_exists, delete_document, library


def test_document_exists_true():
    with patch(
        "app.services.vector_db.collection.get",
        return_value={"ids": ["doc1_0"]},
    ):
        assert document_exists("doc1") is True


def test_document_exists_false():
    with patch(
        "app.services.vector_db.collection.get",
        return_value={"ids": []},
    ):
        assert document_exists("missing") is False


def test_delete_document():
    with (
        patch(
            "app.services.vector_db.document_exists",
            return_value=True,
        ),
        patch("app.services.vector_db.collection.delete") as mock_delete,
    ):
        delete_document("doc1")

    mock_delete.assert_called_once_with(where={"document_id": "doc1"})


def test_delete_missing_document():
    with (
        patch(
            "app.services.vector_db.document_exists",
            return_value=False,
        ),
        patch("app.services.vector_db.collection.delete") as mock_delete,
    ):
        delete_document("missing")

    mock_delete.assert_not_called()


def test_library_empty():
    with patch(
        "app.services.vector_db.collection.get",
        return_value={"metadatas": []},
    ):
        result = library()

    assert result == []
