
import json

import pytest

from ai.rag.retriever import (
    build_index,
    chunk_text,
    search_documents,
)


def test_chunk_text_splits_long_documents():
    text = "A" * 2500

    chunks = chunk_text(text, chunk_size=1000, overlap=100)

    assert len(chunks) == 3
    assert len(chunks[0]) == 1000
    assert chunks[0][-100:] == chunks[1][:100]


def test_chunk_text_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=100, overlap=100)


def test_build_index_creates_index_and_manifest(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    (docs_dir / "payments.md").write_text(
        "# Payment approvals\n"
        "Transaction approval rates measure successful payments.\n"
        "Failed transactions may require investigation.\n",
        encoding="utf-8",
    )

    index_dir = tmp_path / "data" / "processed" / "phase20_rag"

    manifest = build_index(
        project_root=tmp_path,
        index_dir=index_dir,
    )

    assert manifest["backend"] == "tfidf"
    assert manifest["document_count"] >= 1
    assert manifest["chunk_count"] >= 1
    assert (index_dir / "retrieval_index.joblib").exists()
    assert (index_dir / "index_manifest.json").exists()

    saved_manifest = json.loads(
        (index_dir / "index_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert saved_manifest["project"] == "NEXUS-M"


def test_search_returns_relevant_passage_and_source(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    (docs_dir / "payments.md").write_text(
        "# Payment approvals\n"
        "Transaction approval rates measure successful payments. "
        "A low approval rate may indicate transaction failures.\n",
        encoding="utf-8",
    )

    (docs_dir / "weather.md").write_text(
        "# Weather report\n"
        "Rainfall and temperature are weather measurements.\n",
        encoding="utf-8",
    )

    index_dir = tmp_path / "index"

    results = search_documents(
        "payment approval transaction failures",
        top_k=3,
        project_root=tmp_path,
        index_dir=index_dir,
        rebuild=True,
    )

    assert results
    assert results[0]["source"] == "docs\\payments.md" or (
        results[0]["source"] == "docs/payments.md"
    )
    assert results[0]["score"] > 0
    assert "approval" in results[0]["text"].lower()


def test_empty_search_query_is_rejected():
    with pytest.raises(ValueError):
        search_documents("   ")


def test_search_returns_no_results_for_unrelated_terms(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    (docs_dir / "payments.md").write_text(
        "Payment transactions and approval rates.",
        encoding="utf-8",
    )

    results = search_documents(
        "quasar nebula telescope",
        top_k=3,
        project_root=tmp_path,
        index_dir=tmp_path / "index",
        rebuild=True,
    )

    assert results == []


def test_empty_project_builds_an_empty_index(tmp_path):
    index_dir = tmp_path / "index"

    manifest = build_index(
        project_root=tmp_path,
        index_dir=index_dir,
    )

    assert manifest["chunk_count"] == 0

    results = search_documents(
        "payment approval",
        project_root=tmp_path,
        index_dir=index_dir,
    )

    assert results == []
