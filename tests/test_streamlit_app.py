"""Exercise the Streamlit widget tree without an external browser."""

from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def widget(elements, label):
    return next(element for element in elements if element.label == label)


def metric(app, label):
    return widget(app.metric, label).value


class StreamlitAppTests(unittest.TestCase):
    def launch(self):
        app = AppTest.from_file(str(APP), default_timeout=10).run()
        self.assertEqual(len(app.exception), 0)
        return app

    def test_initial_statistics(self):
        app = self.launch()
        self.assertEqual(metric(app, "Total songs"), "22")
        self.assertEqual(metric(app, "Hype songs"), "11")
        self.assertEqual(metric(app, "Chill songs"), "6")
        self.assertEqual(metric(app, "Mixed songs"), "5")
        self.assertEqual(metric(app, "Hype ratio"), "0.50")
        self.assertEqual(metric(app, "Average energy"), "5.73")

    def test_add_song_and_tags(self):
        app = self.launch()
        widget(app.text_input, "Title").set_value(" Quiet Rock ")
        widget(app.text_input, "Artist").set_value(" Test Artist ")
        widget(app.text_input, "Tags (comma separated)").set_value(" calm, , sleep ")
        widget(app.slider, "Energy").set_value(1)
        widget(app.button, "Add to playlist").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(metric(app, "Total songs"), "23")
        self.assertEqual(metric(app, "Chill songs"), "7")
        added = app.session_state["songs"][-1]
        self.assertEqual(added["title"], "Quiet Rock")
        self.assertEqual(added["artist"], "test artist")
        self.assertEqual(added["tags"], ["calm", "sleep"])

    def test_blank_names_are_rejected_with_feedback(self):
        for title, artist in [("   ", "Artist"), ("Track", ""), ("Track", "   ")]:
            with self.subTest(title=title, artist=artist):
                app = self.launch()
                widget(app.text_input, "Title").set_value(title)
                widget(app.text_input, "Artist").set_value(artist)
                widget(app.button, "Add to playlist").click().run()
                self.assertEqual(metric(app, "Total songs"), "22")
                self.assertTrue(any("title and an artist" in w.value for w in app.warning))
                self.assertEqual(len(app.exception), 0)

    def test_artist_search_and_no_match_feedback(self):
        app = self.launch()
        app.text_input(key="search_Hype").set_value("QUEEN").run()
        visible = " ".join(item.value for item in app.tabs[0].markdown)
        self.assertIn("Bohemian Rhapsody", visible)
        self.assertNotIn("Thunderstruck", visible)
        app.text_input(key="search_Hype").set_value("no-such-artist").run()
        self.assertIn("No matching songs.", [m.value for m in app.tabs[0].markdown])
        self.assertEqual(len(app.exception), 0)

    def test_favorite_genre_reclassifies_without_overriding_chill(self):
        app = self.launch()
        widget(app.selectbox, "Favorite genre").set_value("jazz").run()
        self.assertEqual(metric(app, "Hype songs"), "14")
        hype = " ".join(m.value for m in app.tabs[0].markdown)
        chill = " ".join(m.value for m in app.tabs[1].markdown)
        self.assertIn("Take Five", hype)
        self.assertNotIn("So What", hype)
        self.assertIn("So What", chill)

    def test_hype_threshold_slider(self):
        app = self.launch()
        widget(app.slider, "Hype min energy").set_value(10).run()
        self.assertEqual(metric(app, "Hype songs"), "6")
        self.assertEqual(metric(app, "Total songs"), "22")
        self.assertEqual(len(app.exception), 0)

    def test_hide_mixed_changes_views_only(self):
        app = self.launch()
        widget(app.checkbox, "Include Mixed playlist in views").uncheck().run()
        self.assertEqual([tab.label for tab in app.tabs], ["Hype", "Chill"])
        self.assertEqual(metric(app, "Mixed songs"), "5")
        self.assertEqual(metric(app, "Total songs"), "22")

    def test_lucky_pick_history_and_clear(self):
        app = self.launch()
        widget(app.selectbox, "Pick from").set_value("hype").run()
        widget(app.button, "Feeling lucky").click().run()
        self.assertEqual(len(app.success), 1)
        self.assertEqual(len(app.session_state["history"]), 1)
        self.assertEqual(app.session_state["history"][0]["mood"], "Hype")
        widget(app.checkbox, "Show full history").check().run()
        widget(app.button, "Clear history").click().run()
        self.assertEqual(app.session_state["history"], [])
        self.assertEqual(len(app.exception), 0)

    def test_empty_collection_lucky_pick(self):
        app = self.launch()
        app.session_state["songs"] = []
        app.run()
        widget(app.button, "Feeling lucky").click().run()
        self.assertEqual(metric(app, "Total songs"), "0")
        self.assertTrue(any("No songs available" in w.value for w in app.warning))
        self.assertEqual(len(app.exception), 0)

    def test_reset_restores_default_collection(self):
        app = self.launch()
        widget(app.text_input, "Title").set_value("New")
        widget(app.text_input, "Artist").set_value("Artist")
        widget(app.button, "Add to playlist").click().run()
        self.assertEqual(metric(app, "Total songs"), "23")
        widget(app.button, "Reset songs to default").click().run()
        self.assertEqual(metric(app, "Total songs"), "22")
        self.assertEqual(len(app.exception), 0)


if __name__ == "__main__":
    unittest.main()
