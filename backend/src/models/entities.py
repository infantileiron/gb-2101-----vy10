from dataclasses import dataclass, field
from typing import Any
from src.constants.enums import RunStatus,ReviewStatus,SupplementStatus
@dataclass
class DatasetVersion:
    version: int
    source: str
    created_at: str
    row_count: int
    checksum: str
    note: str = ""
    rows: list[dict] = field(default_factory=list)
    supplement_id: str = ""
@dataclass
class Dataset:
    id: str
    name: str
    source: str
    rows: list[dict]
    created_at: str = ""
    current_version: int = 1
    latest_revision: int = 0
    versions: list[dict] = field(default_factory=list)
@dataclass
class Supplement:
    id: str
    dataset_id: str
    source: str
    revision: int
    status: str = SupplementStatus.APPLIED.value
    applied_count: int = 0
    duplicate_count: int = 0
    stale_count: int = 0
    quarantined_count: int = 0
    new_version: int = 0
    created_at: str = ""
    detail: list[dict] = field(default_factory=list)
@dataclass
class Experiment:
    id: str
    name: str
    dataset_id: str
    max_loss: float = 15
    iterations: int = 999
    seed: int = 202611
    created_at: str = ""
@dataclass
class AnalysisRun:
    id: str
    experiment_id: str
    status: str = RunStatus.QUEUED.value
    result: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    created_at: str = ""
    dataset_version: int = 0
    invalidated_at: str = ""
    invalidated_reason: str = ""
@dataclass
class Review:
    id: str
    run_id: str
    comment: str
    status: str = ReviewStatus.PENDING.value
    reviewer: str = ""
    created_at: str = ""
    invalidated_at: str = ""
    invalidated_reason: str = ""
@dataclass
class Report:
    id: str
    run_id: str
    review_id: str
    title: str
    created_at: str = ""
    status: str = "active"
    invalidated_at: str = ""
    invalidated_reason: str = ""
