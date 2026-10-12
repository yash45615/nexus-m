from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BI_DIR = (
    PROJECT_ROOT
    / "dashboards"
    / "powerbi"
)


def test_powerbi_directory_exists():

    assert BI_DIR.exists()


def test_powerbi_documentation_exists():

    assert (
        BI_DIR
        / "README.md"
    ).exists()


def test_powerbi_data_directory_exists():

    assert (
        BI_DIR
        / "data"
    ).exists()


def test_bi_export_module_exists():

    assert (
        PROJECT_ROOT
        / "analytics"
        / "bi"
        / "export.py"
    ).exists()