"""Propagate dataset version changes to runs, reviews and reports.

A new dataset version invalidates every run computed against an older snapshot.
The old run result (and its artifact) is retained as evidence, but downstream
reviews/reports can no longer be decided or downloaded against stale numbers.
"""
from src.constants.enums import RunStatus, ReviewStatus
from src.utils import repository as repo
from src.utils.identity import now
def invalidate_dependents(dataset_id, new_version, supplement_id="", stamp=None):
    stamp = stamp or now()
    reason = f"数据集发布新版本 v{new_version}（补报 {supplement_id or '手动更新'}），旧结果所依据的数据已被替换"
    experiments = [e for e in repo.all_rows("experiments") if e["dataset_id"] == dataset_id]
    affected_runs, affected_reviews, affected_reports = [], [], []
    for run in repo.all_rows("runs"):
        if run.get("dataset_version") and run["dataset_version"] < new_version \
                and run["experiment_id"] in {e["id"] for e in experiments} \
                and run["status"] != RunStatus.INVALIDATED.value:
            run["status"] = RunStatus.INVALIDATED.value
            run["invalidated_at"] = stamp
            run["invalidated_reason"] = reason
            repo.put("runs", run)
            affected_runs.append(run["id"])
    run_ids = set(affected_runs)
    for review in repo.all_rows("reviews"):
        if review["run_id"] in run_ids and review["status"] != ReviewStatus.INVALIDATED.value:
            review["status"] = ReviewStatus.INVALIDATED.value
            review["invalidated_at"] = stamp
            review["invalidated_reason"] = reason
            repo.put("reviews", review)
            affected_reviews.append(review["id"])
    review_ids = set(affected_reviews)
    for report in repo.all_rows("reports"):
        if report.get("status", "active") != "invalidated" and (
            report["run_id"] in run_ids or report["review_id"] in review_ids
        ):
            report["status"] = "invalidated"
            report["invalidated_at"] = stamp
            report["invalidated_reason"] = reason
            repo.put("reports", report)
            affected_reports.append(report["id"])
    return {
        "reason": reason,
        "runs": affected_runs,
        "reviews": affected_reviews,
        "reports": affected_reports,
    }
def propagate_dataset_change(dataset, new_version, supplement_id, stamp):
    return invalidate_dependents(dataset["id"], new_version, supplement_id, stamp)
