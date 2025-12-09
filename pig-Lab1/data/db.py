import sqlite3
import importlib
from typing import Any, Iterable, Optional
from contextlib import contextmanager
from data.db_config import DBConfig

class Database:
    """SQLite by default; optional PostgreSQL via psycopg."""
    def __init__(self, database_url: str = ""):
        self._pg = False
        self._database_url = (database_url or "").strip()
        self._conn: Any = None
        self._sqlite_path: Optional[str] = None

        if self._database_url:
            psycopg = importlib.import_module("psycopg")  # type: ignore
            self._pg = True
            self._conn = psycopg.connect(self._database_url, autocommit=True)
        else:
            self._sqlite_path = DBConfig.SQLITE_PATH
            self._conn = sqlite3.connect(
                self._sqlite_path,
                check_same_thread=False,
                timeout=30.0,
            )
            self._conn.execute("PRAGMA journal_mode=WAL;")
            self._conn.execute("PRAGMA synchronous=NORMAL;")
            self._conn.execute("PRAGMA busy_timeout=30000;")

        self._init_schema()

    def sqlite_path(self) -> Optional[str]:
        return self._sqlite_path

    def _checkpoint(self):
        if not self._pg:
            try:
                self._conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            except Exception:
                pass

    def _init_schema(self) -> None:
        with self.transaction() as cur:
            # versionare simplă
            cur.execute("""CREATE TABLE IF NOT EXISTS __schema_version__(v INTEGER NOT NULL)""")
            cur.execute("SELECT COUNT(*) FROM __schema_version__")
            if cur.fetchone()[0] == 0:
                cur.execute("INSERT INTO __schema_version__(v) VALUES (0)")

            # tabele
            cur.execute("""
                CREATE TABLE IF NOT EXISTS teacher(
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    salary REAL NOT NULL,
                    department TEXT NOT NULL,
                    subject TEXT NOT NULL
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS assistant(
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    salary REAL NOT NULL,
                    department TEXT NOT NULL
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS student(
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    grade INTEGER NOT NULL,
                    speciality TEXT NOT NULL
                );
            """)

            # exemple de migrare viitoare:
            cur.execute("SELECT v FROM __schema_version__")
            v = cur.fetchone()[0]
            if v < 1:
                # ex.: cur.execute("ALTER TABLE student ADD COLUMN group_name TEXT DEFAULT ''")
                cur.execute("UPDATE __schema_version__ SET v=1")

    @contextmanager
    def transaction(self):
        if self._pg:
            cur = self._conn.cursor()
            try:
                yield cur
            finally:
                cur.close()
        else:
            cur = self._conn.cursor()
            try:
                yield cur
                self._conn.commit()
                self._checkpoint()  # face scrierile vizibile imediat pentru vizualizatoare externe
            except:
                self._conn.rollback()
                raise
            finally:
                cur.close()

    def execute(self, sql: str, params: Iterable[Any] = ()):
        try:
            with self.transaction() as cur:
                cur.execute(sql, tuple(params))
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Integrity error: {e}")

    def query(self, sql: str, params: Iterable[Any] = ()) -> list[tuple]:
        with self.transaction() as cur:
            cur.execute(sql, tuple(params))
            return cur.fetchall()

    def scalar(self, sql: str, params: Iterable[Any] = ()) -> Optional[Any]:
        with self.transaction() as cur:
            cur.execute(sql, tuple(params))
            row = cur.fetchone()
            return None if row is None else row[0]
