from dataclasses import dataclass, field
from typing import Any
from src.constants.enums import RunStatus,ReviewStatus
@dataclass
class Dataset:
    id: str
    name: str
    source: str
    rows: list[dict]
    created_at: str = ""
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
@dataclass
class Review:
    id: str
    run_id: str
    comment: str
    status: str = ReviewStatus.PENDING.value
    reviewer: str = ""
    created_at: str = ""
@dataclass
class Report:
    id: str
    run_id: str
    review_id: str
    title: str
    created_at: str = ""
