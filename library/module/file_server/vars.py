from pathlib import Path

# Entry point for file server
FILE_ENTRYPOINT = "/service/file/{file_id}"
LIB_ASSETS_ENTRYPOINT = "/assets/library/{file:path}"
MODULE_ASSETS_ENTRYPOINT = "/assets/{module}/{file:path}"

# Path to directory where files are stored
LIB_ASSETS_DIR = Path.cwd() / "library" / "assets"
