from fastapi import APIRouter,Depends
from src.controllers import experiment as controller
from src.schemas.entities import ExperimentInput
from src.services.auth import current,editor,admin
router=APIRouter(prefix="/experiments",tags=["experiments"])
@router.get("")
def list_items(user=Depends(current)): return controller.list_items()
@router.post("",status_code=201)
def create(data:ExperimentInput,user=Depends(editor)): return controller.create(data)
