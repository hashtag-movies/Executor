import unittest
from fastapi.testclient import TestClient
from executor.server import app
from executor.studio_ui import STUDIO_HTML


class TestStudioEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_studio_page_loads(self):
        """Tests that /studio and /github-studio return 200 with the Studio HTML."""
        response = self.client.get("/studio")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Hashtag GitHub Cloud Studio", response.text)
        self.assertIn("Project Explorer", response.text)
        self.assertIn("code-editor", response.text)

    def test_github_studio_alias_loads(self):
        """Tests that /github-studio alias route works properly."""
        response = self.client.get("/github-studio")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Hashtag GitHub Cloud Studio", response.text)

    def test_console_has_studio_link(self):
        """Tests that the console contains the link to Cloud Studio."""
        response = self.client.get("/console")
        self.assertEqual(response.status_code, 200)
        self.assertIn("/studio", response.text)
        self.assertIn("GitHub Cloud Studio", response.text)


if __name__ == "__main__":
    unittest.main()
