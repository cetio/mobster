#!/usr/bin/env python3
"""
mobster.py — an evil Python script scrabbled together to allow for
watching movies & more from the command line from torrents.

Dependencies:
  - requests
  - fzf (external CLI)
  - peerflix (external CLI)
  - chafa (optional, external CLI)

Usage:
  python3 mobster.py
"""
import os
import sys
import shutil
import subprocess
import tempfile
import threading
import urllib.parse
import time
import json

import requests

# -==- Config -==-
YTS_API = "https://yts.mx/api/v2"
TRACKERS = [
    "udp://tracker.openbittorrent.com:80/announce",
    "udp://tracker.opentrackr.org:1337/announce",
]
RETRY = 2
# %^^@#*((!#&*$()))

WATCHED_FILE = os.path.expanduser("~/.mobster_watched.json")

def has_watched(hashid):
    if not os.path.exists(WATCHED_FILE):
        return False
    try:
        watched = json.load(open(WATCHED_FILE))
    except Exception:
        return False
    return hashid in watched

def mark_watched(hashid):
    watched = {}
    if os.path.exists(WATCHED_FILE):
        try:
            watched = json.load(open(WATCHED_FILE))
        except Exception:
            pass
    watched[hashid] = True
    with open(WATCHED_FILE, 'w') as f:
        json.dump(watched, f)

# Check CLI dependencies
def check_tool(name):
    if not shutil.which(name):
        print(f"X Required tool '{name}' not found. Please install and retry.")
        sys.exit(1)

for tool in ("fzf", "peerflix"):
    check_tool(tool)
cover_enabled = bool(shutil.which("chafa"))
if not cover_enabled:
    print("! Optional cover tool 'chafa' not found—skipping cover art.")

# Retry HTTP GET
def retry_get(url, path):
    for attempt in range(1, RETRY + 1):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            with open(path, 'wb') as f:
                f.write(response.content)
            return True
        except Exception as e:
            print(f"Attempt {attempt}/{RETRY} failed for {url}: {e}")
            time.sleep(0.5)
    return False

# Prompt user with fzf
def prompt_fzf(options, prompt_text):
    proc = subprocess.Popen(
        ['fzf', '--ansi', '--prompt', prompt_text],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    input_str = '\n'.join(options)
    out, _ = proc.communicate(input_str)
    return out.strip()

def main():
    tmpdir = tempfile.mkdtemp(prefix='mobster_')
    print(f"Temporary directory: {tmpdir}")

    # 1) Get search query
    print("* Enter search term(s):")
    proc = subprocess.Popen(
        ['fzf', '--print-query', '--prompt', 'Search YTS: '],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    query, _ = proc.communicate('')
    query = query.splitlines()[0] if query else ''
    if not query:
        print("No query entered, exiting.")
        shutil.rmtree(tmpdir)
        return
    print(f"Searching for: {query}")

    # 2) Fetch search results
    search_path = os.path.join(tmpdir, 'search.json')
    search_url = f"{YTS_API}/list_movies.json?query_term={urllib.parse.quote(query)}"
    if not retry_get(search_url, search_path):
        print("X Failed to fetch search results.")
        shutil.rmtree(tmpdir)
        sys.exit(1)

    with open(search_path, 'r') as f:
        data = json.load(f)
    count = data.get('data', {}).get('movie_count', 0)
    print(f"Found {count} results")
    if count == 0:
        print(f"No movies found for '{query}'")
        shutil.rmtree(tmpdir)
        return

    # 3) Build unique movie list for main menu with watched mark
    # id works fine here but might not be best
    movies = data['data']['movies']
    options = []
    movie_map = {}
    for movie in movies:
        movie_id = movie.get('id')
        title = movie.get('title_long')
        # Determine watched status by checking if ANY torrent hash is watched
        # Quality of the torrent doesn't really matter, as it's the same title anyway.
        watched_any = any(has_watched(t['hash']) for t in movie.get('torrents', []))
        mark = "O" if watched_any else "X"
        options.append(f"{mark} {title}")
        movie_map[title] = movie  # map by title for easy access

    print(f"Preparing {len(options)} unique movie options...")

    # 4) User picks a movie title
    selection = prompt_fzf(options, 'Pick movie> ')
    if not selection:
        print("Selection canceled.")
        shutil.rmtree(tmpdir)
        return
    print(f"You selected: {selection}")

    # Remove watched mark prefix and leading space
    if selection.startswith(("O ", "X ")):
        selection = selection[2:].strip()

    if selection not in movie_map:
        print("Selected movie not found in data, exiting.")
        shutil.rmtree(tmpdir)
        return

    movie = movie_map[selection]

    # 5) Build quality submenu (list all torrents for that movie)
    quality_options = []
    for tor in movie.get('torrents', []):
        q = tor.get('quality')
        sz = tor.get('size')
        h = tor.get('hash')
        quality_options.append(f"{q} — {sz} — {h}")

    print(f"Preparing {len(quality_options)} quality options for '{selection}'...")

    # 6) User picks quality
    quality_selection = prompt_fzf(quality_options, 'Pick quality> ')
    if not quality_selection:
        print("Quality selection canceled.")
        shutil.rmtree(tmpdir)
        return
    print(f"You selected: {quality_selection}")

    quality, size, hashid = [p.strip() for p in quality_selection.split('—')]
    print(f"Parsed: Title='{selection}', Quality={quality}, Size={size}")

    # Mark as watched for the selected torrent hash
    mark_watched(hashid)

    # 7) Construct magnet link
    dn = urllib.parse.quote(selection)
    magnet = f"magnet:?xt=urn:btih:{hashid}&dn={dn}"
    for tr in TRACKERS:
        magnet += f"&tr={urllib.parse.quote(tr)}"
    print(f"Magnet URI: {magnet}")

    # 8) Fetch cover art in background
    def fetch_cover():
        movie_id = movie.get('id')
        if not movie_id:
            print("No matching movie ID, skipping cover art.")
            return
        details_path = os.path.join(tmpdir, 'details.json')
        details_url = f"{YTS_API}/movie_details.json?movie_id={movie_id}"
        if retry_get(details_url, details_path):
            det = json.load(open(details_path))
            img_url = det.get('data', {}).get('movie', {}).get('large_cover_image')
            if img_url:
                img_path = os.path.join(tmpdir, 'cover.jpg')
                if retry_get(img_url, img_path):
                    os.system('clear')
                    subprocess.run(['chafa', '--symbols', 'braille', img_path])
                    print(f"\n{selection} — {quality} — {size}\n")
    # TODO: Make it so covers aren't total shit
    if cover_enabled:
        threading.Thread(target=fetch_cover, daemon=True).start()

    # 9) Launch peerflix → mpv
    print("*  Launching stream via peerflix + mpv...")
    # This outputs the mpv prompt continually for some reason?
    os.execvp('peerflix', ['peerflix', magnet, '--mpv'])

if __name__ == '__main__':
    main()
