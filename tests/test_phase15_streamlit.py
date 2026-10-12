from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

STREAMLIT_DIR = (
    PROJECT_ROOT
    / "apps"
    / "streamlit"
)

PAGES_DIR = STREAMLIT_DIR / "pages"


def test_streamlit_directory_exists():
    assert STREAMLIT_DIR.exists()


def test_streamlit_main_exists():
    assert (
        STREAMLIT_DIR / "app.py"
    ).exists()


def test_api_client_exists():
    assert (
        STREAMLIT_DIR / "api_client.py"
    ).exists()


def test_components_exists():
    assert (
        STREAMLIT_DIR / "components.py"
    ).exists()


def test_expected_pages_exist():

    expected_pages = [
        "01_Executive_Overview.py",
        "02_KPI_Monitoring.py",
        "03_Anomaly_Investigation.py",
        "04_Root_Cause_Explorer.py",
        "05_Opportunity_Intelligence.py",
        "06_Merchant_Explorer.py",
        "07_Partner_Intelligence.py",
        "08_Reconciliation.py",
        "09_Data_Quality.py",
    ]

    for page in expected_pages:

        assert (
            PAGES_DIR / page
        ).exists(), page