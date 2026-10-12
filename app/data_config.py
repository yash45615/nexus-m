from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"


# ============================================================
# DATASET SIZE
# ============================================================

NUMBER_OF_MERCHANTS = 10_000
NUMBER_OF_PARTNERS = 12
NUMBER_OF_REGIONS = 8
NUMBER_OF_CATEGORIES = 20

NUMBER_OF_DAYS = 180

NUMBER_OF_TRANSACTIONS = 250_000


# ============================================================
# RANDOMNESS
# ============================================================

RANDOM_SEED = 42


# ============================================================
# TRANSACTION PARAMETERS
# ============================================================

MIN_TRANSACTION_AMOUNT = 10.0
MAX_TRANSACTION_AMOUNT = 250_000.0


# ============================================================
# INCIDENT WINDOWS
# ============================================================

INCIDENT_START_DAY = 120
INCIDENT_END_DAY = 126

INCIDENT_PARTNER_ID = "PARTNER_07"
INCIDENT_REGION = "West"


# ============================================================
# DATA QUALITY INJECTION
# ============================================================

DUPLICATE_RATE = 0.005
MISSING_MERCHANT_RATE = 0.002
INVALID_AMOUNT_RATE = 0.001