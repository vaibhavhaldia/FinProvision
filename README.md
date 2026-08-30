# FinProvision

**Internal Developer Platform CLI for financial services data pipelines.**  
Scaffold production-grade AWS infrastructure, CI/CD pipelines, Databricks notebooks, Jira epics, and Confluence ADRs from a single YAML file — with built-in compliance gates for SOX, PCI-DSS, and RBI mandates.

---

## What it does

```bash
finprovision init --config service.yaml
```

```
FinProvision Init — fx-rates-pipeline
Domain: fx | Env: staging

──────────────────── Compliance scan ────────────────────
✓ 0 violations — compliance gate passed.

──────────────────── Terraform ──────────────────────────
✓ Terraform written to terraform/generated/fx-rates-pipeline

──────────────────── GitHub Actions ─────────────────────
✓ GitHub Actions written to .github/workflows/fx-rates-pipeline.yml

──────────────────── Databricks notebooks ───────────────
✓ Notebook: databricks/fx-rates-pipeline/01_ingestion.py

──────────────────── Atlassian ──────────────────────────
✓ Epic created: FX-1
✓ 7 stories created
✓ ADR published: https://yourorg.atlassian.net/wiki/...

✓ Init complete — all generators ran successfully
```

One command. One YAML file. Everything your team needs to start building — infrastructure, pipeline, tickets, and documentation — provisioned in under 60 seconds.

---

## Generators

| Generator | Output | Compliance |
|---|---|---|
| **Terraform** | Private-subnet VPC · KMS-encrypted S3 · prefix-scoped IAM role | SOX, PCI-DSS |
| **GitHub Actions** | 5-stage CI/CD with mandatory compliance gate before deploy | SOX |
| **Databricks** | PySpark ingestion notebook with `assert_quality()` DQ checkpoint | SOX |
| **UPI Reconciliation** | Three-cohort DEEMED state reconciliation notebook | RBI T+1 |
| **Jira** | Epic + domain-specific stories, idempotent (safe to re-run) | — |
| **Confluence** | Architecture Decision Record, auto-published at scaffold time | SOX audit trail |
| **Compliance Scanner** | Detects secrets, PII, banking violations → SARIF output, exit code 1 on CRITICAL | PCI-DSS, SOX |

---

## Domain support

FinProvision ships domain-aware templates for two financial verticals:

**FX (Foreign Exchange)**
- Bloomberg B-PIPE rate ingestion with DELAYED/REALTIME entitlement handling
- Cross-rate derivation (EUR/INR via USD) with audit logging
- SOX-compliant financial figure detection (hardcoded `net_pnl`, `ebitda` blocked)

**Payments (UPI/NPCI)**
- DEEMED state reconciliation per RBI circular — three-cohort logic (matched, pending, exception)
- VPA masking enforced in all log statements (`vpa_payer`, `vpa_payee` → `***@bank`)
- NPCI settlement file parser with T+1 exception report generation
- PCI-DSS card data detection in print/log statements

---

## Compliance gate

The compliance scanner runs **first** in every `init`. A single CRITICAL finding aborts all downstream generation — no Terraform, no Jira tickets, no deploy.

```bash
# Inject a violation
echo 'password = "prod_secret_123"' > test.py

finprovision init --config service.yaml
# ✗ 1 CRITICAL finding — TF-SEC-001: Hardcoded password
# ✗ Init ABORTED — compliance gate failed

echo $?   # → 1

# Remove violation and re-run → exit code 0
```

SARIF output compatible with GitHub Code Scanning:

```bash
finprovision scaffold --config service.yaml --type compliance --sarif report.sarif
```

**Rules engine covers:**
- Secrets: hardcoded passwords, API keys, AWS access key IDs, Bearer tokens, GitHub PATs
- PII: Visa/Mastercard/Amex PANs, SSNs, IBANs, email addresses, Indian mobile numbers, VPAs
- Banking: card data in logs (PCI-DSS), hardcoded CVV/CVV2, account numbers, SOX financial figures, security bypass TODOs

---

## Infrastructure defaults

Every provisioned service gets banking-grade AWS defaults with no opt-in required:

```hcl
# Private subnets only — no public exposure
# NAT Gateway for controlled egress
# KMS encryption on all S3 buckets (enabled automatically when sox_relevant: true)
# IAM role scoped to /${service_name}/* prefix — no wildcard S3 access
# Public access block: all four settings true
# S3 versioning enabled
```

---

## Quick start

**Prerequisites:** Python 3.11+, AWS CLI configured, Atlassian account (optional)

```bash
git clone https://github.com/yourusername/finprovision
cd finprovision
python -m venv .venv && source .venv/bin/activate
pip install -e .

cp .env.example .env
# Add ATLASSIAN_BASE_URL, ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN
```

**Dry run — see what will be generated:**
```bash
finprovision init --config service.yaml --dry-run
```

**Full init — FX domain:**
```bash
finprovision init --config service.yaml
```

**Full init — Payments/UPI domain:**
```bash
finprovision init --config service_payments.yaml
```

**Run generators individually:**
```bash
finprovision scaffold --config service.yaml --type terraform
finprovision scaffold --config service.yaml --type actions
finprovision scaffold --config service.yaml --type notebooks
finprovision scaffold --config service.yaml --type atlassian
finprovision scaffold --config service.yaml --type compliance
```

---

## Service spec (service.yaml)

```yaml
service:
  name: fx-rates-pipeline
  domain: fx                        # fx | payments
  owner: team-treasury
  env: staging                      # dev | staging | prod

pipeline:
  type: batch
  source: bloomberg_api
  destination: s3_data_lake

compliance:
  sox_relevant: true                # enables KMS + SOX gate in CI
  pci_dss: false
  data_classification: confidential
  pii_fields: []

atlassian:
  jira_project_key: FX
  confluence_space: FXTEAM
  epic_name: "FX Rates Pipeline"
```

---

## Architecture

```
service.yaml
     │
     ▼
finprovision init
     │
     ├── Compliance Scanner ──► SARIF report  (exit 1 on CRITICAL → aborts)
     │
     ├── Terraform Generator ──► terraform/generated/{service}/main.tf
     │        └── modules: vpc · s3_data_lake · iam_pipeline_role
     │
     ├── GitHub Actions Generator ──► .github/workflows/{service}.yml
     │        └── jobs: lint → compliance-scan → sox-gate → tf-plan → deploy
     │
     ├── Databricks Generator ──► databricks/{service}/
     │        ├── 01_ingestion.py      (all domains)
     │        └── 03_upi_reconciliation.py  (payments domain only)
     │
     └── Atlassian Generator
              ├── Jira: Epic + domain stories  (idempotent)
              └── Confluence: ADR page
```

---

## Project structure

```
finprovision/
├── cli/
│   ├── main.py                    # Typer app entry point
│   └── commands/
│       ├── scaffold.py            # Individual generator commands
│       └── init.py                # Orchestrates all generators
├── generators/
│   ├── terraform_gen.py
│   ├── github_actions_gen.py
│   ├── databricks_gen.py
│   └── atlassian_gen.py
├── compliance/
│   ├── scanner.py                 # Regex rule engine
│   ├── reporter.py                # Rich table + SARIF output
│   └── rules/
│       ├── secrets.py             # TF-SEC-001 to TF-SEC-008
│       ├── pii.py                 # TF-PII-001 to TF-PII-008
│       └── banking.py             # TF-SOX, TF-PCI, TF-RBI rules
├── templates/
│   ├── github_actions/
│   ├── databricks/
│   └── confluence/
├── terraform/modules/
│   ├── vpc/
│   ├── s3_data_lake/
│   └── iam_pipeline_role/
├── config.py                      # Pydantic v2 config validation
├── service.yaml                   # FX domain example
├── service_payments.yaml          # UPI payments domain example
└── pyproject.toml
```

---

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| CLI framework | Typer + Rich | Type-safe commands, terminal UI |
| Config validation | Pydantic v2 | Fail at parse time, not generate time |
| Templating | Jinja2 (StrictUndefined) | Catches missing variables at render |
| Infrastructure | Terraform HCL modules | Reusable, version-controlled infra |
| Notebooks | PySpark (Databricks) | Standard in financial data engineering |
| API integration | Jira REST v3 (ADF) · Confluence REST v2 | Native Atlassian Cloud APIs |
| Compliance output | SARIF v2.1.0 | Native GitHub Code Scanning format |
| Packaging | PEP 517 / pyproject.toml | Modern Python packaging standard |

---

## Design decisions

**Compliance scan runs first.** No point generating infrastructure or creating Jira tickets if secrets are hardcoded. Fail fast at the cheapest point.

**Jira creation is idempotent.** Re-running `init` on an existing service detects the epic via JQL search and skips story creation. Raw `POST` without a check creates duplicate tickets — a real problem in teams that re-run scaffolding after config changes.

**Private subnets only.** The VPC module has no public subnets. This is a deliberate banking-grade default. Any service that genuinely needs public exposure must override it explicitly — the safe path requires no action, the unsafe path requires a decision.

**KMS tied to SOX flag.** Setting `sox_relevant: true` in the service spec automatically enables KMS encryption on S3. Compliance requirements map directly to infrastructure configuration — no manual step, no chance of forgetting.

**ADF for Jira descriptions.** Jira's REST v3 API requires Atlassian Document Format for rich-text fields. Plain strings return a 400. The `_adf()` helper wraps any text into the minimal valid document schema.

---

*Built as a portfolio project targeting platform and data engineering roles at investment banks and financial services firms.*