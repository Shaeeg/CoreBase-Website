import logging
import os
from contextlib import contextmanager

import psycopg
from psycopg_pool import ConnectionPool

logger = logging.getLogger(__name__)


class AnalyticsUnavailable(Exception):
    """Raised when DATABASE_URL isn't configured or the DB can't be reached."""


_pool = None
_schema_ready = False


def _get_pool():
    global _pool
    if _pool is None:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise AnalyticsUnavailable("DATABASE_URL is not set.")
        try:
            _pool = ConnectionPool(conninfo=database_url, min_size=1, max_size=5, open=True)
        except Exception as exc:
            raise AnalyticsUnavailable(f"Could not connect to analytics database: {exc}") from exc
    return _pool


@contextmanager
def _cursor():
    # pool.connection() hands back a connection wrapped in `with conn:`, which
    # commits on a clean exit and rolls back on exception.
    pool = _get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            yield cur


def _ensure_schema(cur):
    global _schema_ready
    if _schema_ready:
        return
    cur.execute("""
        CREATE TABLE IF NOT EXISTS page_view (
            id BIGSERIAL PRIMARY KEY,
            path TEXT NOT NULL,
            referrer TEXT,
            visitor_id TEXT NOT NULL,
            user_agent TEXT,
            lang TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_page_view_created_at ON page_view (created_at)")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS click_event (
            id BIGSERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            path TEXT NOT NULL,
            visitor_id TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_click_event_created_at ON click_event (created_at)")
    _schema_ready = True


def _wrap_db_errors(exc):
    return AnalyticsUnavailable(f"Could not reach analytics database: {exc}")


def record_page_view(*, path, referrer, visitor_id, user_agent, lang):
    try:
        with _cursor() as cur:
            _ensure_schema(cur)
            cur.execute(
                "INSERT INTO page_view (path, referrer, visitor_id, user_agent, lang) "
                "VALUES (%s, %s, %s, %s, %s)",
                (path, referrer, visitor_id, user_agent, lang),
            )
    except (psycopg.OperationalError, psycopg.InterfaceError) as exc:
        raise _wrap_db_errors(exc) from exc


def record_click(*, name, path, visitor_id):
    try:
        with _cursor() as cur:
            _ensure_schema(cur)
            cur.execute(
                "INSERT INTO click_event (name, path, visitor_id) VALUES (%s, %s, %s)",
                (name, path, visitor_id),
            )
    except (psycopg.OperationalError, psycopg.InterfaceError) as exc:
        raise _wrap_db_errors(exc) from exc


def get_stats():
    try:
        with _cursor() as cur:
            _ensure_schema(cur)
            stats = {}

            cur.execute("SELECT COUNT(*), COUNT(DISTINCT visitor_id) FROM page_view")
            stats["total_views"], stats["total_visitors"] = cur.fetchone()

            cur.execute("""
                SELECT COUNT(*), COUNT(DISTINCT visitor_id) FROM page_view
                WHERE created_at >= now() - interval '7 days'
            """)
            stats["views_7d"], stats["visitors_7d"] = cur.fetchone()

            cur.execute("""
                SELECT COUNT(*), COUNT(DISTINCT visitor_id) FROM page_view
                WHERE created_at >= now() - interval '30 days'
            """)
            stats["views_30d"], stats["visitors_30d"] = cur.fetchone()

            cur.execute("""
                SELECT path, COUNT(*) AS views, COUNT(DISTINCT visitor_id) AS visitors
                FROM page_view
                GROUP BY path
                ORDER BY views DESC
                LIMIT 20
            """)
            stats["top_pages"] = [
                {"path": row[0], "views": row[1], "visitors": row[2]} for row in cur.fetchall()
            ]

            cur.execute("""
                SELECT name, COUNT(*) AS clicks
                FROM click_event
                GROUP BY name
                ORDER BY clicks DESC
                LIMIT 20
            """)
            stats["top_clicks"] = [{"name": row[0], "clicks": row[1]} for row in cur.fetchall()]

            cur.execute("""
                SELECT date_trunc('day', created_at)::date AS day,
                       COUNT(*), COUNT(DISTINCT visitor_id)
                FROM page_view
                WHERE created_at >= now() - interval '14 days'
                GROUP BY day
                ORDER BY day
            """)
            stats["daily"] = [
                {"date": row[0].isoformat(), "views": row[1], "visitors": row[2]}
                for row in cur.fetchall()
            ]

            cur.execute("""
                SELECT path, referrer, visitor_id, created_at
                FROM page_view
                ORDER BY created_at DESC
                LIMIT 25
            """)
            stats["recent_views"] = [
                {
                    "path": row[0],
                    "referrer": row[1],
                    "visitor_id": row[2][:8],
                    "created_at": row[3].isoformat(),
                }
                for row in cur.fetchall()
            ]

            return stats
    except (psycopg.OperationalError, psycopg.InterfaceError) as exc:
        raise _wrap_db_errors(exc) from exc
