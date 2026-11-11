from pydantic import BaseModel, Field
from typing import Literal
class LoginInput(BaseModel):
    email: str
    password: str
class DatasetInput(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    source: str = Field(default="uploaded.csv", max_length=100)
    csv_text: str = Field(min_length=20, max_length=1000000)
class SupplementInput(BaseModel):
    source: str = Field(default="resubmission.csv", max_length=100)
    revision: int = Field(ge=1, le=2147483647)
    csv_text: str = Field(min_length=20, max_length=1000000)
class ExperimentInput(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    dataset_id: str
    max_loss: float = Field(default=15, gt=0, le=100)
    iterations: int = Field(default=999, ge=99, le=4999)
    seed: int = Field(default=202611, ge=0, le=2147483647)
class RunInput(BaseModel):
    experiment_id: str
class ReviewInput(BaseModel):
    run_id: str
    comment: str = Field(min_length=5, max_length=2000)
class DecisionInput(BaseModel):
    status: Literal["approved", "rejected"]
    comment: str = Field(min_length=5, max_length=2000)
class ReportInput(BaseModel):
    run_id: str
    review_id: str
    title: str = Field(min_length=2, max_length=100)
