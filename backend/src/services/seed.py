import random
from src.utils import repository as repo
from src.utils.identity import now
from src.utils.security import hash_password
from src.services.statistics import analyze
def demo_rows():
    rng=random.Random(202611)
    rows=[]
    for i in range(480):
        station=["成都东站","双流冷链站","郫都分拨站"][i%3]
        group="A" if (i//3)%2==0 else "B"
        temp=round(rng.gauss(4.5+(i%3)*.7,1),2)
        loss=round(max(.1,rng.gauss(5.9+(i%3)*.4-(1.25 if group=="B" else 0)+.25*(temp-4.5),.7)),3)
        rows.append({"batch_id":f"QH-202611-{i+1:04d}","station":station,"group":group,"loss":loss,"temperature":temp})
    return rows
def seed():
    repo.init_db(); rows=demo_rows(); stamp=now()
    for role,name in [("admin","何婧 · 研发负责人"),("analyst","陈昱 · 实验分析员"),("viewer","许珂 · 采购观察员")]:
        repo.put("users",{"id":role+"@qinghe.demo","email":role+"@qinghe.demo","role":role,"name":name,"password_hash":hash_password("Qinghe2026!")},insert_only=True)
    repo.put("datasets",{"id":"ds-packaging-nov","name":"11月鲜切叶菜保鲜批次","source":"packaging_trial_202611.csv","rows":rows,"created_at":stamp},insert_only=True)
    for id,name,iterations in [("exp-film-b","封膜B · 3站分层验证",999),("exp-recheck","封膜B · 独立复核方案",1999)]:
        repo.put("experiments",{"id":id,"name":name,"dataset_id":"ds-packaging-nov","max_loss":15,"iterations":iterations,"seed":202611,"created_at":stamp},insert_only=True)
    existing={r["id"] for r in repo.all_rows("runs")}
    if "run-baseline" not in existing:
        repo.put("runs",{"id":"run-baseline","experiment_id":"exp-film-b","status":"completed","result":analyze(rows),"error":"","created_at":stamp},insert_only=True)
    if "run-recheck" not in existing:
        repo.put("runs",{"id":"run-recheck","experiment_id":"exp-recheck","status":"completed","result":analyze(rows,iterations=1999),"error":"","created_at":stamp},insert_only=True)
    repo.put("reviews",{"id":"rev-recheck","run_id":"run-recheck","status":"pending","comment":"独立复核使用1999次重采样，请核对区间与业务成本适用性。","reviewer":"","created_at":stamp},insert_only=True)
    repo.put("reviews",{"id":"rev-baseline","run_id":"run-baseline","status":"approved","comment":"三个站点效果方向一致；仍需结合包装成本与运输损耗复核。","reviewer":"admin@qinghe.demo","created_at":stamp},insert_only=True)
    repo.put("reports",{"id":"rpt-baseline","run_id":"run-baseline","review_id":"rev-baseline","title":"封膜B分层试验 · 研发复核版","created_at":stamp},insert_only=True)
    return {t:len(repo.all_rows(t)) for t in repo.TABLES if t!="audit"}
