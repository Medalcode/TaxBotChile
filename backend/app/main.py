from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth_router, income_router

app = FastAPI(
    title="TaxBotChile API",
    description="Asistente Tributario para Freelancers Chilenos",
    version="0.1.0",
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
