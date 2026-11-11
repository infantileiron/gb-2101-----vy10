import csv, io, math, hashlib, json
from dataclasses import asdict
from src.models.entities import Dataset, DatasetVersion, Supplement
from src.constants.enums import SupplementStatus
from src.utils import repository as repo
from src.utils.identity import new_id, now
COLUMNS = ("batch_id", "station", "group", "loss", "temperature")
ROW_LIMIT = 5000
def checksum(rows):
    return hashlib.sha256(json.dumps(rows, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
def summary(item):
    return {k: v for k, v in item.items() if k not in ("rows", "versions")} | {
        "row_count": len(item["rows"]),
        "stations": sorted({r["station"] for r in item["rows"]}),
        "version_count": len(item.get("versions", [])),
    }
def list_datasets():
    return [summary(i) for i in repo.all_rows("datasets")]
def detail(id):
    return repo.get("datasets", id)
def list_supplements(dataset_id):
    repo.get("datasets", dataset_id)
    return [s for s in repo.all_rows("supplements") if s["dataset_id"] == dataset_id]
def parse_rows(csv_text, min_rows=10):
    """Shared strict parsing for imports and supplements. Malformed rows reject the whole file."""
    reader = csv.DictReader(io.StringIO(csv_text.lstrip("\ufeff")))
    if not set(COLUMNS).issubset(reader.fieldnames or []):
        raise ValueError("CSV需包含batch_id,station,group,loss,temperature")
    rows, seen = [], set()
    for i, r in enumerate(reader, 2):
        if i > ROW_LIMIT + 1:
            raise ValueError("单次最多5000行")
        try:
            loss, temp = float(r["loss"]), float(r["temperature"])
            if not math.isfinite(loss + temp) or not 0 <= loss <= 100 or not -30 <= temp <= 60:
                raise ValueError()
            if r["group"] not in ("A", "B") or not r["station"].strip() or not r["batch_id"].strip():
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError(f"第{i}行数值、分组、站点或批次编号无效")
        batch_id = r["batch_id"].strip()
        if batch_id in seen:
            raise ValueError(f"第{i}行批次编号{batch_id}在本次文件内重复")
        seen.add(batch_id)
        rows.append({
            "batch_id": batch_id,
            "station": r["station"].strip(),
            "group": r["group"],
            "loss": loss,
            "temperature": temp,
            "revision": 0,
        })
    if len(rows) < min_rows:
        raise ValueError("至少需要10行观测" if min_rows > 1 else "补报文件至少需要1行观测")
    return rows
def create(data):
    rows = parse_rows(data.csv_text)
    for r in rows:
        r["revision"] = 0
    stamp = now()
    initial = asdict(DatasetVersion(
        version=1, source=data.source, created_at=stamp,
        row_count=len(rows), checksum=checksum(rows), note="初始导入", rows=rows,
    ))
    item = Dataset(new_id("ds"), data.name, data.source, rows, stamp, 1, 0, [initial])
    repo.put("datasets", item)
    return summary(asdict(item))
def same_value(existing, incoming):
    return (existing["station"] == incoming["station"]
            and existing["group"] == incoming["group"]
            and float(existing["loss"]) == float(incoming["loss"])
            and float(existing["temperature"]) == float(incoming["temperature"]))
def submit_supplement(dataset_id, data):
    dataset = repo.get("datasets", dataset_id)
    incoming = parse_rows(data.csv_text, min_rows=1)
    new_batches = sum(1 for r in incoming if r["batch_id"] not in {x["batch_id"] for x in dataset["rows"]})
    if len(dataset["rows"]) + new_batches > ROW_LIMIT:
        raise ValueError(f"数据集累计观测不能超过{ROW_LIMIT}行，本次新增 {new_batches} 条将超限")
    stamp = now()
    detail, working = [], {r["batch_id"]: dict(r) for r in dataset["rows"]}
    applied = duplicates = stale = quarantined = 0
    for row in incoming:
        batch_id, revision = row["batch_id"], data.revision
        current = working.get(batch_id)
        entry = {
            "batch_id": batch_id, "revision": revision,
            "station": row["station"], "group": row["group"],
            "loss": row["loss"], "temperature": row["temperature"],
        }
        if current is None:
            entry["outcome"] = "applied"
            entry["reason"] = "新批次，首次登记"
            row["revision"] = revision
            working[batch_id] = row
            applied += 1
        elif revision < current["revision"]:
            entry["outcome"] = "stale"
            entry["reason"] = f"晚到旧修订 r{revision}，当前已为 r{current['revision']}，不覆盖新值"
            stale += 1
        elif revision == current["revision"]:
            if same_value(current, row):
                entry["outcome"] = "duplicate"
                entry["reason"] = f"修订号 r{revision} 与值均与现存记录一致，重复投递不新增观测"
                duplicates += 1
            else:
                entry["outcome"] = "quarantined"
                entry["reason"] = (
                    f"同号异值：r{revision} 已存在不同观测"
                    f"（现存 loss={current['loss']}/temp={current['temperature']}，"
                    f"补报 loss={row['loss']}/temp={row['temperature']}），隔离待人工裁决，不覆盖"
                )
                quarantined += 1
        else:
            entry["outcome"] = "applied"
            entry["reason"] = f"更新修订 r{current['revision']} → r{revision}"
            row["revision"] = revision
            working[batch_id] = row
            applied += 1
        detail.append(entry)
    new_rows = [working[k] for k in sorted(working)]
    new_version = 0
    if applied:
        new_version = dataset["current_version"] + 1
        version = asdict(DatasetVersion(
            version=new_version, source=data.source, created_at=stamp,
            row_count=len(new_rows), checksum=checksum(new_rows),
            note=f"补报 r{data.revision}：应用 {applied} 条，隔离 {quarantined} 条",
            rows=new_rows, supplement_id="",
        ))
        dataset["rows"] = new_rows
        dataset["current_version"] = new_version
        dataset["latest_revision"] = max(dataset.get("latest_revision", 0), data.revision)
        dataset["versions"].append(version)
    if quarantined:
        status = SupplementStatus.QUARANTINED.value
    elif applied:
        status = SupplementStatus.APPLIED.value
    else:
        status = SupplementStatus.NO_CHANGE.value
    supplement = Supplement(
        new_id("sup"), dataset_id, data.source, data.revision, status,
        applied, duplicates, stale, quarantined, new_version, stamp, detail,
    )
    supplement_dict = asdict(supplement)
    repo.put("supplements", supplement_dict)
    if applied:
        dataset["versions"][-1]["supplement_id"] = supplement_dict["id"]
        repo.put("datasets", dataset)
        from src.services.invalidation import propagate_dataset_change
        propagate_dataset_change(dataset, new_version, supplement_dict["id"], stamp)
    return supplement_dict
