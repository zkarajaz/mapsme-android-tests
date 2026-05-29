"""utils/helpers.py"""
import re, locale, logging, time
from typing import List
from datetime import datetime

logger = logging.getLogger(__name__)

def unique_name(prefix="Test") -> str:
    return f"{prefix}_{datetime.now().strftime('%H%M%S')}"

def generate_string(length: int, char="А") -> str:
    return char * length

def is_sorted_alphabetically(names: List[str]) -> bool:
    try:
        locale.setlocale(locale.LC_COLLATE, "")
    except Exception:
        pass
    for i in range(len(names) - 1):
        if locale.strcoll(names[i], names[i + 1]) > 0:
            return False
    return True

def is_sorted_by_distance(distances: List[str]) -> bool:
    def parse(d):
        m = re.search(r"([\d.]+)\s*(km|м|m)", d.lower().replace(",", "."))
        if not m:
            return float("inf")
        v = float(m.group(1))
        return v * 1000 if m.group(2) == "km" else v
    parsed = [parse(d) for d in distances]
    return all(parsed[i] <= parsed[i+1] for i in range(len(parsed)-1))
