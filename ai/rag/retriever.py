
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDEX_DIR = PROJECT_ROOT / "data" / "processed" / "phase20_rag"

SUPPORTED_EXTENSIONS = {".md", ".txt", ".json", ".csv"}
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_CSV_ROWS = 500
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

INDEX_FILE = "retrieval_index.joblib"
MANIFEST_FILE = "index_manifest.json"


def discover_documents(project_root: Path = PROJECT_ROOT) -> list[Path]:
    """Discover readable project documentation and analytical outputs."""
    candidates: set[Path] = set()

    # Project overview, if available.
    readme = project_root / "README.md"
    if readme.is_file():
        candidates.add(readme)

    # Search only intentional source directories.
    search_roots = [
        project_root / "docs",
        project_root / "reports",
        project_root / "data" / "processed",
    ]

    excluded_parts = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "phase20_rag",
        "output",
    }

    for root in search_roots:
        if not root.exists():
            continue

        for path in root.rglob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            if any(part.lower() in excluded_parts for part in path.parts):
                continue

            try:
                if path.stat().st_size > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue

            candidates.add(path)

    return sorted(candidates)


def read_document(path: Path) -> str:
    """Read a supported document into text, with a bounded CSV preview."""
    try:
        if path.suffix.lower() == ".csv":
            frame = pd.read_csv(path, nrows=MAX_CSV_ROWS)
            if frame.empty:
                return f"CSV file: {path.name}\nNo data rows found."

            return (
                f"CSV file: {path.name}\n"
                f"Columns: {', '.join(map(str, frame.columns))}\n"
                f"Rows:\n{frame.to_csv(index=False)}"
            )

        return path.read_text(encoding="utf-8")

    except (OSError, UnicodeDecodeError, pd.errors.ParserError, ValueError):
        return ""


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split text into overlapping passages for retrieval."""
    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size.")

    normalized = "\n".join(
        line.rstrip() for line in text.splitlines()
    ).strip()

    if not normalized:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        chunk = normalized[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(normalized):
            break

        start = end - overlap

    return chunks


def _make_chunks(
    project_root: Path,
) -> list[dict[str, Any]]:
    """Create text passages while retaining their source file paths."""
    documents: list[dict[str, Any]] = []

    for path in discover_documents(project_root):
        text = read_document(path)

        if not text.strip():
            continue

        try:
            relative_path = str(path.relative_to(project_root))
        except ValueError:
            relative_path = str(path)

        for index, passage in enumerate(chunk_text(text)):
            documents.append(
                {
                    "source": relative_path,
                    "chunk_index": index,
                    "text": passage,
                }
            )

    return documents


def build_index(
    project_root: Path = PROJECT_ROOT,
    index_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Build and persist a local TF-IDF vector index.

    TF-IDF produces sparse text vectors. It is a useful local retrieval
    baseline, but it does not understand meaning as deeply as a neural
    embedding model.
    """
    project_root = Path(project_root).resolve()

    if index_dir is None:
        index_dir = project_root / "data" / "processed" / "phase20_rag"

    index_dir = Path(index_dir)
    index_dir.mkdir(parents=True, exist_ok=True)

    documents = _make_chunks(project_root)
    vectorizer = None
    matrix = None

    if documents:
        vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
            max_features=50000,
            sublinear_tf=True,
        )

        try:
            matrix = vectorizer.fit_transform(
                [document["text"] for document in documents]
            )
        except ValueError:
            # For example, all passages might be empty after tokenization.
            vectorizer = None
            matrix = None
            documents = []

    bundle = {
        "version": 1,
        "backend": "tfidf",
        "project_root": str(project_root),
        "documents": documents,
        "vectorizer": vectorizer,
        "matrix": matrix,
    }

    index_path = index_dir / INDEX_FILE
    joblib.dump(bundle, index_path)

    manifest = {
        "project": "NEXUS-M",
        "backend": "tfidf",
        "document_count": len(
            {document["source"] for document in documents}
        ),
        "chunk_count": len(documents),
        "index_file": INDEX_FILE,
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "source_directories": [
            "README.md",
            "docs/",
            "reports/",
            "data/processed/",
        ],
    }

    (index_dir / MANIFEST_FILE).write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    return manifest


def search_documents(
    query: str,
    top_k: int = 5,
    project_root: Path = PROJECT_ROOT,
    index_dir: Path | None = None,
    rebuild: bool = False,
) -> list[dict[str, Any]]:
    """Return the most relevant passages with scores and source paths."""
    query = query.strip()

    if not query:
        raise ValueError("query must not be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    project_root = Path(project_root).resolve()

    if index_dir is None:
        index_dir = project_root / "data" / "processed" / "phase20_rag"

    index_dir = Path(index_dir)
    index_path = index_dir / INDEX_FILE

    if rebuild or not index_path.exists():
        build_index(project_root=project_root, index_dir=index_dir)

    try:
        bundle = joblib.load(index_path)
    except (OSError, ValueError, EOFError) as exc:
        raise RuntimeError(
            "Could not load the retrieval index. Rebuild it and try again."
        ) from exc

    documents = bundle.get("documents", [])
    vectorizer = bundle.get("vectorizer")
    matrix = bundle.get("matrix")

    if not documents or vectorizer is None or matrix is None:
        return []

    query_vector = vectorizer.transform([query])
    scores = cosine_similarity(query_vector, matrix).ravel()

    ranked_indices = scores.argsort()[::-1][:top_k]
    results: list[dict[str, Any]] = []

    for index in ranked_indices:
        score = float(scores[index])

        # Don't return unrelated passages with zero lexical similarity.
        if score <= 0:
            continue

        document = documents[int(index)]

        results.append(
            {
                "source": document["source"],
                "chunk_index": document["chunk_index"],
                "score": round(score, 4),
                "text": document["text"],
            }
        )

    return results


def main() -> None:
    """Simple interactive search interface."""
    print("NEXUS-M RAG Retrieval")
    print("Type 'exit' to quit.")

    manifest = build_index()
    print(
        f"Indexed {manifest['document_count']} documents "
        f"into {manifest['chunk_count']} chunks."
    )
    print("Retrieval backend: TF-IDF vector search")

    while True:
        try:
            query = input("\nSearch question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if query.lower() in {"exit", "quit"}:
            print("Exiting.")
            break

        if not query:
            print("Enter a question first.")
            continue

        results = search_documents(query, top_k=5)

        if not results:
            print("No matching passages found in the indexed files.")
            continue

        for rank, result in enumerate(results, start=1):
            print(
                f"\n[{rank}] {result['source']} "
                f"(chunk {result['chunk_index']}, "
                f"score {result['score']:.4f})"
            )
            print(result["text"])


if __name__ == "__main__":
    main()
