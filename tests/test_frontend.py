"""
Tests for Universal Parks Wait Times frontend (index.html structure, DOM integrity, themes, and scripts).
"""

import html.parser
import os
import subprocess
import unittest


class DOMExtractor(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.element_ids = set()
        self.scripts = []
        self._current_tag = None
        self._script_buffer = []

    def handle_starttag(self, tag, attrs):
        self._current_tag = tag
        attr_dict = dict(attrs)
        if "id" in attr_dict:
            self.element_ids.add(attr_dict["id"])
        if tag == "script":
            self._script_buffer = []

    def handle_data(self, data):
        if self._current_tag == "script":
            self._script_buffer.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._script_buffer:
            self.scripts.append("".join(self._script_buffer))
            self._script_buffer = []
        self._current_tag = None


class TestUniversalFrontendIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "index.html"))
        with open(cls.html_path, "r", encoding="utf-8") as f:
            cls.html_content = f.read()

        cls.parser = DOMExtractor()
        cls.parser.feed(cls.html_content)

    def test_html_file_exists(self):
        self.assertTrue(os.path.exists(self.html_path))
        self.assertGreater(len(self.html_content), 1000)

    def test_essential_dom_elements_exist(self):
        required_ids = [
            "brandTitle",
            "brandSubtitle",
            "parkSelect",
            "modeBoxBtn",
            "modeBoardBtn",
            "settingsBtn",
            "fullscreenBtn",
            "parkClockBtn",
            "parkClockDisplay",
            "parkTimezoneLabel",
            "statOpenRides",
            "statTotalRides",
            "statAvgWait",
            "statMaxWait",
            "boxView",
            "boxProgressBar",
            "boxRideTitle",
            "boxWaitNumber",
            "boxWaitUnits",
            "boxWaitStatus",
            "boxFavBtn",
            "btnPrev",
            "btnNext",
            "btnPlayPause",
            "boardView",
            "boardGridContainer",
            "modeFireworksBtn",
            "fireworksView",
            "fireworksFeedSelect",
            "fireworksIframe",
            "fireworksReturnBtn",
            "settingsModal",
            "closeSettingsBtn",
            "settingTheme",
            "settingTimezone",
            "settingSpeed",
            "settingFilter",
        ]
        for element_id in required_ids:
            with self.subTest(element_id=element_id):
                self.assertIn(element_id, self.parser.element_ids, f"Missing required element #{element_id}")

    def test_night_shows_view_elements(self):
        """Verify night shows & live feeds view and presets exist."""
        self.assertIn("modeFireworksBtn", self.parser.element_ids)
        self.assertIn("fireworksIframe", self.parser.element_ids)
        self.assertIn("CineSational", self.html_content)
        self.assertIn("Hogwarts Always", self.html_content)
        self.assertIn("Super Nintendo World", self.html_content)

    def test_requested_themes_present(self):
        """Verify Harry Potter (Wizarding), Marvel (MCU), and Mario themes are present."""
        self.assertIn("theme-wizard", self.html_content)
        self.assertIn("theme-mcu", self.html_content)
        self.assertIn("theme-mario", self.html_content)
        self.assertIn("theme-classic", self.html_content)

    def test_timezone_default_cst(self):
        """Verify Central Time (America/Chicago) is configured."""
        self.assertIn('America/Chicago', self.html_content)
        self.assertIn('(CST)', self.html_content)
        self.assertRegex(self.html_content, r'<option\s+value="America/Chicago"\s+selected>')

    def test_javascript_syntax_valid(self):
        """Validate JavaScript syntax inside the HTML file using node --check."""
        self.assertGreater(len(self.parser.scripts), 0, "No script tag found in HTML")
        js_code = self.parser.scripts[0]
        try:
            res = subprocess.run(["node", "--check"], input=js_code, text=True, capture_output=True)
            self.assertEqual(res.returncode, 0, f"JavaScript syntax error: {res.stderr}")
        except FileNotFoundError:
            self.assertIn("function applyTheme", js_code)
            self.assertIn("function startParkClock", js_code)


if __name__ == "__main__":
    unittest.main()
