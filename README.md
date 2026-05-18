# Game Market Booth Navigator

Interactive offline-first booth navigation map for Game Market.

Designed for:

* **iPhone / iPad**
* **Android**
* **Desktop / PC**
* **GitHub Pages hosting**
* **Offline usage after first load**

---

## Features

### Interactive Booth Map

* Drag to move around the map
* Pinch to zoom (canvas only)
* Browser page zoom is disabled
* Booths are selectable

### Search

Search by:

* Booth number
  Example: `い39`
* Booth code
  Example: `C13`
* Special booth
  Example: `特設01`
* Booth name
  Example: `オインク`

### Booth Information

Shows:

* Booth name
* Booth location
* Circle page
* Game list

### Favorites

Users can:

* Add favorite booths
* Mark visited booths
* Mark "もう一回行く"
* Remove favorites

Favorites show:

* Booth name
* Booth location
* Visit status

Saved locally on device.

### User Profile

Default username:

`guest`

Stored locally using browser storage.

### Offline Support

After first access, users can reopen the page even without internet.

Works with:

* iPhone Safari
* Android Chrome
* Desktop browsers

---

# Mobile UI

On mobile:

* Booth information appears as **bottom panel**
* Favorites are collapsible

Optimized for:

* One-hand use
* Fullscreen map navigation

---

# Desktop UI

On desktop:

* Booth information appears on **top-left panel**
* Uses larger information layout

---

# Data Support

Supports:

## Area Booths

Example:

* エリア01
* エリア95

## Special Booths

Example:

* 特設01
* 特設12

## Day-based Booths

Supported formats:

* 土 → Saturday only
* 日 → Sunday only
* 両 → Both days

Current logic:

* Sunday-only booths are excluded
* Saturday + Both-day booths are shown

Example:

`土-い39 → い39`

---

# Hosting on GitHub Pages

## 1. Create repository

Example:

`gamemarket-map`

## 2. Upload files

Upload:

* `index.html`

## 3. Enable Pages

Go to:

`Settings → Pages`

Set:

* Source → Deploy from branch
* Branch → main

## 4. Open

Your URL:

`https://YOUR_USERNAME.github.io/gamemarket-map/`

---

# Offline Installation

## iPhone

Safari:

1. Open website
2. Share
3. Add to Home Screen

## Android

Chrome:

1. Open website
2. Menu
3. Install app

## Desktop

Chrome / Edge:

1. Open website
2. Install icon in address bar

---

# Storage

Uses:

`localStorage`

Saved data:

* Username
* Favorites
* Visited booths
* Visit-again list

No server required.

---

# Tech Stack

Built with:

* HTML
* CSS
* Vanilla JavaScript
* SVG

No frameworks.

No backend.

Fully static.

---

# Version

Current:

**v88**

---

# License

Personal / event usage.

Modify freely.

---
