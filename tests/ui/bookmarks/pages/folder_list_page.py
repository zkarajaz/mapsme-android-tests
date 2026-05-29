"""
pages/folder_list_page.py
=========================
Re-export: FolderListPage = FavoritesPage.
Необходим для совместимости с импортами в тест-файлах.
"""
from pages.favorites_page import FavoritesPage, FolderPage

FolderListPage = FavoritesPage

__all__ = ["FolderListPage", "FolderPage"]
