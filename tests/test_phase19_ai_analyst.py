
from apps.ai_analyst.analyst import ask_analyst, collect_evidence


def test_empty_question_is_rejected():
    result = ask_analyst("   ")

    assert result["mode"] == "validation"
    assert "enter a question" in result["answer"].lower()


def test_evidence_collection_returns_expected_structure():
    evidence = collect_evidence()

    assert "sources" in evidence
    assert "warnings" in evidence
    assert isinstance(evidence["sources"], list)
    assert isinstance(evidence["warnings"], list)


def test_question_returns_a_structured_answer(monkeypatch):
    # Keep this test independent of any real API key or network.
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = ask_analyst("Which partners should I investigate?")

    assert isinstance(result["answer"], str)
    assert result["answer"]
    assert result["mode"] in {"local", "local_fallback"}
    assert isinstance(result["sources"], list)
    assert isinstance(result["warnings"], list)


def test_missing_processed_directory_is_handled(monkeypatch, tmp_path):
    import apps.ai_analyst.analyst as analyst_module

    monkeypatch.setattr(
        analyst_module,
        "PROCESSED_DIR",
        tmp_path / "missing_processed",
    )
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    evidence = collect_evidence()

    assert evidence["sources"] == []
    assert evidence["warnings"]