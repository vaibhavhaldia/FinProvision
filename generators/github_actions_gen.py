from __future__ import annotations
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from config import ServiceSpec

TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "github_actions"


class GitHubActionsGenerator:
    def __init__(self, spec: ServiceSpec, dry_run: bool = False) -> None:
        self.spec = spec
        self.dry_run = dry_run
        self.out_dir = Path(".github/workflows")

    def generate(self) -> str:
        env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template("python_pipeline.yml.j2")
        rendered = template.render(
            service_name=self.spec.service_name,
            domain=self.spec.domain,
            env=self.spec.env,
            region=self.spec.region,
            sox_relevant=self.spec.compliance.sox_relevant,
            pci_dss=self.spec.compliance.pci_dss,
        )

        filename = f"{self.spec.service_name}.yml"
        out_path = self.out_dir / filename

        if self.dry_run:
            print(f"[dry-run] Would write: {out_path}")
            return f"[dry-run] {out_path}"

        self.out_dir.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered)
        print(f"→ {out_path}")
        return str(out_path)