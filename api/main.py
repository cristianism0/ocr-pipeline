from fastapi import FastAPI
from contextlib import asynccontextmanager
from concurrent.futures import ProcessPoolExecutor
from api.routes.witchtr_router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.executor = ProcessPoolExecutor(max_workers=4)
    yield
    app.state.executor.shutdown(wait=True)


app = FastAPI(title="WitcHTR", version="0.1", lifespan=lifespan)

app.include_router(router)
