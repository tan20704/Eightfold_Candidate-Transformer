import unittest
from normalizers.phone import normalize_phone
from normalizers.date import normalize_date
from normalizers.location import normalize_location
from normalizers.skills import canonicalize_skill, normalize_skills

class TestNormalizers(unittest.TestCase):
    def test_phone_normalization(self):
        self.assertEqual(normalize_phone("+91 93346 21693"), "+919334621693")
        self.assertEqual(normalize_phone("ƒ +91 93346 21693"), "+919334621693")
        self.assertEqual(normalize_phone("9334621693"), "+919334621693")
        self.assertEqual(normalize_phone("12345"), "12345")  # fallback
        self.assertIsNone(normalize_phone(None))

    def test_date_normalization(self):
        self.assertEqual(normalize_date("May 2025"), "2025-05")
        self.assertEqual(normalize_date("Jul 2025"), "2025-07")
        self.assertEqual(normalize_date("Present"), "Present")
        self.assertEqual(normalize_date("2023-08"), "2023-08")
        self.assertIsNone(normalize_date(None))

    def test_location_normalization(self):
        loc1 = normalize_location("Chandigarh, India")
        self.assertEqual(loc1["city"], "Chandigarh")
        self.assertEqual(loc1["country"], "IN")
        
        loc2 = normalize_location("Chandigarh")
        self.assertEqual(loc2["city"], "Chandigarh")
        self.assertEqual(loc2["country"], "IN")
        
        loc3 = normalize_location({"city": "San Francisco", "country": "USA"})
        self.assertEqual(loc3["city"], "San Francisco")
        self.assertEqual(loc3["country"], "US")

    def test_skills_normalization(self):
        self.assertEqual(canonicalize_skill("c++ programming"), "C++")
        self.assertEqual(canonicalize_skill("mysql"), "MySQL")
        self.assertEqual(canonicalize_skill("machine learning"), "Machine Learning")
        self.assertEqual(canonicalize_skill("Fuzzy Logic"), "Fuzzy Logic")
        
        norm_list = normalize_skills(["c++ programming", "C++", "MySQL", "mysql"])
        self.assertEqual(norm_list, ["C++", "MySQL"])

if __name__ == "__main__":
    unittest.main()
