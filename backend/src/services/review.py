from fastapi import HTTPException
from src.constants.enums import ReviewStatus, RunStatus
from src.models.entities import Review
from src.utils import repository as repo
from src.utils.identity import new_id, now
def list_reviews(): return repo.all_rows("reviews")
def create(data,user):
    run=repo.get("runs",data.run_id)
    if run["status"]==RunStatus.INVALIDATED.value:
        raise HTTPException(409,"该运行依据的数据已更新并失效，请对新版本数据重算后再提交复核")
    if run["status"]!="completed": raise ValueError("只有已完成的运行可提交复核")
    if any(r["run_id"]==data.run_id and r["status"] in ("pending","approved") for r in repo.all_rows("reviews")): raise HTTPException(409,"该运行已有待审或通过的复核")
    item=Review(new_id("rev"),data.run_id,data.comment,created_at=now())
    return repo.put("reviews",item)
def decide(id,data,user):
    item=repo.get("reviews",id)
    if item["status"]==ReviewStatus.INVALIDATED.value:
        raise HTTPException(409,"该复核依据的旧分析已失效，不能继续审批；请复核新版本数据的重算结果")
    if item["status"]!=ReviewStatus.PENDING.value: raise HTTPException(409,"该复核已处理")
    item.update(status=data.status,comment=data.comment,reviewer=user["email"])
    return repo.put("reviews",item)
