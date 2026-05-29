"""utils/network_utils.py"""
import subprocess, time, logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)
ADB = r"C:\Users\Victoria\AppData\Local\Android\Sdk\platform-tools\adb.exe"

class NetworkUtils:
    @staticmethod
    def _adb(cmd):
        try:
            return subprocess.run(f'"{ADB}" {cmd}', shell=True,
                                  capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:
            return ""

    @classmethod
    def go_offline(cls, driver=None):
        cls._adb("shell svc wifi disable")
        cls._adb("shell svc data disable")
        time.sleep(3)

    @classmethod
    def go_online(cls, driver=None):
        cls._adb("shell svc wifi enable")
        cls._adb("shell svc data enable")
        time.sleep(5)

@contextmanager
def offline_mode(driver=None):
    try:
        NetworkUtils.go_offline(driver)
        yield
    finally:
        NetworkUtils.go_online(driver)
