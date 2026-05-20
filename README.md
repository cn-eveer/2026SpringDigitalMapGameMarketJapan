# ゲムマ2026春 デジタルマップ

Split file structure:

```text
index.html
css/
  styles.css
js/
  data.js
  app.js
```

- `index.html` stays at the project root.
- `css/styles.css` contains the extracted styles.
- `js/data.js` contains map/data arrays and constants.
- `js/app.js` contains the app behavior.

Open `index.html` in a browser, or serve this folder with a local static server.


## Memo feature

Each selected booth now has a free-text memo field in the information panel. Memos are automatically saved in `localStorage` per user name and booth ID.


## Memo-first booth information panel

- The booth information panel title now shows the booth number and booth name together.
- The memo field appears directly under the title and is saved automatically per booth and user.
- Favorite / visited / revisit buttons appear directly under the memo field.
- Booth detail metadata no longer repeats the booth number before the booth URL.
- The user-specific favorite heading text was removed from the information panel.


## Latest UI changes

- Info panel title now shows only `[ブース場所] [ブース名]`.
- Close control is a compact `×` button aligned to the title row.
- `ブースURL` and `ゲーム一覧` are always visible directly under the title.
- Memo appears below the booth links and keeps autosaving per booth.
- Action buttons are equal-width: `お気に入り`, `行った`, `もう一度`.


## v91 info panel tabs

- Added tabs inside the booth information panel: `メモ`, `概要`, `ゲーム一覧`.
- `概要` is populated from `gamemarket_2026s_booths_only(1).csv`.
- `ゲーム一覧` is populated from `gamemarket_2026s_games_only(1).csv`.
- Memo text remains saved per booth and per user in localStorage.

## Latest update

- `概要` is now shown directly below the booth title/link area with a fixed-height scroll box.
- The info panel tabs are now `メモ`, `ゲーム一覧`, and `気になるリスト`.
- Games can be marked as `気になる` from the game list.
- Marking any game as `気になる` automatically adds that booth to `お気に入り`.


## Latest info-panel changes

- Removed the `気になるリスト` tab inside the booth info panel.
- Added `ブース概要` before the overview text.
- Updated link labels:
  - `最新のブース情報をチェック`
  - `最新のゲーム一覧をチェック`
- Game `気になる` buttons remain in `ゲーム一覧` and still automatically add the booth to favorites.


## Latest layout update

- The info panel itself no longer scrolls vertically.
- `ブース概要` stays visible below the title and links.
- Only the active tab content scrolls when there is too much content.

## Latest overview sizing update

- Reduced the maximum height of `ブース概要`.
- Long overview text now scrolls inside the `ブース概要` area instead of expanding the info panel.
- The info panel itself remains non-scrolling vertically.


## v96

- ブース概要の本文エリアを3行分表示する高さに調整しました。
- 3行を超える概要は、ブース概要内だけで縦スクロールします。
- 情報パネル本体は引き続き縦スクロールしません。
