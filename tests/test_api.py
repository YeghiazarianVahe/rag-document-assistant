from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_without_relevant_context():
    with patch("app.api.routes.search_chunks", return_value=[]):
        response = client.post(
            "/ask",
            json={
                "question": "What is the capital of Japan?",
                "top_k": 3,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["context"] == []
    assert data["sources"] == []
    assert data["answer"] == "I don't know based on the provided documents."


def test_ask_with_context():
    fake_context = [
        {
            "text": "Customers can return products within 30 days.",
            "distance": 0.2,
            "metadata": {
                "filename": "refund_policy.pdf",
                "chunk_index": 0,
            },
        }
    ]

    with (
        patch(
            "app.api.routes.search_chunks",
            return_value=fake_context,
        ),
        patch(
            "app.api.routes.generate_answer",
            return_value="Yes, you can return it within 30 days.",
        ),
    ):
        response = client.post(
            "/ask",
            json={
                "question": "Can I return my product?",
                "top_k": 3,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["context"] == fake_context
    assert data["answer"] == "Yes, you can return it within 30 days."
    assert data["sources"] == [
        {
            "filename": "refund_policy.pdf",
            "chunk_index": 0,
        }
    ]


def test_upload_document():
    with (
        patch(
            "app.api.routes.load_pdf",
            return_value="Some extracted PDF text",
        ),
        patch(
            "app.api.routes.chunk_text",
            return_value=["chunk 1", "chunk 2"],
        ),
        patch(
            "app.api.routes.add_chunks",
        ) as mock_add_chunks,
    ):
        response = client.post(
            "/documents",
            files={
                "file": (
                    "test.pdf",
                    b"fake pdf bytes",
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "test.pdf"
    assert data["characters"] == len("Some extracted PDF text")
    assert data["chunks"] == 2
    assert "document_id" in data

    mock_add_chunks.assert_called_once()


def test_upload_invalid_pdf():
    with patch(
        "app.api.routes.load_pdf",
        side_effect=ValueError("Only PDF files are supported."),
    ):
        response = client.post(
            "/documents",
            files={
                "file": (
                    "test.txt",
                    b"not a pdf",
                    "text/plain",
                )
            },
        )

    assert response.status_code == 400
    assert response.json() == {"detail": "Only PDF files are supported."}
