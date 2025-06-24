# mobster.py

**An evil Python script scrabbled together to allow for watching movies & more from the commandline via torrents.**

## Features

- Search YTS movies using `fzf`
- Choose video quality from a list of torrent options
- Automatically streams via `peerflix` + `mpv`
- Renders cover art as ASCII directly in terminal using Chafa.
- Zero config. Just run and enjoy.

### **ARTIFICIAL INTELLIGENCE**

THIS SCRIPT IS SENTIENT, AND ENTIRELY ARTIFICIALLY INTELLIGENT.
DO NOT RUN IT AS SUDO OR IT WILL AGENTICALLY RUN `rm -rf /**`

## Requirements

Despite being a Python script, Mobster doesn't actually use much of any dependencies from Python, you simply need:

- Python 3
- `python-requests`
- `fzf` (CLI)
- `mpv` (VLC may end up gaining support)
- `peerflix` (CLI)
- Optionally: `chafa` (if you'd like external cover rendering)

## Usage

If you're a dork, you can use the following:

```bash
python3 mobster.py
```

Otherwise:

```bash
./mobster.py
```

Just type your movie name and hit enter. Mobster will do the rest.

## Notes

- Simply functions, no weird shenanigans but no guarantees for content.
- Doesn’t keep any cache or logs.
- Fun for the whole family, except Rodger.
- Works best in a decent-width terminal (80+ columns recommended).
 - chafa may require more space or render strangely based on your sizing.

## Screenshot

```
Temporary directory: /tmp/mobster_abc123
* Enter search term(s):
Searching for: Shin Godzilla
Found 3 results
Preparing 6 options...
You selected: Shin Godzilla (2016) — 1080p — 1.82 GB — [HASH]
Parsed: Title='Shin Godzilla (2016)', Quality=1080p, Size=1.82 GB
Magnet URI: magnet:?xt=urn:btih:...
Fetching cover art...
[ASCII Art Here]
* Launching stream via peerflix + mpv...
```

## License

Mobster is licensed under the [AGPL-3.0 License](LICENSE.txt) but for legal reasons this is an educational tool.
By using Mobster you forgo all human rights and implicitly agree that, in the event a federal or local authority were to question you, you are to be hanged in the gallows.
