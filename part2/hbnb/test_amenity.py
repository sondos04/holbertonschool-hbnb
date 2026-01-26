#!/usr/bin/env python3
import unittest

from app.models.amenity import Amenity


class TestAmenity(unittest.TestCase):
    def test_create_valid_amenity(self):
        a = Amenity(name="WiFi")
        self.assertEqual(a.name, "WiFi")

    def test_empty_name_should_fail(self):
        with self.assertRaises(Exception):
            Amenity(name="")
        with self.assertRaises(Exception):
            Amenity(name="   ")


if __name__ == "__main__":
    unittest.main(verbosity=2)
