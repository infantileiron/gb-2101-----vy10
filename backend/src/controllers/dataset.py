from src.services import dataset as service
def list_items(): return service.list_datasets()
def detail(id): return service.detail(id)
def create(data): return service.create(data)
def supplements(id): return service.list_supplements(id)
def submit_supplement(id, data): return service.submit_supplement(id, data)
def version_detail(id, version):
    dataset = service.detail(id)
    match = next((v for v in dataset.get("versions", []) if v["version"] == version), None)
    if match is None:
        from fastapi import HTTPException
        raise HTTPException(404, "该数据版本不存在")
    return match
