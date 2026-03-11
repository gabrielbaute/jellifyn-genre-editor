from pydantic import BaseModel, Field

class GenreItem(BaseModel):
    """Representa la vinculación formal de un género en el servidor.
    
    Attributes:
        name: El nombre legible del género (e.g., 'Soundtrack').
        genre_id: El UUID único del género en el sistema.
    """
    name: str = Field(..., alias="Name")
    genre_id: str = Field(..., alias="Id")