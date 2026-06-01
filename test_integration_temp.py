import sys, os, asyncio, json
sys.path.insert(0, 'G:/mnt/yahoo_indicators')

print("=== Testing Full App Integration ===")

# Test 1: All imports work
print("\n1. Testing all imports:")
try:
    from storage.database import Database
    from data.provider import get_provider
    from indicators import CamarillaIndicator, VolumeSpikeIndicator
    from alert.notifier import Notifier
    from alert.poller import Poller
    from ui.theme import get_theme, glass_container, glass_card, border_all
    from ui.home_screen import build_home_screen
    from ui.alert_conditions_screen import build_alert_conditions_screen
    from ui.history_screen import build_history_screen
    from ui.settings_screen import build_settings_screen
    from ui.search_overlay import build_search_overlay
    print("   All imports: OK")
except Exception as e:
    print(f"   Import FAILED: {e}")
    import traceback; traceback.print_exc()

# Test 2: Settings loading
print("\n2. Testing settings:")
try:
    settings_path = 'G:/mnt/yahoo_indicators/settings.json'
    with open(settings_path) as f:
        settings = json.load(f)
    print(f"   Settings keys: {list(settings.keys())}")
except Exception as e:
    print(f"   Settings FAILED: {e}")

# Test 3: Database + Data provider integration
print("\n3. Testing DB + Provider integration:")
try:
    db = Database('G:/mnt/yahoo_indicators/test_integration.db')
    provider = get_provider("yahoo")

    # Create watchlist and add symbols
    wl_id = db.create_watchlist("Integration Test")
    db.set_active_watchlist(wl_id)
    db.add_symbol(wl_id, "AAPL", "Apple Inc.")

    # Fetch data for symbol
    data = asyncio.run(provider.get_camarilla_data("AAPL"))
    print(f"   Camarilla data for AAPL: {data is not None}")

    data = asyncio.run(provider.get_volume_data("AAPL"))
    print(f"   Volume data for AAPL: {data is not None}")

    db.close()
    os.remove('G:/mnt/yahoo_indicators/test_integration.db')
except Exception as e:
    print(f"   Integration FAILED: {e}")
    import traceback; traceback.print_exc()

# Test 4: Indicator + Data pipeline
print("\n4. Testing Indicator + Data pipeline:")
try:
    cam = CamarillaIndicator()
    data = {"high": 190.0, "low": 180.0, "close": 185.0, "current_price": 192.0, "symbol": "AAPL"}
    triggered, msg = cam.evaluate(data, cam.default_params)
    print(f"   Camarilla evaluate: triggered={triggered}, msg={msg[:50]}")

    vol = VolumeSpikeIndicator()
    data = {"current_volume": 50000000, "volume_history": [10000000]*8, "symbol": "AAPL"}
    triggered, msg = vol.evaluate(data, vol.default_params)
    print(f"   Volume spike evaluate: triggered={triggered}, msg={msg[:50]}")
except Exception as e:
    print(f"   Pipeline FAILED: {e}")
    import traceback; traceback.print_exc()

# Test 5: Poller initialization
print("\n5. Testing Poller:")
try:
    db = Database('G:/mnt/yahoo_indicators/test_poller.db')
    wl_id = db.create_watchlist("Poller Test")
    db.set_active_watchlist(wl_id)
    db.add_symbol(wl_id, "AAPL")

    provider = get_provider("yahoo")
    notifier = Notifier("Alertra")
    indicators = [CamarillaIndicator(), VolumeSpikeIndicator()]

    poller = Poller(
        db=db, provider=provider, notifier=notifier,
        indicators=indicators, polling_interval=300, cooldown_seconds=300
    )
    print(f"   Poller created: interval={poller.polling_interval}s")

    # Test single poll cycle
    alerts = asyncio.run(poller._poll_cycle())
    print(f"   Poll cycle completed: {len(alerts)} alerts")

    db.close()
    os.remove('G:/mnt/yahoo_indicators/test_poller.db')
except Exception as e:
    print(f"   Poller FAILED: {e}")
    import traceback; traceback.print_exc()

# Test 6: Theme system
print("\n6. Testing Theme system:")
try:
    for accent in ["teal", "blue", "purple", "orange"]:
        for mode in ["dark", "light"]:
            theme = get_theme(accent, mode)
            print(f"   Theme({accent}, {mode}): OK")
except Exception as e:
    print(f"   Theme FAILED: {e}")

print("\n=== ALL INTEGRATION TESTS COMPLETE ===")
