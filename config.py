from __future__ import annotations
from pathlib import Path
from typing import Literal, Optional

import yaml
from pydantic import BaseModel, Field, model_validator


class ConfigValidationError(Exception):
    pass


class ServiceConfig(BaseModel):
    name: str = Field(..., pattern=r"^[a-z][a-z0-9-]+$")
    domain: Literal["fx", "credit", "rates", "equity", "payments"]
    owner: str
    env: Literal["dev", "staging", "production"]


class PipelineConfig(BaseModel):
    type: Literal["batch", "streaming", "hybrid"]
    source: str
    destination: str
    schedule: str = "0 6 * * 1-5"
    throughput: Literal["standard", "high"] = "standard"


class InfrastructureConfig(BaseModel):
    cloud: Literal["aws"] = "aws"
    region: str = "eu-west-1"
    compute: Literal["lambda", "ecs", "databricks"] = "lambda"
    database: Literal["rds_postgres", "rds_mysql", "none"] = "rds_postgres"


class ComplianceConfig(BaseModel):
    data_classification: Literal["public", "internal", "confidential", "restricted"] = "confidential"
    sox_relevant: bool = False
    pci_dss: bool = False
    rbi_compliant: bool = False
    pii_fields: list[str] = Field(default_factory=list)


class AtlassianConfig(BaseModel):
    jira_project_key: str
    confluence_space: str
    epic_name: str


class ServiceSpec(BaseModel):
    service: ServiceConfig
    pipeline: PipelineConfig
    infrastructure: InfrastructureConfig
    compliance: ComplianceConfig
    atlassian: Optional[AtlassianConfig] = None

    @model_validator(mode="after")
    def payments_requires_upi(self) -> "ServiceSpec":
        # We'll add upi block later — placeholder for now
        return self

    # Convenience properties — so callers write spec.service_name not spec.service.name
    @property
    def service_name(self) -> str:
        return self.service.name

    @property
    def domain(self) -> str:
        return self.service.domain

    @property
    def env(self) -> str:
        return self.service.env

    @property
    def region(self) -> str:
        return self.infrastructure.region

    @property
    def s3_bucket(self) -> str:
        return f"{self.service.name}-data-lake-{self.service.env}"


def load_config(path: str | Path = "service.yaml") -> ServiceSpec:
    config_path = Path(path)

    if not config_path.exists():
        raise ConfigValidationError(f"service.yaml not found at '{config_path.resolve()}'")

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ConfigValidationError("service.yaml must be a YAML mapping.")

    try:
        return ServiceSpec.model_validate(raw)
    except Exception as e:
        raise ConfigValidationError(str(e)) from e