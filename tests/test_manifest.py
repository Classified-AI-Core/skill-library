import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "manifest.json"
SKILLS_ROOT = ROOT / "skills"
XQUIK_SKILL_PATH = SKILLS_ROOT / "research" / "xquik-x-research" / "SKILL.md"
ACTOR_URLS = (
    "https://apify.com/xquik/x-tweet-scraper",
    "https://apify.com/xquik/x-follower-scraper",
)
REST_IDS = ("xquik~x-tweet-scraper", "xquik~x-follower-scraper")
NOTICE = (
    "Xquik is an independent third-party service. Not affiliated with X Corp. "
    '"Twitter" and "X" are trademarks of X Corp.'
)


class ManifestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_declared_count_matches_manifest(self) -> None:
        self.assertEqual(self.manifest["count"], len(self.manifest["skills"]))

    def test_manifest_entries_are_unique_and_sorted(self) -> None:
        pairs = [
            (skill["category"], skill["name"]) for skill in self.manifest["skills"]
        ]

        self.assertEqual(pairs, sorted(pairs))
        self.assertEqual(len(pairs), len(set(pairs)))

    def test_manifest_matches_skill_directories(self) -> None:
        manifest_paths = {
            f"{skill['category']}/{skill['name']}" for skill in self.manifest["skills"]
        }
        filesystem_paths = {
            str(skill_dir.relative_to(SKILLS_ROOT))
            for skill_dir in SKILLS_ROOT.glob("*/*")
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").is_file()
        }

        self.assertSetEqual(manifest_paths, filesystem_paths)

    def test_xquik_manifest_entry(self) -> None:
        entry = next(
            skill
            for skill in self.manifest["skills"]
            if skill["name"] == "xquik-x-research"
        )

        self.assertEqual(entry["category"], "research")
        self.assertEqual(entry["author"], "Xquik")

    def test_xquik_skill_uses_both_actors_safely(self) -> None:
        content = XQUIK_SKILL_PATH.read_text(encoding="utf-8")

        for actor_url in ACTOR_URLS:
            with self.subTest(actor_url=actor_url):
                self.assertIn(actor_url, content)

        for rest_id in REST_IDS:
            with self.subTest(rest_id=rest_id):
                self.assertIn(rest_id, content)

        self.assertIn('"maxItems": 50', content)
        self.assertIn('"maxItemsPerTarget": 25', content)
        self.assertIn("| jq -r '.data.inputSchema'", content)
        self.assertIn("Authorization: Bearer ${APIFY_TOKEN}", content)
        self.assertNotIn("?token=", content)
        self.assertNotIn("xquik.com", content)
        self.assertIn(NOTICE, " ".join(content.split()))


if __name__ == "__main__":
    unittest.main()
