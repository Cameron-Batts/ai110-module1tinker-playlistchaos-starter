# Playlist Chaos

Cameron Batts

A Streamlit playlist explorer that groups songs into Chill, Hype and Mixed playlists, supports search and lucky picks, and summarizes the collection.

## Classification

Energy uses a 1–10 scale in the interface. With the default profile:

- Chill: energy at most 3, or a title containing lofi, ambient or sleep, ignoring case.
- Hype: energy at least 7, a favorite-genre match, or a hype genre keyword.
- Mixed: songs matching neither rule.

Chill is evaluated first when signals overlap. Profile sliders customize the energy thresholds.

## Fixes and behavior

- Low-energy and explicitly chill-titled songs keep their Chill classification when another signal suggests Hype.
- Chill title keywords match regardless of capitalization.
- Hype ratio uses the entire collection as its denominator.
- Average energy includes every playlist.
- Merging playlists creates independent list containers and leaves both inputs unchanged. Song dictionaries remain shared.
- Empty lucky-pick selections return None and use the interface's existing no-songs warning.
- The any pick mode includes Hype, Chill and Mixed songs.

## Run

Use Python 3.10 or newer from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

## Regression tests

The tests use Python's standard library:

```bash
python3 -m unittest discover -s tests -v
```

Verified result:

```text
Ran 15 tests
OK
```

Before the fixes, this same suite reported six failures and two errors. Coverage includes overlapping classification rules, threshold boundaries, normalization, collection statistics, list aliasing, empty selections, selection modes and search.

Verification covers the Python logic. The Streamlit interface still needs an interactive check after the update.

## Organization

- app.py: Streamlit interface.
- playlist_logic.py: classification, collection statistics, merge, search and selection functions.
- tests/test_playlist_logic.py: regression cases.

The original starter's provenance remains available through this repository's GitHub fork lineage.
