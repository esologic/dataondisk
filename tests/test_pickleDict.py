import pickle
from os import remove
from unittest import TestCase

from code.external_tools.dataondisk.dataondisk import PickleDict


class TestPickleDict(TestCase):

    def setUp(self):
        self.path = "p.p"

    def test_create(self):

        path = self.path

        test_pd = PickleDict(path)

        test_pd[5] = "five"

        with open(path, "rb") as file:
            p = pickle.load(file)

        self.assertEqual(test_pd[5], p[5])

    def tearDown(self):
        remove(self.path)


