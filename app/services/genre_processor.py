from typing import List, Set

class GenreProcessor:
    """
    Se encarga de la lógica de transformación y limpieza de géneros.
    """

    def __init__(self, mandatory_genres: List[str] = None, forbidden_genres: List[str] = None):
        """
        Args:
            mandatory_genres: Géneros que siempre deben estar presentes.
            forbidden_genres: Géneros que deben ser eliminados si existen.
        """
        self.mandatory: Set[str] = set(mandatory_genres or [])
        self.forbidden: Set[str] = set(forbidden_genres or [])

    def process(self, current_genres: List[str]) -> List[str]:
        """
        Aplica las reglas de transformación.
        
        Args:
            current_genres: Lista actual de géneros del track.
            
        Returns:
            List[str]: Lista transformada, sin duplicados y normalizada.
        """
        # Usamos sets para operaciones de álgebra de conjuntos (eficiencia y unicidad)
        genre_set = set(current_genres)
        
        # 1. Eliminar prohibidos: G = G \ F
        genre_set -= self.forbidden
        
        # 2. Agregar obligatorios: G = G ∪ M
        genre_set |= self.mandatory
        
        # 3. Normalización (opcional): e.g., Capitalizar
        return sorted(list(genre_set))