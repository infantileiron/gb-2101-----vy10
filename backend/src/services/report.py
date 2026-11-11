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
    if run["status"]=="invalidated":
        raise HTTPException(409,"该报告引用的分析已因数据更新失效，请基于新版本重算并复核后再归档")
    if review["status"]!="approved" or review["run_id"]!=run["id"] or run["status"]!="completed": raise ValueError("报告必须引用该运行已通过的复核")
    report=repo.put("reports",Report(new_id("rpt"),data.run_id,data.review_id,data.title,now()))
    ARTIFACT_DIR.mkdir(parents=True,exist_ok=True)
    (ARTIFACT_DIR/(report["id"]+".csv")).write_text(download(report["id"]),encoding="utf-8")
    return report
def download(id):
    report=repo.get("reports",id); run=repo.get("runs",report["run_id"])
    if report.get("status","active")=="invalidated":
        raise HTTPException(409,"报告已因源数据更新失效，停止沿用；请查看新版本重算结果生成的报告")
    if repo.get("reviews",report["review_id"])["status"]!="approved": raise HTTPException(403,"复核未通过")
    r=run["result"]; out=io.StringIO(); writer=csv.writer(out)
    writer.writerow(["report","effect_B_minus_A_pp","p_two_sided","ci95_low","ci95_high","included","excluded","seed","checksum","dataset_version"])
    title=safe_cell(report["title"])
    writer.writerow([title,r["effect"],r["p_value"],r["ci_low"],r["ci_high"],r["included"],r["excluded"],r["seed"],r["checksum"],run.get("dataset_version","")])
    writer.writerow([]);writer.writerow(["station","A_n","B_n","effect_pp","weight"])
    for s in r["sites"]: writer.writerow([safe_cell(s["station"]),s["A"],s["B"],s["effect"],s["weight"]])
    return "\ufeff"+out.getvalue()
