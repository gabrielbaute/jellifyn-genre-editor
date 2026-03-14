from app.errors.base_error import GenreEditorError


class TimeOutError(GenreEditorError):
    """
    Error de tiempo de espera agotado.
    """
    pass