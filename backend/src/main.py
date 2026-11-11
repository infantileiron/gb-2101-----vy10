import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.config.settings import SEED_DEMO
from src.utils import repository as repo
from src.middlewares.audit import AuditMiddleware
from src.middlewares.errors import ErrorMiddleware
from src.routes import auth,dataset,experiment,run,review,report
@asynccontextmanager
async def lifespan(app):
    repo.init_db()
    if SEED_DEMO:
        try:
            from src.services.seed import seed
            seed()
        except Exception: logging.exception("demo seed failed; API remains available")
    yield
app=FastAPI(title="青禾鲜品 · 保鲜包装随机试验",lifespan=lifespan)
app.add_middleware(AuditMiddleware)
app.add_middleware(ErrorMiddleware)
for module in (auth,dataset,experiment,run,review,report): app.include_router(module.router)
@app.get("/health")
def health():
    repo.all_rows("users")
    return {"status":"ok","service":"fresh-trial"}
