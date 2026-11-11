from src.models.entities import Experiment
from src.utils import repository as repo
from src.utils.identity import new_id, now
def list_experiments(): return repo.all_rows("experiments")
def create(data):
    repo.get("datasets",data.dataset_id)
    return repo.put("experiments",Experiment(new_id("exp"),data.name,data.dataset_id,data.max_loss,data.iterations,data.seed,now()))
