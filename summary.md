# 📊 **Project Summary: Cross-Platform Stock Alert System (Alertra)**

## **1. Executive Summary**
**Alertra** is a lightweight, alert-only stock monitoring application for **Windows (desktop)** and **Android (mobile)**. It periodically polls user-defined watchlists and sends local push notifications when technical conditions (Camarilla breakouts, volume spikes) are met. The system prioritises **accuracy**, **reliability**, and **extensibility**, using professional-grade data APIs (Polygon.io / Twelve Data). It features a **liquid glass UI** with smooth animations, offline-capable search, and plugin architecture for adding future indicators.

---

## **2. Core Features (MVP)**

| Category | Features |
|----------|----------|
| **Watchlist** | Add/remove symbols by name or symbol; multiple watchlists; drag‑and‑drop reorder; import/export (JSON/CSV). |
| **Search** | Auto‑complete search with offline symbol cache; fuzzy matching; add directly from results. |
| **Alert Conditions** | Camarilla H4/L4 breakout (bullish: price > H4; bearish: price < L4). Volume spike (current volume > multiplier × SMA8 of volume). |
| **Polling** | User‑adjustable interval (30s–10min); smart polling (market hours, volatility, battery). |
| **Notifications** | Native Windows Toast / Android system notification; custom sounds; priority levels; snooze; cooldown per symbol per condition (default 5 min). |
| **History** | Alert log (timestamp, symbol, condition, price); export, pin, clear. |
| **Settings** | Polling interval, cooldown, volume multiplier, theme (dark/light/system), notification sound, silent schedule. |
| **Data Provider** | Professional API (Polygon.io / Twelve Data) with user‑entered API key; fallback to Yahoo Finance. |
| **Extensibility** | Plugin‑based indicators – add new conditions (RSI, MACD, Supertrend) without core changes. |

---

## **3. Technical Architecture**

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.11+ |
| **UI Framework** | Flet (Flutter for Python) – single codebase for Windows and Android, native performance, glass effects. |
| **Data Provider** | Polygon.io (primary), Twelve Data (alternative), Yahoo Finance (fallback). User configures API key. |
| **Local Database** | SQLite (`sqlite3`) – stores watchlists, alert history, settings, cooldown. |
| **Notifications** | `plyer` (cross‑platform wrapper) + platform‑specific enhancements. |
| **Background Polling** | `asyncio` + Android `WorkManager` (via Flet platform channel) for background execution. |
| **Build & Distribution** | Windows: `.exe` via `flet pack`. Android: `.apk` via `flet build apk`. |

### **Database Schema (SQLite)**
```sql
watchlists(id, name, is_active, created_at)
watchlist_items(id, watchlist_id, symbol, display_name, sort_order)
alerts(id, symbol, condition, price, message, triggered_at, is_read)
settings(key, value)
cooldown(symbol, condition, last_trigger)
```

### **Polling Loop (Async)**
- Runs every `polling_interval` seconds.
- Fetches only required data (previous day’s high/low/close, last 8 volumes, current price).
- Caches data to minimise API calls.
- Evaluates enabled indicators; triggers notification if condition met and cooldown allows.
- Respects rate limits with exponential backoff.

---

## **4. UI/UX Design – Liquid Glass & Animations**

### **Visual Style**
- Frosted glass background (blur + semi‑transparency) with gradient.
- Dark theme default, light theme option, system theme detection.
- User‑selectable accent colour (teal, blue, purple, orange).
- Rounded cards (24px), soft shadows, subtle border glow.

### **Screens & Navigation**
1. **Home (Watchlist)** – symbol cards, search bar, alert badge, floating add button.
2. **Alert Conditions** – toggle indicators, adjust parameters, test notification.
3. **Alerts History** – timeline of triggered alerts (grouped by date), export.
4. **Settings** – polling, cooldown, notifications, data provider, theme, about.
5. **Search Overlay** – modal with auto‑complete, recent searches, one‑tap add.

### **Animations**
- Page transition: slide + fade (300ms).
- Card entry: staggered vertical slide.
- Button tap: scale down + ripple.
- Pull‑to‑refresh: spinner + haptic.
- Alert arrival: card flash, sound, slight bounce.
- Switch toggle: spring animation.

---

## **5. Extensibility – Adding New Indicators**

- Each indicator is a separate class in `indicators/` folder.
- Implements `evaluate(data, params) -> (triggered, message)`.
- Registered automatically; user can enable/disable in Settings.
- Example: RSI, Supertrend, MACD, Bollinger Bands, ATR.

---

## **6. Data Accuracy & Reliability**

- **Primary choice:** Polygon.io or Twelve Data – professional accuracy, WebSocket, paid.
- **Fallback:** Yahoo Finance (free, adequate for learning / initial testing).
- **Sanity checks:** Ignore price moves >50% unless confirmed by consecutive candle.
- **Cache & rate limit handling:** Exponential backoff, deduplication.

---

## **7. Build & Distribution**

| Platform | Build Command | Output |
|----------|---------------|--------|
| Windows | `flet pack main.py --name Alertra --add-data "assets;assets"` | `Alertra.exe` installer |
| Android | `flet build apk` | `alertra.apk` (sign with keystore) |

---

## **8. Success Metrics**

- ✅ App runs on Windows 10/11 and Android 10+.
- ✅ Users can add symbols via search with auto‑complete.
- ✅ Alerts trigger correctly for Camarilla and volume spike (tested with historical data).
- ✅ Notifications appear natively with sound.
- ✅ Cooldown prevents duplicates.
- ✅ UI is liquid glass, animations smooth, no lag.
- ✅ Polling respects interval and handles rate limits.
- ✅ New indicators can be added without core changes.

---

## **9. Timeline Estimate (3‑4 weeks part‑time)**

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| 1: Core logic & data provider | 5 days | Data fetcher, indicator engine, polling loop, SQLite. |
| 2: Basic UI (Flet) | 5 days | Watchlist, add/remove, settings, alert history. |
| 3: Notifications & background | 4 days | Cross‑platform notifications, cooldown, background polling. |
| 4: UI polish (glass, animations) | 4 days | All screens, transitions, dark/light theme. |
| 5: Build & test | 2 days | Windows `.exe`, Android `.apk`, user testing. |

---

