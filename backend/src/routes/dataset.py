from fastapi import APIRouter,Depends
from src.controllers import dataset as controller
from src.schemas.entities import DatasetInput, SupplementInput
from src.services.auth import current,editor
router=APIRouter(prefix="/datasets",tags=["datasets"])
@router.get("")
def list_items(user=Depends(current)): return controller.list_items()
@router.post("",status_code=201)
def create(data:DatasetInput,user=Depends(editor)): return controller.create(data)
@router.get("/{id}")
def detail(id:str,user=Depends(current)): return controller.detail(id)
@router.get("/{id}/versions/{version}")
def version_detail(id:str,version:int,user=Depends(current)): return controller.version_detail(id,version)
@router.get("/{id}/supplements")
def supplements(id:str,user=Depends(current)): return controller.supplements(id)
@router.post("/{id}/supplements",status_code=201)
def submit_supplement(id:str,data:SupplementInput,user=Depends(editor)): return controller.submit_supplement(id,data)
