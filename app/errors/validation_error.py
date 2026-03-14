from app.errors.base_error import GenreEditorError

class ValidationError(GenreEditorError):
    """
    Error de validación de datos o reglas de negocio.
    """
    pass