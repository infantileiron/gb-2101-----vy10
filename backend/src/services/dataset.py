import csv, io, math
from dataclasses import asdict
from src.models.entities import Dataset
from src.utils import repository as repo
from src.utils.identity import new_id, now
def summary(item):
    return {k:v for k,v in item.items() if k!="rows"} | {"row_count":len(item["rows"]),"stations":sorted({r["station"] for r in item["rows"]})}
def list_datasets(): return [summary(i) for i in repo.all_rows("datasets")]
def detail(id): return repo.get("datasets",id)
def create(data):
    reader = csv.DictReader(io.StringIO(data.csv_text.lstrip("\ufeff")))
    expected = {"batch_id","station","group","loss","temperature"}
    if not expected.issubset(reader.fieldnames or []): raise ValueError("CSV需包含batch_id,station,group,loss,temperature")
    rows=[]; seen=set()
    for i,r in enumerate(reader,2):
        if i>5001: raise ValueError("单次最多5000行")
        try:
            loss,temp = float(r["loss"]),float(r["temperature"])
            if not math.isfinite(loss+temp) or not 0<=loss<=100 or not -30<=temp<=60: raise ValueError()
            if r["group"] not in ("A","B") or not r["station"].strip() or not r["batch_id"].strip() or r["batch_id"] in seen: raise ValueError()
        except (ValueError,TypeError): raise ValueError(f"第{i}行数值、分组、站点或批次编号无效/重复")
        seen.add(r["batch_id"])
        rows.append({"batch_id":r["batch_id"],"station":r["station"],"group":r["group"],"loss":loss,"temperature":temp})
    if len(rows)<10: raise ValueError("至少需要10行观测")
    item=Dataset(new_id("ds"),data.name,data.source,rows,now())
    repo.put("datasets",item)
    return summary(asdict(item))
