from __future__ import annotations

import os


API_BASE_URL = os.getenv(
    "NEXUS_M_API_URL",
    "http://127.0.0.1:8000",
)

APP_TITLE = "NEXUS-M Analyst Console"

APP_ICON = "📊"

REQUEST_TIMEOUT = int(
    os.getenv(
        "NEXUS_M_API_TIMEOUT",
        "15",
    )
)