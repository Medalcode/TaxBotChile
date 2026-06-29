from contextlib import asynccontextmanager

from app.models import Base, engine
from app.routers import auth_router, income_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="TaxBotChile API",
    description="Asistente Tributario para Freelancers Chilenos",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(income_router.router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
