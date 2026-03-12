# Jellyfin Genre Editor

Este proyecto es personal, es creado para atender una necesidad muy personal: lidiar con el sistema de etiquetado de Jellyfin a la hora de colocar género a los tracks. 

## Contexto: ¿y esto por qué?

Contexto: tengo una biblioteca de audio considerablemente grande, editar el género de los tracks no es viable con la interfaz de jellifyn, una opción era entonces editar el género directamente en el archivo, pero la interfaz en windows (o en linux, no sé por qué) solo me permite asignar un género por track, en lugar de varios, lo que iba a complicarme mucho las cosas. El sistema de recomendaciones de Jellyfin (o si voy  usar plugins) funciona mejor si los tags y géneros están bien distribuidos. Así que en lugar de pasar todo a m4a y editar los archivos con listas de genéro, pensé que era mejor editar directamente el registro del track en la base de datos de jellyfin, cosa que puedo acceder desde la API. 

Así que empecé a trabajar en ello, duré varios días dándome contra la pared, porque la API de Jellyfin (estoy en la versión 10.10.7, ya que las 10.11.x no son para nada amables con las bibliotecas de audio) es ridículamente grande (en este repo puse el openapi.json y son unas 62mil líneas, no me jodan). Con ayuda de Gemini (que también desvarió bastante y me sacó canas verdes con su "entusiasmo"), logré reducirlo a los endpoints que necesitaba, y luego de manejar algunos esquemas básicos de pydantic, descubrimos que igual la edición de la data requiere que se devuelva el item completo, y no solo el campo que quería editar. En fin, que luego de estructurar todo para trabajar con un script, pues decidí que la forma más cómoda de operar esto era con una CLI, y me puse en ello.

## Instalación del proyecto
Usé `uv` para esto. Si no tienes `uv` instalado, puedes obtenerlo así:

```shell
curl -LsSf [https://astral-sh.uv.run/install.sh](https://astral-sh.uv.run/install.sh) | sh
```

De ahí en adelante seguimos el procedimiento estándar. Clonamos el repo y sincronizamos con `uv sync`. Es importante que crees una `api_key` en Jellyfin, ya que la usaremos para autenticarnos y acceder a la API, y también copia el nombre que le asignaste a la aplicación, serái mportante.

## Ejecución

Puedes ejecutarlo como si fuera un script (caso del archivo `main.py` que está en la raíz del proyecto):

```python
from app.settings.app_settings import settings
from app.settings.app_logs_settings import JGELogger
from app.services.genre_editor import GenreEditor
from app.services.jellyfin_client_service import JellyfinClientService

JGELogger.setup_logging()

def main():
    # Inicializamos el servicio base
    jf_service = JellyfinClientService(settings)
    
    # Inicializamos el editor de géneros
    editor = GenreEditor(jf_service)

    try:
        # Escenario A: Editar todo un artista
        print("--- Editando Artista: Beetlebug ---")
        editor.add_genre_to_all_artist_tracks("Beetlebug", "Indie")

        # Escenario B: Editar un álbum específico
        # Si ya conoces el ID o lo obtienes de una búsqueda
        # editor.add_genre_to_album_tracks("id_del_album", "Synthpop")

    finally:
        jf_service.close()

if __name__ == "__main__":
    main()
```
Para usarlo de esta manera, como script y no como CLI, es importante que configures un archivo .env en l raíz del proyecto, donde clonaste el repo, puedes guiarte del .env.example:

| Variable         | Descripción                                                                       |
|------------------|-----------------------------------------------------------------------------------|
| `APP_NAME`       | Nombre de la APP, puedes poner el mismo que en jellyfin cuando creaste la api_key |
| `API_KEY`        | api_key generada por Jellyfin                                                     |
| `JELLIFYIN_HOST` | Dirección del servidor de Jellyfin en tu red local o en tu dominio                |


## 🛠 Guía de Comandos: GenreEditor CLI

La CLI se ejecuta utilizando el comando base `jge` (por Jellyfin Genre Editor). A continuación, se detallan los subcomandos disponibles y sus respectivos argumentos:

| Comando       | Acción             | Flags / Argumentos | Descripción                                 |
| --------------| ------------------ |------------------- | ------------------------------------------- |
| **`version`** | Muestra la versión | *(Ninguno)*        | Imprime la versión actual de la aplicación. |
| **`init`**    | Inicialización     | `--host` (REQ)     | URL del servidor (ej. `http://localhost:8096`). |
|               |                    | `--api-key` (REQ)  | Token de acceso generado en Jellyfin. |
|               |                    | `--app-name`       | Nombre personalizado para la instancia (Default: `GenreEditor`). |
| **`analyze`** | Análisis de metadatos | `--artist` (REQ) | Nombre del artista para buscar y listar álbumes/IDs. |
|  |  | `--album` | ID específico de un álbum para analizar sus tracks. |
|  |  | `--track` | ID específico de un track para ver su metadata cruda. |
| **`edit`** | Modificación de géneros | `--genre` (REQ) | El nombre del género que se desea añadir (ej. "Rock"). |
|  |  | `--artist` | Aplica el género a la ficha del artista. |
|  |  | `--album` | Aplica el género a la ficha del álbum (usar ID). |
|  |  | `--track` | Aplica el género a un track específico (usar ID). |
|  |  | `--recursive` | **Flag:** Si se usa con `--artist` o `--album`, propaga el género a todos los tracks hijos. |

---

### 💡 Notas de uso rápido

1. **Prioridad en `edit`:** Los flags `--artist`, `--album` y `--track` determinan el "objetivo" de la operación. Se recomienda usar solo uno a la vez.
2. **Uso de IDs:** Para los niveles de álbum y track, se deben utilizar los IDs obtenidos previamente con el comando `analyze`.
3. **Recursividad:** El flag `--recursive` es la herramienta más potente para la edición masiva; asegúrate de haber analizado bien el objetivo antes de ejecutarlo.
4. **El comando init**: este comando es el primero que debes ejecutar si usas la CLI (~~y por qué carajos entonces lo mencionas de último?~~), mediante este comando creamos una carpeta en el directorio del usuario (espero tengas permisos) donde situaremos el .env con los datos de conexión, y tendremos además un directorio para los logs, que podrán consultar allí (le haremos un comando de consulta de los logs en un futuro).

## 📜 Licencia
Este es un proyecto bajo licencia MIT, obviamente!