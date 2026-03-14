from typing import Any, Dict, Optional

class GenreEditorError(Exception):
    """Base para todos los errores de la aplicación."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}