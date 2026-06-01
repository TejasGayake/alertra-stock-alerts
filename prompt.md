# 📱 **Cross‑Platform Stock Alert System – Complete Project Specification & Implementation Prompt**

## **Project Name:** *Alertra* (or your preferred name)  
**Tagline:** *Precision alerts for every market move.*  
**Platforms:** Windows (desktop) + Android (mobile)  
**UI Style:** Liquid glass (blur, translucency, smooth animations)  
**Primary Focus:** Accuracy, reliability, and extensibility. Willing to pay for data.

---

## 🎯 **1. Project Overview**

Build a **lightweight, alert‑only** stock monitoring application that periodically checks user‑defined watchlists and sends **local notifications** when technical conditions are met.  
**No continuous live feed** – uses periodic polling (every 1–5 minutes) to respect rate limits and save battery/data.  
**Data source:** Professional, high‑accuracy API (e.g., Polygon.io, Twelve Data, or Dhan_TradeHull).  
**Target users:** Retail traders who want to be alerted of key price/volume events without staring at screens.

---

## 📋 **2. Feature List – Complete (Including Suggested Enhancements)**

### **2.1 Core Features (MVP)**
| Feature | Description |
|---------|-------------|
| **Watchlist Management** | Add/remove symbols (by symbol or name). Multiple watchlists, reorder, import/export (JSON/CSV). |
| **Search** | Auto‑complete search with offline cache (symbol master). Fuzzy matching. Add directly from search results. |
| **Alert Conditions** | – Camarilla H4/L4 breakout (bullish: price > H4; bearish: price < L4)<br>– Volume spike: current volume > multiplier × SMA8(volume) (multiplier default 3, adjustable 2–5) |
| **Extensible Indicators** | Plugin architecture for future indicators (RSI, MACD, Supertrend, etc.). User can enable/disable per indicator. |
| **Polling** | Adjustable interval (30 sec – 10 min). Smart polling: market hours vs. closed, volatility, battery, network type. |
| **Local Notifications** | Windows Toast, Android System Notification. Sound (user customizable), priority levels, snooze. |
| **Cooldown** | Per symbol per condition (default 5 min, user adjustable). Prevents duplicate spam. |
| **Alert History** | Log of all triggered alerts (timestamp, symbol, condition, price). Clear, export, pin favorites. |
| **Settings** | Polling interval, cooldown, volume multiplier, theme (dark/light/system), notification sound, silent mode schedule. |
| **Data Provider** | Professional API (Polygon.io / Twelve Data / Dhan_TradeHull) – user enters API key. Fallback to Yahoo Finance (optional). |
| **Cross‑Platform** | Windows `.exe` and Android `.apk` from same codebase (using Flet / Flutter). |

### **2.2 Advanced / Future Features (for later releases)**
- Multiple watchlist groups (e.g., “Swing”, “Earnings”, “Crypto”).
- Email / webhook alerts (Telegram, Discord).
- Cloud sync (optional, via Firebase/Supabase).
- Widget / Live Tile (Android home screen, Windows Start menu).
- Smart polling (adaptive based on volatility, market hours, battery).
- Demo mode (replay historical data to test alerts).
- Crash reporting & auto‑update.

---

## 🎨 **3. UI/UX Specification – Liquid Glass + Animations**

### **3.1 Visual Style**
- **Background:** Frosted glass effect – semi‑transparent with blur and subtle gradient. Use platform‑specific blur where available, fallback to semi‑transparent layers.
- **Theme:** Dark by default, Light alternative. System theme detection.
- **Accent color:** User‑selectable (teal, blue, purple, orange).
- **Cards:** Rounded corners (24px), soft multi‑layered shadows, subtle border glow.

### **3.2 Animations & Micro‑interactions**
| Element | Animation |
|---------|-----------|
| Page transition | Slide + fade (300ms ease‑in‑out) |
| Card entry | Staggered vertical slide from bottom (200ms delay per card) |
| Button tap | Scale down to 0.95 with ripple effect (100ms) |
| Pull‑to‑refresh | Animated loading spinner + haptic feedback (mobile) |
| Alert arrival | Card flash (yellow pulse) + sound + slight bounce |
| Switch toggle | Spring animation (mass 1, stiffness 200) |
| Number change (LTP) | Smooth count‑up or flip‑digit |
| Empty state | Lottie animation (e.g., “no alerts” illustration) |

### **3.3 Screen Layouts**

#### **A. Home / Dashboard (Watchlist)**
- Header: Search bar, alert count badge (🔔 with number), settings gear.
- Watchlist selector (dropdown – multiple watchlists).
- List of symbols as cards:
  - Symbol (large), current price, change % (colored), volume.
  - Alert icon (⚠️) if any active alert for that symbol.
- Floating Action Button (+) to add symbol.
- Swipe left on card → delete; swipe right → edit alert conditions for that symbol.

#### **B. Alert Conditions Screen**
- List of all available indicators (Camarilla, Volume Spike, etc.) with toggle switch.
- Tapping an indicator opens parameter editor (e.g., volume multiplier, SMA period).
- “Test Alert” button – simulates condition met for current symbol (sends test notification).
- Cooldown setting (global or per condition).

#### **C. Alerts History Screen**
- Two tabs: **Active** (last 24h) and **All**.
- Grouped by date. Each row: time, symbol, condition, price.
- Swipe to delete or mark as read.
- Share / export as CSV or JSON.

#### **D. Settings Screen**
- **General** – Polling interval (slider), cooldown, theme.
- **Indicators** – Enable/disable, adjust thresholds.
- **Notifications** – Sound picker, silent mode schedule, test notification.
- **Data** – API key configuration, clear cache, export/import all data.
- **About** – Version, license, privacy policy, contact.

#### **E. Search Overlay**
- Modal overlay with search input.
- Suggestions appear as you type (symbol, name, exchange).
- Recent searches section.
- One‑tap add to current watchlist.

---

## 🛠️ **4. Technical Architecture**

### **4.1 Technology Stack**
| Layer | Choice | Reason |
|-------|--------|--------|
| **Language** | Python 3.11+ | Your expertise, cross‑platform support via Flet |
| **Framework** | Flet (Flutter for Python) | One codebase for Windows + Android; native performance; rich UI capabilities |
| **Data Provider** | Polygon.io (or Twelve Data) | Professional accuracy, WebSocket, REST; paid but reliable |
| **Local Database** | SQLite (via `sqlite3` or `drift`) | Lightweight, no server, cross‑platform |
| **Notifications** | `plyer` (cross‑platform wrapper) + platform‑specific enhancements | Simplifies Windows Toast and Android notifications |
| **Background Polling** | `asyncio` + `WorkManager` (Android via Flet platform channel) | Allows periodic checks even when app closed |
| **Build** | Flet pack (Windows) + Flet build apk (Android) | Simple distribution |

### **4.2 Data Provider Integration**
- User provides API key (stored locally, encrypted).
- For each symbol, fetch required data:
  - **Camarilla:** previous day’s high, low, close; current price (last candle close).
  - **Volume spike:** last 8 volume values (5‑minute candles) to compute SMA8; current volume.
- Cache fetched data to minimise API calls.
- Handle rate limits with exponential backoff.

### **4.3 Database Schema (SQLite)**
```sql
-- Watchlists
CREATE TABLE watchlists (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 0,
    created_at TIMESTAMP
);

-- Watchlist items
CREATE TABLE watchlist_items (
    id INTEGER PRIMARY KEY,
    watchlist_id INTEGER,
    symbol TEXT NOT NULL,
    display_name TEXT,
    sort_order INTEGER,
    FOREIGN KEY(watchlist_id) REFERENCES watchlists(id)
);

-- Alert history
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY,
    symbol TEXT NOT NULL,
    condition TEXT NOT NULL,
    price REAL,
    message TEXT,
    triggered_at TIMESTAMP,
    is_read BOOLEAN DEFAULT 0
);

-- Settings (key‑value)
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Cooldown tracking (can also be in‑memory)
CREATE TABLE cooldown (
    symbol TEXT,
    condition TEXT,
    last_trigger INTEGER,
    PRIMARY KEY (symbol, condition)
);
```

### **4.4 Polling Loop (Async)**
```python
async def polling_loop(page):
    while True:
        if not is_within_schedule() and not force_update:
            await asyncio.sleep(60)
            continue
        watchlist = await get_active_watchlist_symbols()
        for symbol in watchlist:
            data = await fetch_required_data(symbol)  # from API, with caching
            for indicator in enabled_indicators:
                if indicator.evaluate(data):
                    if not in_cooldown(symbol, indicator.name):
                        await send_notification(...)
                        await save_alert(...)
                        update_cooldown(...)
                        await asyncio.sleep(0.5)  # small delay between notifications
        await asyncio.sleep(polling_interval_seconds)
```

### **4.5 Extensible Indicator Registry**
Each indicator is a class implementing:
```python
class Indicator:
    name: str
    description: str
    default_params: dict
    cooldown_key(symbol) -> str
    evaluate(data: dict, params: dict) -> Tuple[bool, str]
```

Indicators are discovered automatically from a `indicators/` folder. User can enable/disable in Settings.

### **4.6 Build & Distribution**
- **Windows:** `flet pack main.py --name Alertra --add-data "assets;assets" --icon assets/icon.ico`
- **Android:** `flet build apk` → sign with your keystore → produce `.apk`.
- **Optional:** Publish to Microsoft Store / Google Play.

---

## ✅ **5. Success Criteria**

- [ ] App runs on Windows 10/11 and Android 10+.
- [ ] User can add symbols via search with auto‑complete.
- [ ] Alerts trigger correctly for Camarilla H4/L4 and volume spike (test with known historical data).
- [ ] Notifications appear as native toasts with sound.
- [ ] Cooldown prevents duplicate alerts within set time.
- [ ] UI is glass‑morphism, animations smooth, no lag.
- [ ] Polling respects user‑set interval and handles API rate limits gracefully.
- [ ] Future indicators can be added without modifying core engine.

---

## 📄 **6. Detailed Implementation Prompt (For AI / Developer)**

Use the following prompt to generate the **complete working application** code.

---

> **Role:** You are a senior full‑stack developer expert in Python, Flet, cross‑platform development, and financial APIs.
> 
> **Task:** Build the cross‑platform stock alert system as specified above. Use the technology stack described. Do not skip any of the core features. Implement the liquid glass UI using semi‑transparent containers and shadows (Flet supports `blur` and `gradient`). Use the `plyer` library for cross‑platform notifications. Use `yfinance` initially as a placeholder data provider, but include a configuration for switching to Polygon.io (i.e., user can enter an API key and choose provider). Implement all database schemas exactly as described.
> 
> **Deliverables:**
> 1. Complete Python source code organized into modules (`ui/`, `data/`, `indicators/`, `alert/`, `storage/`).
> 2. `requirements.txt` with all dependencies.
> 3. `README.md` with setup and build instructions for Windows and Android.
> 4. Assets (default icon, sound files, Lottie animation JSON) placeholders.
> 5. A sample `settings.json` for default configuration.
> 
> **Constraints:** The code must be self‑contained, run without external servers, and be easily modifiable for adding new indicators. Ensure proper error handling and logging. Use `asyncio` for polling loop. Make the UI responsive to different screen sizes.
> 
> **Start coding now.**

---
