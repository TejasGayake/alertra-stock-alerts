# Alertra - Project Log

## Project Overview
- **Name:** Alertra
- **Tagline:** Precision alerts for every market move.
- **Type:** Cross-platform stock alert system (alert-only, no live feed)
- **Platforms:** Windows (desktop) + Android (mobile)
- **UI Style:** Liquid glass (blur, translucency, smooth animations)
- **Target Users:** Retail traders who want alerts on key price/volume events without staring at screens

---

## Tech Stack
| Layer | Choice |
|-------|--------|
| Language | Python 3.11+ |
| UI Framework | Flet (Flutter for Python) - single codebase for Windows + Android |
| Data Provider | Polygon.io (primary), Twelve Data (alt), Yahoo Finance (fallback) |
| Local Database | SQLite |
| Notifications | `plyer` (cross-platform) + platform-specific enhancements |
| Background Polling | `asyncio` + Android `WorkManager` (via Flet platform channel) |
| Build | `flet pack` (Windows .exe), `flet build apk` (Android .apk) |

---

## Core Features (MVP)
1. **Watchlist Management** - Add/remove symbols, multiple watchlists, reorder, import/export (JSON/CSV)
2. **Search** - Auto-complete with offline symbol cache, fuzzy matching
3. **Alert Conditions:**
   - Camarilla H4/L4 breakout (bullish: price > H4, bearish: price < L4)
   - Volume spike: current volume > multiplier x SMA8(volume) (default multiplier: 3, adjustable 2-5)
4. **Extensible Indicators** - Plugin architecture for future indicators (RSI, MACD, Supertrend, etc.)
5. **Polling** - Adjustable interval (30s - 10min), smart polling based on market hours/battery/volatility
6. **Local Notifications** - Windows Toast / Android system notification, custom sounds, priority, snooze
7. **Cooldown** - Per symbol per condition (default 5 min), prevents duplicate alerts
8. **Alert History** - Log of all triggered alerts (timestamp, symbol, condition, price), export, clear
9. **Settings** - Polling interval, cooldown, volume multiplier, theme, notification sound, silent mode schedule
10. **Data Provider** - User enters API key, supports Polygon.io / Twelve Data / Yahoo Finance fallback

---

## Advanced / Future Features
- Multiple watchlist groups (Swing, Earnings, Crypto)
- Email / webhook alerts (Telegram, Discord)
- Cloud sync (Firebase/Supabase)
- Widget / Live Tile (Android home screen, Windows Start menu)
- Demo mode (replay historical data to test alerts)
- Crash reporting & auto-update

---

## Database Schema (SQLite)
```sql
watchlists(id, name, is_active, created_at)
watchlist_items(id, watchlist_id, symbol, display_name, sort_order)
alerts(id, symbol, condition, price, message, triggered_at, is_read)
settings(key, value)
cooldown(symbol, condition, last_trigger)
```

---

## UI/UX Design
### Visual Style
- Frosted glass background (blur + semi-transparency) with gradient
- Dark theme default, light theme option, system theme detection
- User-selectable accent color (teal, blue, purple, orange)
- Rounded cards (24px), soft shadows, subtle border glow

### Screens
1. **Home (Watchlist)** - symbol cards, search bar, alert badge, floating add button
2. **Alert Conditions** - toggle indicators, adjust parameters, test notification
3. **Alerts History** - timeline grouped by date, export
4. **Settings** - polling, cooldown, notifications, data provider, theme, about
5. **Search Overlay** - modal with auto-complete, recent searches, one-tap add

### Animations
- Page transition: slide + fade (300ms)
- Card entry: staggered vertical slide (200ms delay per card)
- Button tap: scale down to 0.95 + ripple (100ms)
- Pull-to-refresh: spinner + haptic feedback
- Alert arrival: card flash (yellow pulse) + sound + bounce
- Switch toggle: spring animation
- Number change (LTP): smooth count-up or flip-digit
- Empty state: Lottie animation

---

## Project Structure (Planned)
```
main.py
requirements.txt
settings.json
ui/           - UI screens and components
data/         - Data provider integration (API fetchers)
indicators/   - Plugin-based indicator classes
alert/        - Notification and alert logic
storage/      - SQLite database layer
assets/       - Icons, sounds, Lottie animations
```

---

## Indicator Plugin Architecture
Each indicator is a class in `indicators/` implementing:
```python
class Indicator:
    name: str
    description: str
    default_params: dict
    cooldown_key(symbol) -> str
    evaluate(data: dict, params: dict) -> Tuple[bool, str]
```
Indicators auto-discovered from `indicators/` folder. User enable/disable in Settings.

---

## Polling Loop Logic
```
1. Check schedule (market hours, user settings)
2. Get active watchlist symbols
3. For each symbol:
   - Fetch required data (with caching)
   - For each enabled indicator:
     - Evaluate condition
     - If triggered and not in cooldown -> send notification, save alert, update cooldown
4. Sleep for polling_interval_seconds
```
- Handles rate limits with exponential backoff
- Sanity checks: ignore price moves >50% unless confirmed

---

## Build & Distribution
| Platform | Command | Output |
|----------|---------|--------|
| Windows | `flet pack main.py --name Alertra --add-data "assets;assets" --icon assets/icon.ico` | Alertra.exe |
| Android | `flet build apk` | alertra.apk (sign with keystore) |

---

## Success Criteria
- [ ] Runs on Windows 10/11 and Android 10+
- [ ] Add symbols via search with auto-complete
- [ ] Alerts trigger correctly for Camarilla and volume spike
- [ ] Native notifications with sound
- [ ] Cooldown prevents duplicates
- [ ] Liquid glass UI, smooth animations, no lag
- [ ] Polling respects interval, handles rate limits
- [ ] New indicators addable without core changes

---

## Timeline Estimate (3-4 weeks part-time)
| Phase | Duration | Deliverables |
|-------|----------|-------------|
| 1: Core logic & data provider | 5 days | Data fetcher, indicator engine, polling loop, SQLite |
| 2: Basic UI (Flet) | 5 days | Watchlist, add/remove, settings, alert history |
| 3: Notifications & background | 4 days | Cross-platform notifications, cooldown, background polling |
| 4: UI polish (glass, animations) | 4 days | All screens, transitions, dark/light theme |
| 5: Build & test | 2 days | Windows .exe, Android .apk, user testing |

---

## Git Setup Notes
- User wants to upload project to GitHub
- Create repo if not exists, commit all changes
- No co-author on commits

## Development Notes
- **Use multiple agents in parallel** - spawn multiple agents to do different tasks simultaneously for faster execution

---

## Implementation Status (as of 2026-06-01)

### Completed Files
| File | Status | Description |
|------|--------|-------------|
| `main.py` | Done | Entry point, AlertraApp class, wires all components |
| `settings.json` | Done | Default app settings |
| `requirements.txt` | Done | Dependencies: flet, yfinance, plyer, requests |
| `storage/database.py` | Done | SQLite Database class with all CRUD operations |
| `data/provider.py` | Done | Abstract DataProvider base + factory |
| `data/yahoo_provider.py` | Done | YahooDataProvider with caching (60s price, 300s historical) |
| `indicators/base.py` | Done | Abstract Indicator base class |
| `indicators/camarilla.py` | Done | Camarilla H4/L4 breakout detector |
| `indicators/volume_spike.py` | Done | Volume spike detector (SMA-based) |
| `indicators/__init__.py` | Done | Exports all indicators |
| `alert/notifier.py` | Done | Cross-platform notifications via plyer |
| `alert/poller.py` | Done | Async polling loop with cooldown |
| `ui/theme.py` | Done | Glass-morphism theme, colors, containers |
| `ui/home_screen.py` | Done | Watchlist dashboard with symbol cards |
| `ui/alert_conditions_screen.py` | Done | Indicator toggle and parameter editor |
| `ui/history_screen.py` | Done | Alert history with tabs |
| `ui/settings_screen.py` | Done | All settings (polling, theme, notifications, data) |
| `ui/search_overlay.py` | Done | Search modal with autocomplete |

### Known Issues
- Camarilla indicator expects `symbol` in data - fixed by adding it in poller
- Volume spike expects `volume_history` key - fixed by mapping from `volumes` in poller
