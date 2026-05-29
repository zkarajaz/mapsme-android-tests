"""config/settings.py"""
import os
from typing import Dict, Any

PLATFORM    = "Android"
APPIUM_HOST = "http://127.0.0.1:4723"

class Timeouts:
    IMPLICIT        = 0     # Отключаем — используем явные ожидания
    EXPLICIT        = 20
    ANIMATION       = 2
    SNACK_DISAPPEAR = 8
    SYNC_TIMEOUT    = 30
    SWIPE_DURATION  = 800

class BookmarkColors:
    DEFAULT = "#687AFF"

class FieldLimits:
    BOOKMARK_NAME_MAX        = 60
    BOOKMARK_DESCRIPTION_MAX = 4000
    FOLDER_NAME_MAX          = 30

class TestData:
    DEFAULT_FOLDER_NAME = "My Places"
    SEARCH_OBJECT_NAME  = "Basketball"

_APP_PATH = os.getenv("APP_PATH", r"C:\Users\Victoria\Downloads\mapsme.apk")

ANDROID_CAPABILITIES: Dict[str, Any] = {
    "platformName":            "Android",
    "appium:automationName":   "UiAutomator2",
    "appium:deviceName":       "emulator-5554",
    "appium:app":              _APP_PATH,
    "appium:appPackage":       "com.mapswithme.maps.pro",
    "appium:appActivity":      "com.mapswithme.maps.pro.DefaultIcon",
    "appium:noReset":          True,
    "appium:fullReset":        False,
    "appium:newCommandTimeout": 120,
    "appium:autoGrantPermissions": True,
    "appium:noSign":           True,
    "appium:adbExecTimeout":   60000,
    "appium:uiautomator2ServerLaunchTimeout": 60000,
    "appium:androidDeviceReadyTimeout": 90,
}

def get_capabilities() -> Dict[str, Any]:
    return ANDROID_CAPABILITIES
