# NEXUS-M — Autonomous Merchant & Network Intelligence Platform

**An end-to-end payment analytics and intelligence platform built with Python, data engineering, APIs, AI-assisted investigations, and cloud integration.**

NEXUS-M is a portfolio project that demonstrates how payment transaction data can be transformed into actionable network intelligence. It combines payment performance analytics, merchant insights, anomaly detection, settlement reconciliation, recovery opportunity analysis, and an AI-assisted investigation workflow in one modular platform.

The project is designed to demonstrate practical software engineering and data analytics skills through reusable components, automated tests, API development, and cloud integration code.

## Key Features

### Payment Network Analytics
- Calculate key performance indicators for payment transactions.
- Analyze payment and merchant performance.
- Identify operational trends and potential areas for improvement.
- Generate structured analytical outputs for downstream applications.

### Anomaly Detection & Investigation
- Identify unusual transaction and operational patterns.
- Investigate anomalies using supporting analytical evidence.
- Organize findings to help explain potential root causes.
- Surface actionable insights for further review.

### Settlement Reconciliation
- Compare transaction and settlement records.
- Identify reconciliation mismatches and exceptions.
- Produce structured reconciliation results to support investigation.

### Recovery Opportunity Intelligence
- Analyze potential recovery opportunities.
- Estimate and prioritize opportunities using available analytical evidence.
- Present results to support data-driven decision-making.

### API & Dashboard
- Expose application functionality through a FastAPI backend.
- Provide a Streamlit interface for interacting with analytical outputs.
- Separate analytics and investigation logic into modular components.

### AI-Assisted Investigation
- Use retrieval-based context to support investigation workflows.
- Select approved tools for specific analytical questions.
- Assemble evidence from analytics and reconciliation results.
- Evaluate investigation behavior and apply guardrails.

### Google Cloud Integration
- Include integration code for Google Cloud Storage and BigQuery.
- Support cloud-oriented data storage and analytical workflows.
- Include integration tests for validating application behavior.

**Note:** Cloud integration code and mocked-client tests do not establish that the platform has been deployed to live Google Cloud services. A real cloud deployment requires project configuration, credentials, enabled APIs, and successful end-to-end validation.

## Architecture

The platform follows a modular architecture:

```text
Synthetic Payment Data
         |
         v
Data Processing & Analytics
         |
         +--------------------+
         |                    |
         v                    v
 KPI & Merchant Insights   Anomaly Detection
         |                    |
         +----------+---------+
                    |
                    v
        Reconciliation & Recovery
                    |
                    v
        Investigation & AI Tools
                    |
          +---------+---------+
          |                   |
          v                   v
      FastAPI API        Streamlit UI
          |
          v
   Cloud Integration Layer
   Google Cloud Storage
        & BigQuery
```

The diagram represents the intended application structure; the exact runtime services depend on local configuration and deployment.

## Technology Stack

| Area | Technologies |
|---|---|
| Programming | Python |
| Data processing | Pandas, PySpark |
| Backend | FastAPI |
| Interactive dashboard | Streamlit |
| Database | PostgreSQL |
| Testing | pytest |
| AI-assisted workflows | Retrieval, tool calling, evaluation, guardrails |
| Cloud integration | Google Cloud Storage, BigQuery |
| Development tools | Git, GitHub |

## Testing

Automated tests cover the project's analytics, investigation workflows, and integration logic.

The verified local test run completed with:

- **157 passed**
- **2 warnings**

The results reflect the local environment at the time of testing. The warnings included Google Cloud library support considerations for the Python 3.10.2 environment.

Run the test suite from the project root:

```powershell
cd D:\nexus-m
.\.venv\Scripts\Activate.ps1
python -m pytest -v
```

If the virtual environment has not been created, follow the project's dependency and environment setup instructions before running the tests.

## Local Setup

### Prerequisites

- Python compatible with the project's dependencies
- Git
- A terminal such as PowerShell
- PostgreSQL if required by the selected application configuration

### 1. Clone the repository

Replace `YOUR-USERNAME` with your GitHub username.

```powershell
git clone https://github.com/YOUR-USERNAME/nexus-m.git
cd nexus-m
```

### 2. Create a virtual environment

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If Python 3.10 is unavailable, install a compatible Python version and verify dependency compatibility before proceeding.

### 3. Install dependencies

If the repository contains a `requirements.txt` file:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If dependencies are managed through another file or package manager, use the instructions provided by that configuration.

### 4. Configure environment variables

If the project uses environment variables, create a local `.env` file based on `.env.example`, if that example file is included.

Add your own local configuration values. Never commit API keys, database passwords, service-account credentials, or other secrets.

### 5. Run the application

Start the API using the project's configured FastAPI entry point. For example, if the application module is `app.main`:

```powershell
uvicorn app.main:app --reload
```

When the API is running, FastAPI commonly provides interactive documentation at:

- API documentation: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

Start the Streamlit dashboard using the actual dashboard entry-point file in the repository. For example, if it is `dashboard.py`:

```powershell
streamlit run dashboard.py
```

**Important:** Confirm the actual module names, dashboard filename, database initialization procedure, and required environment variables in the repository before treating these example commands as verified setup instructions.

## Project Structure

The following is a conceptual overview. Actual filenames and directories may vary by implementation.

```text
nexus-m/
├── ai/
│   └── agents/           # Investigation and tool-selection logic
├── app/                  # API and application components
├── data/                 # Synthetic or generated datasets
├── tests/                # Automated tests
├── scripts/              # Setup and utility scripts
├── docs/                 # Documentation and screenshots
├── .gitignore
├── README.md
└── requirements.txt      # If used by the project
```

## Data & Responsible Use

NEXUS-M uses **synthetic payment data for demonstration**. It is not connected to a real payment network, financial institution, or live payment-processing system.

Anomaly detection and recovery opportunity estimates are analytical outputs, not proof of fraud or guaranteed financial recovery. Findings would require validation against real-world business rules and reliable source data before operational use.

## Future Improvements

- Deploy the API and dashboard to a cloud environment.
- Add a production database migration workflow.
- Introduce CI pipelines for automated testing and quality checks.
- Add authentication, authorization, and structured audit logging.
- Add monitoring, performance benchmarks, and operational metrics.
- Validate Google Cloud integrations against a real configured project.
- Add screenshots, sample reports, and reproducible demonstration datasets.

## What This Project Demonstrates

- Python application development and modular design
- Data transformation and payment analytics
- REST API development
- Automated testing and test-driven debugging
- Anomaly investigation and reconciliation workflows
- AI-assisted tool orchestration and guardrails
- Cloud integration patterns
- Documentation and reproducible development practices

## Author

**Yash Kalbhile**

GitHub: https://github.com/yash45615

LinkedIn: https://www.linkedin.com/in/yash-kalbhile-697727231/

---

*Built as a software engineering and data intelligence portfolio project.*
