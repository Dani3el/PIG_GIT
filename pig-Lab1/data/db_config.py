from pathlib import Path
import sys

def _app_root() -> Path:
    # în modul “frozen” (PyInstaller), pune fișierele lângă executabil
    if getattr(sys, "frozen", False) and hasattr(sys, "executable"):
        return Path(sys.executable).parent
    # în modul normal, baza proiectului (…/pig-Lab1)
    return Path(__file__).resolve().parent.parent

class DBConfig:
    BASE_DIR = _app_root()
    SQLITE_PATH = str((BASE_DIR / "school.db").resolve())
    DATABASE_URL = ""  # lasă gol pentru SQLite
