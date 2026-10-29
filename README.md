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
- Blank or whitespace-only song titles/artists are rejected with a visible message.

## Run

Use Python 3.10 or newer from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

## Regression tests

Install the application requirements first. The unittest runner covers both logic regressions and Streamlit AppTest widget interactions:

```bash
python3 -m unittest discover -s tests -v
```

Verified result:

```text
Ran 25 tests
OK
```

The 15 logic regressions cover overlapping classification rules, threshold boundaries, normalization, collection statistics, list aliasing, empty selections, selection modes and search. Before the logic fixes, those cases reported six failures and two errors.

Ten additional Streamlit widget tests cover startup statistics, adding songs/tags, invalid names and feedback, artist search, genre and threshold controls, hiding Mixed views, lucky picks/history, empty collections and reset controls. The invalid-name cases exposed whitespace-only entries and silent rejection of empty fields; both behaviors are fixed.

Verified on Python 3.12 with Streamlit 1.66.1. Streamlit AppTest runs the application and interacts with its widgets without an external browser; browser visual layout is outside these checks.

## Organization

- app.py: Streamlit interface.
- playlist_logic.py: classification, collection statistics, merge, search and selection functions.
- tests/test_playlist_logic.py: 15 logic regression cases.
- tests/test_streamlit_app.py: 10 Streamlit widget cases.

The original starter's provenance remains available through this repository's GitHub fork lineage.
