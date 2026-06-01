import sys, os
sys.path.insert(0, 'G:/mnt/yahoo_indicators')
import flet as ft
from storage.database import Database
from data.provider import get_provider
from indicators import CamarillaIndicator, VolumeSpikeIndicator
from ui.theme import get_theme, glass_container, glass_card, border_all

# Create temp db with test data
db_path = 'G:/mnt/yahoo_indicators/test_ui_temp.db'
db = Database(db_path)

# Set up test data
wl_id = db.create_watchlist("Test WL")
db.set_active_watchlist(wl_id)
db.add_symbol(wl_id, "AAPL", "Apple Inc.")
db.add_symbol(wl_id, "MSFT", "Microsoft Corp.")
db.save_alert("AAPL", "camarilla", 185.50, "Test alert message")
db.set_setting("polling_interval_seconds", "300")
db.set_setting("cooldown_seconds", "300")

provider = get_provider("yahoo")
indicators = [CamarillaIndicator(), VolumeSpikeIndicator()]

print("=== Testing UI Screen Builds ===")

# Test 1: theme helpers
print("\n1. Theme helpers:")
try:
    theme = get_theme("teal", "dark")
    print(f"   get_theme('teal', 'dark'): OK")
except Exception as e:
    print(f"   get_theme FAILED: {e}")

try:
    theme = get_theme("blue", "light")
    print(f"   get_theme('blue', 'light'): OK")
except Exception as e:
    print(f"   get_theme FAILED: {e}")

try:
    c = glass_container(ft.Text("test"))
    print(f"   glass_container: OK")
except Exception as e:
    print(f"   glass_container FAILED: {e}")

try:
    c = glass_card(ft.Text("test"))
    print(f"   glass_card: OK")
except Exception as e:
    print(f"   glass_card FAILED: {e}")

try:
    b = border_all(1, ft.Colors.WHITE)
    print(f"   border_all: OK")
except Exception as e:
    print(f"   border_all FAILED: {e}")

# Test 2: Screen function imports
print("\n2. Screen imports:")
try:
    from ui.home_screen import build_home_screen
    print(f"   home_screen: OK")
except Exception as e:
    print(f"   home_screen FAILED: {e}")

try:
    from ui.alert_conditions_screen import build_alert_conditions_screen
    print(f"   alert_conditions_screen: OK")
except Exception as e:
    print(f"   alert_conditions_screen FAILED: {e}")

try:
    from ui.history_screen import build_history_screen
    print(f"   history_screen: OK")
except Exception as e:
    print(f"   history_screen FAILED: {e}")

try:
    from ui.settings_screen import build_settings_screen
    print(f"   settings_screen: OK")
except Exception as e:
    print(f"   settings_screen FAILED: {e}")

try:
    from ui.search_overlay import build_search_overlay
    print(f"   search_overlay: OK")
except Exception as e:
    print(f"   search_overlay FAILED: {e}")

# Test 3: __init__ imports
print("\n3. Package imports:")
try:
    from ui import build_home_screen, build_alert_conditions_screen, build_history_screen, build_settings_screen, build_search_overlay
    print(f"   All screen imports from ui package: OK")
except Exception as e:
    print(f"   Package import FAILED: {e}")

# Test 4: function signatures
print("\n4. Function signatures:")
import inspect

sig = inspect.signature(build_home_screen)
params = list(sig.parameters.keys())
print(f"   build_home_screen params: {params}")

sig = inspect.signature(build_alert_conditions_screen)
params = list(sig.parameters.keys())
print(f"   build_alert_conditions_screen params: {params}")

sig = inspect.signature(build_history_screen)
params = list(sig.parameters.keys())
print(f"   build_history_screen params: {params}")

sig = inspect.signature(build_settings_screen)
params = list(sig.parameters.keys())
print(f"   build_settings_screen params: {params}")

sig = inspect.signature(build_search_overlay)
params = list(sig.parameters.keys())
print(f"   build_search_overlay params: {params}")

# Test 5: notifier
print("\n5. Notifier:")
try:
    from alert.notifier import Notifier
    n = Notifier("Alertra")
    n.configure(enabled=True, sound_enabled=False)
    result = n.send("Test", "Test message")
    print(f"   Notifier send: {result}")
except Exception as e:
    print(f"   Notifier FAILED: {e}")

# Cleanup
db.close()
os.remove(db_path)
print("\n=== ALL UI TESTS COMPLETE ===")
