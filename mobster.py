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

# Check CLI dependencies
def check_tool(name):
    if not shutil.which(name):
        print(f"X Required tool '{name}' not found. Please install and retry.")
        sys.exit(1)

for tool in ("fzf", "peerflix"):
    check_tool(tool)
cover_enabled = bool(shutil.which("chafa"))
if not cover_enabled:
    print("!  Optional cover tool 'chafa' not found—skipping cover art.")

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

# cyclomatic complexity is too high :-)
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

    # 3) Build selection list
    options = []
    for movie in data['data']['movies']:
        title = movie.get('title_long')
        for tor in movie.get('torrents', []):
            q = tor.get('quality')
            sz = tor.get('size')
            h = tor.get('hash')
            options.append(f"{title} — {q} — {sz} — {h}")
    print(f"Preparing {len(options)} options...")

    # 4) User picks option
    selection = prompt_fzf(options, 'Pick> ')
    if not selection:
        print("Selection canceled.")
        shutil.rmtree(tmpdir)
        return
    print(f"You selected: {selection}")

    title, quality, size, hashid = [p.strip() for p in selection.split('—')]
    print(f"Parsed: Title='{title}', Quality={quality}, Size={size}")

    # 5) Construct magnet link
    dn = urllib.parse.quote(title)
    magnet = f"magnet:?xt=urn:btih:{hashid}&dn={dn}"
    for tr in TRACKERS:
        magnet += f"&tr={urllib.parse.quote(tr)}"
    print(f"Magnet URI: {magnet}")

    # 6) Fetch cover art in background
    def fetch_cover():
        for movie in data['data']['movies']:
            if any(t['hash'] == hashid for t in movie.get('torrents', [])):
                movie_id = movie.get('id')
                break
        else:
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
                    print(f"\n{title} — {quality} — {size}\n")

    if cover_enabled:
        threading.Thread(target=fetch_cover, daemon=True).start()

    # 7) Launch peerflix → mpv
    print("*  Launching stream via peerflix + mpv...")
    os.execvp('peerflix', ['peerflix', magnet, '--mpv'])

if __name__ == '__main__':
    main()
