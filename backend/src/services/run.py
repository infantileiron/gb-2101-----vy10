from src.models.entities import AnalysisRun
from src.utils import repository as repo
from src.utils.identity import new_id, now
from src.services.statistics import analyze
from src.config.settings import TASK_MODE, REDIS_URL, ARTIFACT_DIR
import json
def list_runs(): return repo.all_rows("runs")
def execute(id):
    run=repo.get("runs",id)
    if run["status"] in ("running","completed","invalidated"): return run
    run["status"]="running"; repo.put("runs",run)
    try:
        exp=repo.get("experiments",run["experiment_id"])
        dataset=repo.get("datasets",exp["dataset_id"])
        run["result"]=analyze(dataset["rows"],exp["max_loss"],exp["iterations"],exp["seed"])
        run["dataset_version"]=dataset["current_version"]
        ARTIFACT_DIR.mkdir(parents=True,exist_ok=True)
        (ARTIFACT_DIR / (id+".json")).write_text(json.dumps(run["result"],ensure_ascii=False))
        # A supplement may have invalidated this run while it was computing.
        latest=repo.get("runs",id)
        if latest["status"]=="invalidated":
            run["status"]="invalidated"
            run["invalidated_at"]=latest.get("invalidated_at","")
            run["invalidated_reason"]=latest.get("invalidated_reason","")
        else:
            run["status"]="completed"
    except Exception as exc:
        run["status"]="failed"; run["error"]=str(exc)
    return repo.put("runs",run)
def create(data):
    exp=repo.get("experiments",data.experiment_id)
    dataset=repo.get("datasets",exp["dataset_id"])
    if sum(r["status"] in ("queued","running") for r in repo.all_rows("runs"))>=10: raise ValueError("运行队列已满，请等待已有任务完成")
    run=AnalysisRun(new_id("run"),data.experiment_id,created_at=now())
    run.dataset_version=dataset["current_version"]
    run=repo.put("runs",run)
    if TASK_MODE=="inline": return execute(run["id"])
    try:
        import redis
        redis.Redis.from_url(REDIS_URL).rpush("fresh-trial:jobs",run["id"])
    except Exception:
        run["status"]="failed"; run["error"]="队列不可用，请恢复Redis后重新提交"
        repo.put("runs",run)
        raise ValueError(run["error"])
    return run
