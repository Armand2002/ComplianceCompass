# Aggiorna il modello di base Pydantic per usare la nuova notazione
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    # Usa ConfigDict invece di Config classe
    model_config = ConfigDict(from_attributes=True)  # Invece di orm_mode=True