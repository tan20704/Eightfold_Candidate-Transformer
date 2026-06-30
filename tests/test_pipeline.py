import unittest
from merger.merge import MergeEngine
from utils.projection import project_profile


class TestPipeline(unittest.TestCase):

    def setUp(self):
        self.merge_engine = MergeEngine()

    def test_candidate_grouping(self):

        c1 = {
            "candidate_id": "C1",
            "full_name": "John Doe",
            "emails": ["john@example.com"],
            "phones": ["+919999999999"],
            "location": "Delhi",
            "skills": ["C++"],
            "_meta": {
                "source": "source1.csv",
                "method": "csv_row_import"
            }
        }

        c2 = {
            "candidate_id": None,
            "full_name": "John D.",
            "emails": ["john@example.com"],
            "phones": [],
            "location": None,
            "skills": ["Python"],
            "_meta": {
                "source": "source2.pdf",
                "method": "resume_pdf_extraction"
            }
        }

        merged = self.merge_engine.merge_candidates([c1, c2])

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0].full_name, "John Doe")
        self.assertEqual(merged[0].emails, ["john@example.com"])
        self.assertEqual(
            set(s.name for s in merged[0].skills),
            {"C++", "Python"}
        )

    def test_conflict_resolution_and_confidence(self):

        c1 = {
            "candidate_id": "C1",
            "full_name": "John Doe",
            "emails": ["john@example.com"],
            "headline": "Software Intern",
            "_meta": {
                "source": "source1.csv",
                "method": "csv_row_import"
            }
        }

        c2 = {
            "candidate_id": "C1",
            "full_name": "John Doe",
            "emails": ["john@example.com"],
            "headline": "C++ Specialist",
            "_meta": {
                "source": "source2.pdf",
                "method": "resume_pdf_extraction"
            }
        }

        merged = self.merge_engine.merge_candidates([c1, c2])

        self.assertEqual(
            merged[0].headline,
            "Software Intern"
        )

    def test_custom_projection(self):

        c = {
            "candidate_id": "C1",
            "full_name": "John Doe",
            "emails": ["john@example.com"],
            "phones": ["+919999999999"],
            "location": "Delhi",
            "skills": ["C++", "Python"],
            "_meta": {
                "source": "source1.csv",
                "method": "csv_row_import"
            }
        }

        profile = self.merge_engine.merge_candidates([c])[0]

        config = {
            "fields": {
                "id": "candidate_id",
                "name": "full_name",
                "skills_list": {
                    "from": "skills",
                    "format": "names_only"
                }
            },
            "include_provenance": True,
            "include_confidence": False,
            "missing_value_strategy": "null"
        }

        projected = project_profile(profile, config)

        self.assertIn("id", projected)
        self.assertIn("name", projected)
        self.assertIn("skills_list", projected)
        self.assertNotIn("overall_confidence", projected)

        self.assertEqual(projected["id"], "C1")
        self.assertEqual(
            projected["skills_list"],
            ["C++", "Python"]
        )

        for prov in projected.get("provenance", []):

            self.assertIn(
                prov["field"],
                [
                    "id",
                    "name",
                    "skills_list.C++",
                    "skills_list.Python"
                ]
            )

    def test_projection_missing_error(self):

        c = {
            "candidate_id": "C1",
            "full_name": "John Doe",
            "emails": [],
            "_meta": {
                "source": "source1.csv",
                "method": "csv_row_import"
            }
        }

        profile = self.merge_engine.merge_candidates([c])[0]

        config = {
            "fields": {
                "email_contact": "emails"
            },
            "missing_value_strategy": "error"
        }

        with self.assertRaises(ValueError):
            project_profile(profile, config)

        config["missing_value_strategy"] = "omit"

        projected = project_profile(profile, config)

        self.assertNotIn("email_contact", projected)


if __name__ == "__main__":
    unittest.main()