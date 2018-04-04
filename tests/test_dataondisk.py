import os
import unittest

from code.external_tools.dataondisk.dataondisk import InMemoryDataOnDisk, TextFileDataOnDisk


class InMemoryDataOnDiskTester(unittest.TestCase):

    def setUp(self):

        self.dod = InMemoryDataOnDisk("tester")

        self.dod.set_data("office jobs", "mark", "sales")
        self.dod.set_data("office jobs", "kenneth", "sales")
        self.dod.set_data("office jobs", "jane", "marketing")
        self.dod.set_data("office jobs", "leroy", "storming")

    def test_get_data(self):

        self.assertEqual(self.dod.get_data("office jobs", "mark"), "sales")
        self.assertEqual(self.dod.get_data("office jobs", "jane"), "marketing")
        self.assertEqual(self.dod.get_data("office jobs", "leroy"), "storming")

        with self.assertRaises(KeyError):
            self.dod.get_data("salary", "mark")

        with self.assertRaises(KeyError):
            self.dod.get_data("office jobs", "ken")


class TextFileDataOnDiskTester(unittest.TestCase):

    def tearDown(self):
        os.remove(self.path + ".txt")

    def setUp(self):

        self.path = "TextFileTest"

        self.dod = TextFileDataOnDisk(self.path)

        self.dod.set_data("office jobs", "mark", "sales")
        self.dod.set_data("office jobs", "kenneth", "sales")
        self.dod.set_data("office jobs", "jane", "marketing")
        self.dod.set_data("office jobs", "leroy", "storming")

        self.dod.set_data("salary", "mark", "$3000")
        self.dod.set_data("salary", "kenneth", "$2000")
        self.dod.set_data("salary", "billy", "$50000")

    def test_get_data(self):
        self.assertEqual(self.dod.get_data("office jobs", "mark"), "sales")
        self.assertEqual(self.dod.get_data("office jobs", "jane"), "marketing")

        self.assertEqual(self.dod.get_data("salary", "mark"), "$3000")
        self.assertEqual(self.dod.get_data("salary", "kenneth"), "$2000")
        self.assertEqual(self.dod.get_data("salary", "billy") , "$50000")

        self.assertEqual(self.dod.get_data("office jobs", "mark"), "sales")
        self.assertEqual(self.dod.get_data("office jobs", "jane"), "marketing")

        self.assertEqual(self.dod.get_data("salary", "mark"), "$3000")
        self.assertEqual(self.dod.get_data("salary", "kenneth"), "$2000")
        self.assertEqual(self.dod.get_data("salary", "billy") , "$50000")

        with self.assertRaises(KeyError):
            self.dod.get_data("location", "mark")

        with self.assertRaises(KeyError):
            self.dod.get_data("office jobs", "ken")

    def test_bad_file(self):
        dod = TextFileDataOnDisk("bad_file")

        with self.assertRaises(KeyError):
            dod.get_data("entry0", "data5")

if __name__ == '__main__':
    unittest.main()
