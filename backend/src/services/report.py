import csv,io
from fastapi import HTTPException
from src.models.entities import Report
from src.config.settings import ARTIFACT_DIR
from src.utils import repository as repo
from src.utils.identity import new_id,now
def safe_cell(value):
    return "'"+value if isinstance(value,str) and value.lstrip().startswith(("=","+","-","@")) else value
def list_reports(): return repo.all_rows("reports")
def create(data):
    run,review=repo.get("runs",data.run_id),repo.get("reviews",data.review_id)
    if review["status"]!="approved" or review["run_id"]!=run["id"] or run["status"]!="completed": raise ValueError("报告必须引用该运行已通过的复核")
    report=repo.put("reports",Report(new_id("rpt"),data.run_id,data.review_id,data.title,now()))
    ARTIFACT_DIR.mkdir(parents=True,exist_ok=True)
    (ARTIFACT_DIR/(report["id"]+".csv")).write_text(download(report["id"]),encoding="utf-8")
    return report
def download(id):
    report=repo.get("reports",id); run=repo.get("runs",report["run_id"])
    if repo.get("reviews",report["review_id"])["status"]!="approved": raise HTTPException(403,"复核未通过")
    r=run["result"]; out=io.StringIO(); writer=csv.writer(out)
    writer.writerow(["report","effect_B_minus_A_pp","p_two_sided","ci95_low","ci95_high","included","excluded","seed","checksum"])
    title=safe_cell(report["title"])
    writer.writerow([title,r["effect"],r["p_value"],r["ci_low"],r["ci_high"],r["included"],r["excluded"],r["seed"],r["checksum"]])
    writer.writerow([]);writer.writerow(["station","A_n","B_n","effect_pp","weight"])
    for s in r["sites"]: writer.writerow([safe_cell(s["station"]),s["A"],s["B"],s["effect"],s["weight"]])
    return "\ufeff"+out.getvalue()
