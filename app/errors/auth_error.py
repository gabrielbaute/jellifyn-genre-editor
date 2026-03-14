from app.errors.base_error import GenreEditorError

class AuthError(GenreEditorError):
    """Error de autenticación o API Key inválida."""
    pass