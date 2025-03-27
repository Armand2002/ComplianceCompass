from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.api import api_router
from src.db.session import engine
from src.models.base import Base

# Crea tabelle del database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Compliance Compass API",
    description="API per la piattaforma wiki collaborativa di normative tecniche e di sicurezza",
    version="0.1.0"
)

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione, limitare agli origin specifici
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include i router API
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Benvenuto nella Compliance Compass API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
