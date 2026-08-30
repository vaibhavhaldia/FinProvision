from __future__ import annotations
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from config import ServiceSpec

TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "databricks"

DOMAIN_TEMPLATE = {
    "fx":       "base_ingestion.py.j2",
    "credit":   "base_ingestion.py.j2",
    "rates":    "base_ingestion.py.j2",
    "equity":   "base_ingestion.py.j2",
    "payments": "base_ingestion.py.j2",  # payments gets base + upi on top
}


class DatabricksGenerator:
    def __init__(self, spec: ServiceSpec, dry_run: bool = False) -> None:
        self.spec = spec
        self.dry_run = dry_run
        self.out = Path(f"databricks/{spec.service_name}")

    def generate(self) -> str:
        jenv = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        if not self.dry_run:
            self.out.mkdir(parents=True, exist_ok=True)

        context = {
            "service_name":        self.spec.service_name,
            "domain":              self.spec.domain,
            "env":                 self.spec.env,
            "source":              self.spec.pipeline.source,
            "s3_bucket":           self.spec.s3_bucket,
            "pipeline_version":    "0.1.0",
            "data_classification": self.spec.compliance.data_classification,
            "pii_fields":          self.spec.compliance.pii_fields,
        }

        # 01 — domain ingestion notebook
        template_name = DOMAIN_TEMPLATE[self.spec.domain]
        self._write(jenv, template_name, "01_ingestion.py", context)

        # 03 — UPI reconciliation (payments only)
        if self.spec.domain == "payments":
            upi_context = {
                **context,
                "npci_settlement_path": "your-npci-bucket/settlement",
                "rbi_exception_path":   "your-rbi-bucket/exceptions",
            }
            self._write(jenv, "upi_reconciliation.py.j2", "03_upi_reconciliation.py", upi_context)

        return str(self.out)

    def _write(self, jenv, template_name: str, out_filename: str, context: dict) -> None:
        rendered = jenv.get_template(template_name).render(**context)
        if self.dry_run:
            print(f"[dry-run] Would write: {self.out}/{out_filename}")
            return
        path = self.out / out_filename
        path.write_text(rendered)
        print(f"→ {path}")