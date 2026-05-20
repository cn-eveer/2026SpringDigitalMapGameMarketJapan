#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game Market 2026 Spring scraper — separated outputs

This scraper writes separated files:
- Booth-only JSON / CSV
- Games-only JSON / CSV
- Optional nested JSON / Markdown

It extracts:
- Booth-only data from /booth/{id}
  - seq
  - booth_name
  - booth_number
  - booth_type
  - booth_url
  - booth_id
  - booth_status
  - booth_overview
  - game_list_url
  - game_list_status
  - games_count

- Games-only data from the same booth page's 新着ゲーム section and /booth/game/{id}
  - booth_seq
  - booth_name
  - booth_number
  - booth_type
  - booth_url
  - booth_id
  - game_index_in_booth
  - game_title
  - game_description
  - game_price
  - game_player
  - game_play_time
  - game_target_age
  - game_tags
  - game_publisher
  - game_url
  - game_source_section

Usage:
  python scrape_gamemarket.py \
    --input gamemarket_2026s_all_1318_booths_.csv \
    --start 1 \
    --limit 100 \
    --out-prefix gm2026s_batch_001 \
    --print-extracted

Continue:
  python scrape_gamemarket_separated.py \
    --input gamemarket_2026s_all_1318_booths_.csv \
    --start 101 \
    --limit 100 \
    --out-prefix gm2026s_batch_101 \
    --print-extracted

All:
  python scrape_gamemarket_separated.py \
    --input gamemarket_2026s_all_1318_booths_.csv \
    --start 1 \
    --limit 0 \
    --out-prefix gm2026s_all \
    --print-extracted

Single URL:
  python scrape_gamemarket_separated.py \
    --url https://gamemarket.jp/booth/2702 \
    --out-prefix test_2702 \
    --print-extracted
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://gamemarket.jp"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en;q=0.8",
}


@dataclass
class GameItem:
    title: str = ""
    description: str = ""
    price: str = ""
    player: str = ""
    play_time: str = ""
    target_age: str = ""
    tags: str = ""
    publisher: str = ""
    game_url: str = ""
    source_section: str = ""


@dataclass
class BoothItem:
    seq: int = 1
    booth_name: str = ""
    booth_number: str = ""
    booth_type: str = ""
    booth_url: str = ""
    booth_id: str = ""
    booth_status: str = ""
    booth_overview: str = ""
    game_list_url: str = ""
    game_list_status: str = ""
    games: list[GameItem] = field(default_factory=list)


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\xa0", " ").replace("\u3000", " ")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def one_line(text: str) -> str:
    return clean_text(text).replace("\n", " ").strip()


def absolute_url(href: str) -> str:
    return urljoin(BASE_URL, href or "")


def booth_id_from_url(url: str) -> str:
    m = re.search(r"/booth/(\d+)", url or "")
    return m.group(1) if m else ""


def fetch(url: str, sleep: float = 0.5, retries: int = 2) -> tuple[Optional[str], str]:
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code == 200 and r.text.strip():
                time.sleep(sleep)
                return r.text, "ok"
            status = f"http_{r.status_code}"
        except Exception as e:
            status = f"error:{type(e).__name__}:{e}"

        if attempt < retries:
            time.sleep(sleep * (attempt + 1))

    return None, status


def load_booths_from_csv(path: Path) -> list[BoothItem]:
    booths: list[BoothItem] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            url = row.get("booth_url") or row.get("url") or row.get("Booth URL") or ""
            if not url:
                continue

            url = absolute_url(url)
            booths.append(
                BoothItem(
                    seq=int(row.get("seq") or row.get("global_seq") or i),
                    booth_name=one_line(row.get("booth_name") or row.get("name") or ""),
                    booth_number=one_line(
                        row.get("booth_number") or row.get("booth_num") or ""
                    ),
                    booth_type=one_line(row.get("booth_type") or row.get("type") or ""),
                    booth_url=url,
                    booth_id=booth_id_from_url(url),
                )
            )

    return booths


def load_booths_from_html(path: Path) -> list[BoothItem]:
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")
    booths: list[BoothItem] = []

    for idx, li in enumerate(
        soup.select("ul.archiveList > li.itemList-child"), start=1
    ):
        a = li.select_one("a[href*='/booth/']")
        if not a:
            continue

        href = a.get("href", "")
        if not re.search(r"/booth/\d+", href):
            continue

        url = absolute_url(href)
        booths.append(
            BoothItem(
                seq=idx,
                booth_name=one_line(a.get("title", "")),
                booth_number=(
                    one_line(li.select_one("dd.booth-num").get_text(" ", strip=True))
                    if li.select_one("dd.booth-num")
                    else ""
                ),
                booth_type=(
                    one_line(li.select_one("dd.booth-type").get_text(" ", strip=True))
                    if li.select_one("dd.booth-type")
                    else ""
                ),
                booth_url=url,
                booth_id=booth_id_from_url(url),
            )
        )

    return booths


def load_booths(path: Path) -> list[BoothItem]:
    if path.suffix.lower() == ".csv":
        return load_booths_from_csv(path)
    return load_booths_from_html(path)


def extract_booth_name(soup: BeautifulSoup) -> str:
    h = soup.select_one("#boothDetail h3.titleLv3")
    if h:
        # Remove Twitter/X link so booth_name does not become "シエラゲームズ @..."
        h_copy = BeautifulSoup(str(h), "lxml")
        for a in h_copy.select("a"):
            a.decompose()
        return one_line(h_copy.get_text(" ", strip=True))

    og = soup.select_one("meta[property='og:title']")
    if og and og.get("content"):
        return one_line(og["content"].split("|")[0])

    return ""


def extract_booth_overview(soup: BeautifulSoup) -> str:
    about = soup.select_one("#boothAbout")
    if not about:
        return ""

    text = clean_text(about.get_text("\n", strip=True))
    return re.sub(r"^ブース概要\s*", "", text).strip()


def text_or_blank(parent: Tag, selector: str) -> str:
    el = parent.select_one(selector)
    return one_line(el.get_text(" ", strip=True)) if el else ""


def parse_game_card(card: Tag, source_section: str) -> Optional[GameItem]:
    title = text_or_blank(card, "dl.game dt.title")
    if not title:
        return None

    a = card.select_one("a[href*='/game/']")
    ux_tags = [
        one_line(li.get_text(" ", strip=True)) for li in card.select("ul.uxTag li")
    ]
    ux_tags = [t for t in ux_tags if t]

    return GameItem(
        title=title,
        description=text_or_blank(card, "dl.game dd.about"),
        price=text_or_blank(card, "dl.game dd.price"),
        player=text_or_blank(card, "ul.fliterTag li.num span.icon"),
        play_time=text_or_blank(card, "ul.fliterTag li.time span.icon"),
        target_age=text_or_blank(card, "ul.fliterTag li.age span.icon"),
        tags=", ".join(ux_tags),
        publisher=text_or_blank(card, "a.optionLink"),
        game_url=absolute_url(a.get("href")) if a and a.get("href") else "",
        source_section=source_section,
    )


def extract_games_from_section(section: Tag, source_section: str) -> list[GameItem]:
    games: list[GameItem] = []
    seen: set[str] = set()

    for card in section.select("ul.archiveList > li.itemList-child"):
        game = parse_game_card(card, source_section=source_section)
        if not game:
            continue

        key = game.game_url or game.title
        if key not in seen:
            games.append(game)
            seen.add(key)

    return games


def extract_new_games_from_booth_page(soup: BeautifulSoup) -> list[GameItem]:
    section = soup.select_one("section#gameList")
    if not section:
        return []

    return extract_games_from_section(section, "新着ゲーム")


def find_game_list_url(soup: BeautifulSoup, booth_id: str) -> str:
    a = soup.select_one("section#gameList header a[href*='/booth/game/']")
    if a and a.get("href"):
        return absolute_url(a["href"])

    a = soup.select_one("a[href*='/booth/game/']")
    if a and a.get("href"):
        return absolute_url(a["href"])

    return f"{BASE_URL}/booth/game/{booth_id}" if booth_id else ""


def extract_game_list_page_games(html: str) -> list[GameItem]:
    soup = BeautifulSoup(html, "lxml")
    return extract_games_from_section(soup, "ゲーム一覧")


def merge_games(
    new_games: list[GameItem], list_games: list[GameItem]
) -> list[GameItem]:
    merged: list[GameItem] = []
    seen: set[str] = set()

    # Prefer new-games information when duplicated.
    for g in new_games + list_games:
        key = g.game_url or g.title
        if key and key not in seen:
            merged.append(g)
            seen.add(key)

    return merged


def scrape_one_booth(booth: BoothItem, sleep: float = 0.5) -> BoothItem:
    html, status = fetch(booth.booth_url, sleep=sleep)
    booth.booth_status = status

    if not html:
        booth.game_list_status = "skipped_no_booth_html"
        return booth

    soup = BeautifulSoup(html, "lxml")

    booth.booth_name = extract_booth_name(soup) or booth.booth_name
    booth.booth_overview = extract_booth_overview(soup)

    # Important: games are often on the same booth page under section#gameList / 新着ゲーム.
    new_games = extract_new_games_from_booth_page(soup)

    booth.game_list_url = find_game_list_url(soup, booth.booth_id)
    list_games: list[GameItem] = []

    if booth.game_list_url:
        g_html, g_status = fetch(booth.game_list_url, sleep=sleep)
        booth.game_list_status = g_status
        if g_html:
            list_games = extract_game_list_page_games(g_html)
    else:
        booth.game_list_status = "not_found"

    booth.games = merge_games(new_games, list_games)
    return booth


def booth_only_row(b: BoothItem) -> dict:
    return {
        "seq": b.seq,
        "booth_name": b.booth_name,
        "booth_number": b.booth_number,
        "booth_type": b.booth_type,
        "booth_url": b.booth_url,
        "booth_id": b.booth_id,
        "booth_status": b.booth_status,
        "booth_overview": b.booth_overview,
        "game_list_url": b.game_list_url,
        "game_list_status": b.game_list_status,
        "games_count": len(b.games),
    }


def game_only_rows(b: BoothItem) -> list[dict]:
    rows = []
    for idx, g in enumerate(b.games, start=1):
        rows.append(
            {
                "booth_seq": b.seq,
                "booth_name": b.booth_name,
                "booth_number": b.booth_number,
                "booth_type": b.booth_type,
                "booth_url": b.booth_url,
                "booth_id": b.booth_id,
                "game_index_in_booth": idx,
                "game_title": g.title,
                "game_description": g.description,
                "game_price": g.price,
                "game_player": g.player,
                "game_play_time": g.play_time,
                "game_target_age": g.target_age,
                "game_tags": g.tags,
                "game_publisher": g.publisher,
                "game_url": g.game_url,
                "game_source_section": g.source_section,
            }
        )

    return rows


def write_json(path: Path, data: list[dict]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, data: list[dict]) -> None:
    if not data:
        path.write_text("", encoding="utf-8-sig")
        return

    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)


def write_nested_json(path: Path, booths: list[BoothItem]) -> None:
    path.write_text(
        json.dumps([asdict(b) for b in booths], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_markdown(path: Path, booths: list[BoothItem]) -> None:
    lines = ["# Game Market 2026 Spring Booth Extraction", ""]

    for b in booths:
        lines.append(f"- Booth: {b.booth_name or '未取得'}")
        lines.append(f"  - Booth No.: {b.booth_number or '未取得'}")
        lines.append(f"  - Booth Type: {b.booth_type or '未取得'}")
        lines.append(f"  - Booth URL: {b.booth_url}")
        lines.append("  - Booth Overview: |")

        if b.booth_overview:
            for line in b.booth_overview.splitlines():
                lines.append(f"      {line}")
        else:
            lines.append("      未取得")

        lines.append(f"  - Games Found: {len(b.games)}")
        lines.append("  - Games:")

        if not b.games:
            lines.append("    - Game: 未取得")
        else:
            for g in b.games:
                lines.append(f"    - Game: {g.title or '未取得'}")
                lines.append(f"      - Title: {g.title or '未取得'}")
                lines.append(f"      - Description: {g.description or '未取得'}")
                lines.append(f"      - Price: {g.price or '未取得'}")
                lines.append(f"      - Player: {g.player or '未取得'}")
                lines.append(f"      - Play Time: {g.play_time or '未取得'}")
                lines.append(f"      - Target Age: {g.target_age or '未取得'}")
                lines.append(f"      - Tags: {g.tags or '未取得'}")
                lines.append(f"      - Publisher: {g.publisher or '未取得'}")
                lines.append(f"      - Source: {g.game_url or '未取得'}")

        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def print_booth(b: BoothItem) -> None:
    print("=" * 80)
    print(f"Booth: {b.booth_name or '未取得'}")
    print(f"Booth No.: {b.booth_number or '未取得'}")
    print(f"Booth URL: {b.booth_url}")
    print(f"Booth Status: {b.booth_status}")
    print("Booth Overview:")
    print(b.booth_overview or "未取得")
    print(f"Game List URL: {b.game_list_url or '未取得'}")
    print(f"Game List Status: {b.game_list_status or '未取得'}")
    print(f"Games Found: {len(b.games)}")

    if not b.games:
        print("  - Game: 未取得")

    for g in b.games:
        print(f"  - Title: {g.title or '未取得'}")
        print(f"    Description: {g.description or '未取得'}")
        print(f"    Price: {g.price or '未取得'}")
        print(f"    Player: {g.player or '未取得'}")
        print(f"    Play Time: {g.play_time or '未取得'}")
        print(f"    Target Age: {g.target_age or '未取得'}")
        print(f"    Tags: {g.tags or '未取得'}")
        print(f"    Publisher: {g.publisher or '未取得'}")
        print(f"    Source Section: {g.source_section or '未取得'}")
        print(f"    Source: {g.game_url or '未取得'}")

    print("=" * 80)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Booth list CSV/HTML")
    parser.add_argument("--url", help="Specific booth URL")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--limit", type=int, default=0, help="0 = all remaining")
    parser.add_argument("--sleep", type=float, default=0.5)
    parser.add_argument("--out-prefix", default="gm2026s")
    parser.add_argument("--print-extracted", action="store_true")
    parser.add_argument(
        "--write-nested", action="store_true", help="Also write nested booth+games JSON"
    )
    parser.add_argument(
        "--write-markdown",
        action="store_true",
        help="Also write Obsidian-friendly Markdown",
    )
    args = parser.parse_args()

    if args.url:
        booths = [
            BoothItem(seq=1, booth_url=args.url, booth_id=booth_id_from_url(args.url))
        ]
    elif args.input:
        all_booths = load_booths(Path(args.input))
        start = max(args.start - 1, 0)
        booths = (
            all_booths[start:]
            if args.limit == 0
            else all_booths[start : start + args.limit]
        )
    else:
        raise SystemExit("Provide either --url or --input")

    scraped: list[BoothItem] = []

    for i, b in enumerate(booths, start=1):
        print(f"[{i}/{len(booths)}] FETCH {b.booth_url}", file=sys.stderr)
        item = scrape_one_booth(b, sleep=args.sleep)
        scraped.append(item)

        if args.print_extracted:
            print_booth(item)

    booth_rows = [booth_only_row(b) for b in scraped]
    games_rows = []
    for b in scraped:
        games_rows.extend(game_only_rows(b))

    prefix = Path(args.out_prefix)

    booth_json = Path(f"{prefix}_booths_only.json")
    games_json = Path(f"{prefix}_games_only.json")
    booth_csv = Path(f"{prefix}_booths_only.csv")
    games_csv = Path(f"{prefix}_games_only.csv")

    write_json(booth_json, booth_rows)
    write_json(games_json, games_rows)
    write_csv(booth_csv, booth_rows)
    write_csv(games_csv, games_rows)

    print(f"Wrote: {booth_json}")
    print(f"Wrote: {games_json}")
    print(f"Wrote: {booth_csv}")
    print(f"Wrote: {games_csv}")
    print(f"Booths: {len(booth_rows)}")
    print(f"Games: {len(games_rows)}")

    if args.write_nested:
        nested_path = Path(f"{prefix}_nested.json")
        write_nested_json(nested_path, scraped)
        print(f"Wrote: {nested_path}")

    if args.write_markdown:
        md_path = Path(f"{prefix}.md")
        write_markdown(md_path, scraped)
        print(f"Wrote: {md_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
