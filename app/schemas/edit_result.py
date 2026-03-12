from pydantic import BaseModel
from typing import Optional

from app.enums import EditStatus, ItemType

class EditResult(BaseModel):
    name: str
    item_type: Optional[ItemType] = None
    status: Optional[EditStatus] = None
    message: Optional[str] = None