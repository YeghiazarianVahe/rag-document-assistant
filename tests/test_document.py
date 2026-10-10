from app.services.document import chunk_text
import pytest


def test_chunk_text_basic():
    result = chunk_text("abcdefghij", chunk_size=4, overlap=1)
    expected = ["abcd", "defg", "ghij", "j"]
    assert result == expected


def test_chunk_text_invalid_chunk_size():
    with pytest.raises(ValueError, match="Chunk size must be greater than 0"):
        chunk_text("abcdefghij", chunk_size=0, overlap=0)


def test_chunk_text_negative_overlap():
    with pytest.raises(ValueError, match="Overlap must be non-negative."):
        chunk_text("abcdefghij", chunk_size=4, overlap=-1)


def test_chunk_text_overlap_greate_than_chunk_size():
    with pytest.raises(ValueError, match="Overlap must be less than chunk size."):
        chunk_text("abcdefghij", chunk_size=4, overlap=5)
