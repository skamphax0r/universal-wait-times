# ⚡ Universal Parks Wait Times Display Box

A retro smart-clock display box and live park wait times board for Universal Parks worldwide, featuring themes inspired by **The Wizarding World of Harry Potter**, **Marvel Super Hero Island (MCU)**, and **Super Nintendo World (Mario)**.

Designed for Raspberry Pi kiosks, desk displays, home dashboards, and Proxmox LXC containers.

---

## ✨ Features

- **⚡ Multiple Immersive Themes**:
  - **⚡ Wizarding World (Harry Potter)**: Aged parchment, Hogwarts gold, Diagon Alley & Hogsmeade aesthetics.
  - **🛡️ Marvel Super Hero Island (MCU)**: Stark Arc Reactor cyan & crimson red, angular tech HUD, comic halftone dots.
  - **🍄 Super Nintendo World (Mario)**: 8-bit arcade fonts, Question Block gold, Mario red & Warp Pipe green.
  - **🌐 Classic Universal Studios**: Iconic Universal globe blue & gold cinematic art deco finish.
- **📦 Smart Clock Display (Box Mode)**:
  - Hardware chassis simulation with tactile controls (◀ Prev, ❚❚ Pause/Play, ▶ Next, ★ Favorite).
  - Continuous countdown progress bar cycling through open attractions.
  - Giant LED wait time digits and standby status indicator.
- **📋 Full Park Tip Board (Board Mode)**:
  - Land-by-land breakdown with instant search and filtering (*Open Only*, *Favorites Only*, *All Rides*).
- **⏱️ Configurable Live Clock**:
  - Live clock header defaulting to **Central Standard Time (CST/CDT)**.
  - One-click timezone switcher (CST, EST, MST, PST, JST, Park Time, Device Time).
  - Saved in browser `localStorage`.
- **🎡 Supported Parks**:
  - Universal's Islands of Adventure
  - Universal Studios Florida
  - Universal Studios Hollywood
  - Universal Studios Japan
  - Universal's Epic Universe
  - Universal's Volcano Bay
- **⚡ Lightweight High-Performance Backend**:
  - Python standard library server (zero external pip dependencies).
  - 60-second caching proxy to `queue-times.com`.
  - Fallback to stale cache on upstream connection hiccups.
  - Health check endpoint at `/api/health`.

---

## 🚀 Quick Start

```bash
python3 server.py
```
Open `http://localhost:8089` in your browser.

---

## 🐳 Docker

```bash
docker compose up -d
```
Accessible at `http://localhost:8089`.

---

## 📟 Raspberry Pi Kiosk Setup

Want to turn a Raspberry Pi and small display into a dedicated desk clock?
Check out the step-by-step [Raspberry Pi Kiosk Setup Guide](RASPBERRY_PI_KIOSK_GUIDE.md) for automated booting, cursor hiding, and display scheduling.

---

## 🧪 Testing

Run the automated test suite locally:

```bash
python3 -m unittest discover -s tests -v
```

---

## 🌐 Endpoints

- `GET /api/parks` - List of supported Universal parks and metadata.
- `GET /api/parks/<id>/waits` - Live wait times and summary stats.
- `GET /api/health` - Health check status.

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.
