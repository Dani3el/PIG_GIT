from pathlib import Path
from presenter.school_presenter import SchoolPresenter
from view.school_view import SchoolView
from data.db_config import DBConfig
from data.db import Database

def _db_sanity_check():
    # deschide DB o dată ca să aplice PRAGMA și să valideze accesul
    try:
        db = Database("")  # SQLite implicit
        db.scalar("SELECT 1")
    except Exception:
        p = Path(DBConfig.SQLITE_PATH)
        if p.exists():
            p.rename(p.with_suffix(".corrupt.bak"))

def main():
    _db_sanity_check()
    presenter = SchoolPresenter(
        initial_counts={"Teacher": 5, "Assistant": 4, "Student": 18},
        seed=42,          # pune None pentru aleator real când DB e goală
        database_url=""   # "" = SQLite; altfel URL Postgres
    )
    app = SchoolView(presenter)
    app.mainloop()

if __name__ == "__main__":
    main()
