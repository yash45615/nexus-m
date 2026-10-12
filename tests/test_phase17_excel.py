from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EXCEL_DIR = (
    PROJECT_ROOT
    / "reports"
    / "excel"
)

OUTPUT_FILE = (
    EXCEL_DIR
    / "output"
    / "NEXUS-M_Analyst_Model.xlsx"
)


def test_excel_directory_exists():

    assert EXCEL_DIR.exists()


def test_excel_generator_exists():

    assert (
        EXCEL_DIR
        / "generate_workbook.py"
    ).exists()


def test_excel_output_directory_exists():

    assert (
        EXCEL_DIR
        / "output"
    ).exists()


def test_excel_workbook_exists():

    assert OUTPUT_FILE.exists()