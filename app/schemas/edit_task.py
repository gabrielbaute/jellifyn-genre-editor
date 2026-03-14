from pydantic import BaseModel
from typing import Optional
from app.enums import ItemType

class EditTask(BaseModel):
    """Representa una unidad de trabajo individual en el plan de ejecución."""
    item_id: str
    name: str
    type: ItemType
    parent_name: Optional[str] = None
    
    class Config:
        frozen = True  # La tarea es inmutable una vez creada