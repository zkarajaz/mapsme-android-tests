"""utils/db_utils.py — заглушка (нет root-доступа к SQLite)"""
import logging
logger = logging.getLogger(__name__)


class BookmarksDB:
    """Заглушка. Реальная работа с БД требует root-доступа к эмулятору."""

    def pull_db(self) -> str:
        logger.warning("BookmarksDB.pull_db(): нет root-доступа, пропускаем")
        return ""

    def get_bookmark_by_name(self, name: str):
        return None

    def get_all_bookmarks(self):
        return []

    def cleanup(self):
        pass
