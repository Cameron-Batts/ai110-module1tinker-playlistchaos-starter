"""Regression coverage for playlist classification, statistics and safe selection."""

import copy
import unittest

from playlist_logic import (
    DEFAULT_PROFILE, build_playlists, classify_song, compute_playlist_stats,
    lucky_pick, merge_playlists, random_choice_or_none, search_songs,
)


def song(title="Track", genre="jazz", energy=5):
    return {"title": title, "artist": "Artist", "genre": genre, "energy": energy}


class PlaylistLogicTests(unittest.TestCase):
    def test_low_energy_beats_favorite_genre(self):
        self.assertEqual(classify_song(song(genre="rock", energy=1), DEFAULT_PROFILE), "Chill")

    def test_chill_keyword_is_case_insensitive(self):
        self.assertEqual(classify_song(song(title="Lofi Rain"), DEFAULT_PROFILE), "Chill")

    def test_chill_keyword_beats_hype_energy(self):
        self.assertEqual(classify_song(song(title="AMBIENT Night", energy=9), DEFAULT_PROFILE), "Chill")

    def test_energy_boundaries_and_mixed(self):
        for energy, label in [(3, "Chill"), (4, "Mixed"), (6, "Mixed"), (7, "Hype")]:
            with self.subTest(energy=energy):
                self.assertEqual(classify_song(song(energy=energy), DEFAULT_PROFILE), label)

    def test_favorite_genre_works_above_chill_threshold(self):
        self.assertEqual(classify_song(song(genre="rock", energy=5), DEFAULT_PROFILE), "Hype")

    def test_build_normalizes_without_changing_input(self):
        raw = [song(title=" Track ", genre=" JAZZ ", energy="5")]
        original = copy.deepcopy(raw)
        result = build_playlists(raw, DEFAULT_PROFILE)
        self.assertEqual(raw, original)
        self.assertEqual(result["Mixed"][0]["genre"], "jazz")
        self.assertEqual(result["Mixed"][0]["energy"], 5)

    def test_stats_use_every_song(self):
        stats = compute_playlist_stats({"Hype": [song(energy=8)], "Chill": [song(energy=2)], "Mixed": [song(energy=5)]})
        self.assertEqual(stats["total_songs"], 3)
        self.assertAlmostEqual(stats["hype_ratio"], 1 / 3)
        self.assertEqual(stats["avg_energy"], 5)

    def test_empty_stats(self):
        stats = compute_playlist_stats({})
        self.assertEqual(stats["total_songs"], 0)
        self.assertEqual(stats["hype_ratio"], 0)
        self.assertEqual(stats["avg_energy"], 0)

    def test_stats_without_hype(self):
        stats = compute_playlist_stats({"Chill": [song(energy=2)]})
        self.assertEqual(stats["hype_ratio"], 0)
        self.assertEqual(stats["avg_energy"], 2)

    def test_merge_does_not_change_either_input(self):
        a, b = {"Hype": [song("A")]}, {"Hype": [song("B")], "Chill": []}
        originals = copy.deepcopy((a, b))
        merged = merge_playlists(a, b)
        self.assertEqual((a, b), originals)
        self.assertEqual([s["title"] for s in merged["Hype"]], ["A", "B"])
        merged["Hype"].clear()
        self.assertEqual((a, b), originals)

    def test_merge_copies_one_sided_lists(self):
        b = {"Mixed": [song()]}
        merged = merge_playlists({}, b)
        merged["Mixed"].clear()
        self.assertEqual(len(b["Mixed"]), 1)

    def test_empty_random_selection(self):
        self.assertIsNone(random_choice_or_none([]))
        self.assertIsNone(lucky_pick({}))
        self.assertIsNone(lucky_pick({"Mixed": [song()]}, mode="hype"))

    def test_any_pick_includes_mixed_songs(self):
        track = song()
        self.assertEqual(lucky_pick({"Mixed": [track]}, mode="any"), track)

    def test_specific_pick_respects_mode(self):
        hype, chill = song("Hype"), song("Chill")
        catalog = {"Hype": [hype], "Chill": [chill]}
        self.assertEqual(lucky_pick(catalog, "hype"), hype)
        self.assertEqual(lucky_pick(catalog, "chill"), chill)

    def test_search_remains_partial_and_case_insensitive(self):
        tracks = [song("A"), dict(song("B"), artist="Other")]
        self.assertEqual(search_songs(tracks, "ART"), tracks[:1])


if __name__ == "__main__":
    unittest.main()
